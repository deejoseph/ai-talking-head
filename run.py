import os
import shutil
import subprocess
import sys
from tts.generate_audio import generate_audio

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "inputs")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
SAD_OUTPUT_DIR = os.path.join(OUTPUT_DIR, "sadtalker_runs")

INPUT_AUDIO = os.path.join(INPUT_DIR, "audio.wav")
TTS_AUDIO = os.path.join(INPUT_DIR, "tts_audio.wav")
IMAGE_PATH = os.path.join(INPUT_DIR, "image.png")

SADTALKER_PATH = os.path.join(BASE_DIR, "sadtalker")
WAV2LIP_PATH = os.path.join(BASE_DIR, "Wav2Lip")
FINAL_VIDEO = os.path.join(OUTPUT_DIR, "output.mp4")

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(SAD_OUTPUT_DIR, exist_ok=True)


def _get_env_int(key: str, default: int) -> int:
    try:
        return int(os.environ.get(key, str(default)))
    except (TypeError, ValueError):
        return default


def _get_env_float(key: str, default: float) -> float:
    try:
        return float(os.environ.get(key, str(default)))
    except (TypeError, ValueError):
        return default


def _get_env_bool(key: str, default: bool) -> bool:
    val = os.environ.get(key, "1" if default else "0").strip().lower()
    return val in {"1", "true", "yes", "on"}


def _run_and_stream(cmd, cwd):
    def _safe_stdout_write(text: str) -> None:
        try:
            sys.stdout.write(text)
            return
        except UnicodeEncodeError:
            pass

        out_enc = sys.stdout.encoding or "utf-8"
        safe_bytes = text.encode(out_enc, errors="replace")
        if hasattr(sys.stdout, "buffer"):
            sys.stdout.buffer.write(safe_bytes)
            sys.stdout.flush()
        else:
            sys.stdout.write(safe_bytes.decode(out_enc, errors="replace"))

    print(f"[RUN] {' '.join(cmd)}")
    proc = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert proc.stdout is not None
    for line in proc.stdout:
        _safe_stdout_write(line)
    return proc.wait()


def _latest_mp4(folder: str):
    videos = [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.lower().endswith(".mp4")
    ]
    if not videos:
        return None
    return max(videos, key=os.path.getmtime)


def _first_existing(paths):
    for p in paths:
        if os.path.exists(p):
            return p
    return None


PADS = os.environ.get("PADS", "0 20 0 0")
RESIZE = _get_env_int("RESIZE", 1)
FACE_BS = _get_env_int("FACE_BS", 8)
WAV_BS = _get_env_int("WAV_BS", 16)

POSE_STYLE = _get_env_int("POSE_STYLE", 0)
EXPRESSION_SCALE = _get_env_float("EXPRESSION_SCALE", 1.0)
FIX_HEAD = _get_env_bool("FIX_HEAD", True)
PREPROCESS = os.environ.get("PREPROCESS", "full")
SMOOTH_FACE = _get_env_bool("SMOOTH_FACE", True)
RUN_WAV2LIP = _get_env_bool("RUN_WAV2LIP", True)
USE_ENHANCER = _get_env_bool("USE_ENHANCER", True)

print("========== UI PARAMS ==========")
print("PADS:", PADS)
print("RESIZE:", RESIZE)
print("FACE_BS:", FACE_BS)
print("WAV_BS:", WAV_BS)
print("POSE_STYLE:", POSE_STYLE)
print("EXPRESSION_SCALE:", EXPRESSION_SCALE)
print("FIX_HEAD:", FIX_HEAD)
print("PREPROCESS:", PREPROCESS)
print("SMOOTH_FACE:", SMOOTH_FACE)
print("RUN_WAV2LIP:", RUN_WAV2LIP)
print("USE_ENHANCER:", USE_ENHANCER)
print("================================")

text = None
if text:
    print("Using TTS...")
    AUDIO_PATH = TTS_AUDIO
    generate_audio(text, AUDIO_PATH)
