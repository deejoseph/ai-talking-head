import os
import subprocess
from config import *
from tts.generate_audio import generate_audio

# =========================
# 🔥 基础路径（统一绝对路径）
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_AUDIO = os.path.join(BASE_DIR, "inputs", "input_audio.wav")
TTS_AUDIO   = os.path.join(BASE_DIR, "inputs", "tts_audio.wav")
IMAGE_PATH  = os.path.join(BASE_DIR, "inputs", "face.png")
OUTPUT_DIR  = os.path.join(BASE_DIR, "outputs")
SADTALKER_PATH = os.path.join(BASE_DIR, "sadtalker")

# =========================
# 🔥 模式选择
# =========================
MODE = "audio"   # "tts" 或 "audio"

# =========================
# 文本（仅 TTS 用）
# =========================
text = "人工智能时代已经到来，现在学习如何使用人工智能非常重要"

# =========================
# 🔥 选择音频来源
# =========================
if MODE == "tts":
    print("🎤 Using TTS mode...")
    AUDIO_PATH = TTS_AUDIO
    generate_audio(text, AUDIO_PATH)

elif MODE == "audio":
    print("🎧 Using input audio...")
    AUDIO_PATH = INPUT_AUDIO

else:
    raise ValueError("MODE must be 'tts' or 'audio'")

# =========================
# 🔍 文件检查（防踩坑）
# =========================
if not os.path.exists(AUDIO_PATH):
    raise FileNotFoundError(f"❌ Audio not found: {AUDIO_PATH}")

if not os.path.exists(IMAGE_PATH):
    raise FileNotFoundError(f"❌ Image not found: {IMAGE_PATH}")

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("✅ Audio:", AUDIO_PATH)
print("✅ Image:", IMAGE_PATH)

# =========================
# 🚀 调用 SadTalker（关键：cwd 解决 checkpoints 问题）
# =========================
print("Running SadTalker...")

cmd = [
    "python",
    "inference.py",
    "--driven_audio", AUDIO_PATH,
    "--source_image", IMAGE_PATH,
    "--result_dir", OUTPUT_DIR,
    "--still",
    "--preprocess", "full",
    "--batch_size", "1"
]

result = subprocess.run(cmd, cwd=SADTALKER_PATH)

# =========================
# ✅ 结果输出
# =========================
if result.returncode == 0:
    print("✅ Done! 视频已生成在 outputs 文件夹")
else:
    print("❌ Failed")