else:
    print("Using input audio...")
    AUDIO_PATH = _first_existing(
        [
            os.path.join(INPUT_DIR, "audio.wav"),
            os.path.join(INPUT_DIR, "input_audio.wav"),
            os.path.join(INPUT_DIR, "tts_audio.wav"),
        ]
    )

IMAGE_PATH = _first_existing(
    [
        os.path.join(INPUT_DIR, "image.png"),
        os.path.join(INPUT_DIR, "face.png"),
        os.path.join(INPUT_DIR, "dee.png"),
        os.path.join(INPUT_DIR, "image.jpg"),
        os.path.join(INPUT_DIR, "face.jpg"),
        os.path.join(INPUT_DIR, "image.jpeg"),
        os.path.join(INPUT_DIR, "face.jpeg"),
    ]
)

if not AUDIO_PATH:
    raise FileNotFoundError(
        f"Audio not found in {INPUT_DIR}. Expected one of: audio.wav / input_audio.wav / tts_audio.wav"
    )
if not IMAGE_PATH:
    raise FileNotFoundError(
        f"Image not found in {INPUT_DIR}. Expected one of: image.png / face.png / dee.png / *.jpg / *.jpeg"
    )

print("Audio:", AUDIO_PATH)
print("Image:", IMAGE_PATH)

if os.path.exists(FINAL_VIDEO):
    os.remove(FINAL_VIDEO)

# keep pose_style at 0 in still mode for stability
sad_pose_style = 0 if FIX_HEAD else POSE_STYLE
sad_expression_scale = max(0.6, min(1.3, EXPRESSION_SCALE))

print("Running SadTalker...")
cmd_sad = [
    "python",
    "inference.py",
    "--driven_audio",
    AUDIO_PATH,
    "--source_image",
    IMAGE_PATH,
    "--result_dir",
    SAD_OUTPUT_DIR,
    "--preprocess",
    PREPROCESS,
    "--batch_size",
    "1",
    "--pose_style",
    str(sad_pose_style),
    "--expression_scale",
    str(sad_expression_scale),
]

if FIX_HEAD:
    cmd_sad.append("--still")
if USE_ENHANCER:
    cmd_sad.extend(["--enhancer", "gfpgan"])

sad_rc = _run_and_stream(cmd_sad, cwd=SADTALKER_PATH)
if sad_rc != 0:
    raise RuntimeError("SadTalker failed")

sad_video_path = _latest_mp4(SAD_OUTPUT_DIR)
if not sad_video_path:
    raise RuntimeError("No video generated by SadTalker")
print("SadTalker output:", sad_video_path)

if not RUN_WAV2LIP:
    shutil.copy2(sad_video_path, FINAL_VIDEO)
    print("Skip Wav2Lip. Final video:", FINAL_VIDEO)
    sys.exit(0)

print("Running Wav2Lip...")
checkpoint_path = os.path.join(WAV2LIP_PATH, "checkpoints", "wav2lip_gan.pth")
if not os.path.exists(checkpoint_path):
    raise FileNotFoundError(f"Wav2Lip checkpoint not found: {checkpoint_path}")

cmd_wav = [
    "python",
    "inference.py",
    "--checkpoint_path",
    checkpoint_path,
    "--face",
    sad_video_path,
    "--audio",
    AUDIO_PATH,
    "--outfile",
    FINAL_VIDEO,
    "--pads",
    *PADS.split(),
    "--resize_factor",
    str(RESIZE),
    "--face_det_batch_size",
    str(FACE_BS),
    "--wav2lip_batch_size",
    str(WAV_BS),
]

if not SMOOTH_FACE:
    cmd_wav.append("--nosmooth")

wav_rc = _run_and_stream(cmd_wav, cwd=WAV2LIP_PATH)
if wav_rc != 0 or not os.path.exists(FINAL_VIDEO):
    raise RuntimeError("Wav2Lip failed")

print("Done! Final video:", FINAL_VIDEO)
