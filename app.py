import os
import shutil
import subprocess
import sys
import gradio as gr

BASE = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE, "inputs")
OUTPUT_VIDEO = os.path.join(BASE, "outputs", "output.mp4")
RUN_PY = os.path.join(BASE, "run.py")

os.makedirs(INPUT_DIR, exist_ok=True)

PRESETS = {
    "Realistic (Recommended)": {
        "pads_top": 0,
        "pads_bottom": 24,
        "resize_factor": 1,
        "face_bs": 8,
        "wav_bs": 16,
        "preprocess": "full",
        "pose_style": 1,
        "expression_scale": 1.05,
        "fix_head": False,
        "smooth_face": True,
        "use_enhancer": True,
        "run_wav2lip": True,
    },
    "Kaggle-Like (SadTalker Only)": {
        "pads_top": 0,
        "pads_bottom": 20,
        "resize_factor": 1,
        "face_bs": 8,
        "wav_bs": 16,
        "preprocess": "full",
        "pose_style": 0,
        "expression_scale": 1.0,
        "fix_head": True,
        "smooth_face": True,
        "use_enhancer": True,
        "run_wav2lip": False,
    },
    "Stable Head": {
        "pads_top": 0,
        "pads_bottom": 20,
        "resize_factor": 1,
        "face_bs": 8,
        "wav_bs": 16,
        "preprocess": "full",
        "pose_style": 0,
        "expression_scale": 0.9,
        "fix_head": True,
        "smooth_face": True,
        "use_enhancer": True,
        "run_wav2lip": True,
    },
}


def _to_path(file_obj):
    if file_obj is None:
        return None
    if isinstance(file_obj, str):
        return file_obj
    if isinstance(file_obj, dict):
        return file_obj.get("name") or file_obj.get("path")
    return getattr(file_obj, "name", None)


def apply_preset(name):
    p = PRESETS[name]
    return (
        gr.update(value=p["pads_top"]),
        gr.update(value=p["pads_bottom"]),
        gr.update(value=p["resize_factor"]),
        gr.update(value=p["face_bs"]),
        gr.update(value=p["wav_bs"]),
        gr.update(value=p["preprocess"]),
        gr.update(value=p["pose_style"]),
        gr.update(value=p["expression_scale"]),
        gr.update(value=p["fix_head"]),
        gr.update(value=p["smooth_face"]),
        gr.update(value=p["use_enhancer"]),
        gr.update(value=p["run_wav2lip"]),
    )


def run_pipeline(
    image,
    audio,
    pads_top,
    pads_bottom,
    resize_factor,
    face_bs,
    wav_bs,
    pose_style,
    expression_scale,
    fix_head,
    preprocess,
    smooth_face,
    use_enhancer,
    run_wav2lip,
):
    try:
        image_src = _to_path(image)
        audio_src = _to_path(audio)

        if not image_src or not os.path.exists(image_src):
            return None, None, "Error: please upload a valid portrait image."
        if not audio_src or not os.path.exists(audio_src):
            return None, None, "Error: please upload a valid WAV audio file."

        image_path = os.path.join(INPUT_DIR, "image.png")
        audio_path = os.path.join(INPUT_DIR, "audio.wav")

        for p in (image_path, audio_path, OUTPUT_VIDEO):
            if os.path.exists(p):
                os.remove(p)

        shutil.copy(image_src, image_path)
        shutil.copy(audio_src, audio_path)

        if os.path.getsize(audio_path) == 0:
            return None, None, "Error: audio file is empty."

        env = os.environ.copy()
        env["PADS"] = f"0 {int(pads_top)} 0 {int(pads_bottom)}"
        env["RESIZE"] = str(int(resize_factor))
        env["FACE_BS"] = str(int(face_bs))
        env["WAV_BS"] = str(int(wav_bs))
        env["POSE_STYLE"] = str(int(pose_style))
        env["EXPRESSION_SCALE"] = str(float(expression_scale))
        env["FIX_HEAD"] = "1" if fix_head else "0"
        env["PREPROCESS"] = preprocess
        env["SMOOTH_FACE"] = "1" if smooth_face else "0"
        env["USE_ENHANCER"] = "1" if use_enhancer else "0"
        env["RUN_WAV2LIP"] = "1" if run_wav2lip else "0"

        process = subprocess.Popen(
            [sys.executable, RUN_PY],
            cwd=BASE,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        log_lines = []
        assert process.stdout is not None
        for line in process.stdout:
            log_lines.append(line.rstrip("\n"))

        code = process.wait()
        log = "\n".join(log_lines)

        if code != 0:
            return None, None, f"Pipeline failed (exit code {code})\n\n{log}"

        if not os.path.exists(OUTPUT_VIDEO):
            return None, None, f"Output video not found: {OUTPUT_VIDEO}\n\n{log}"

        return OUTPUT_VIDEO, OUTPUT_VIDEO, log

    except Exception as exc:
        return None, None, str(exc)


with gr.Blocks(title="PixelSmile AI Video") as demo:
    gr.Markdown("# PixelSmile Talking Head Generator")
    gr.Markdown("Upload image/audio, tune parameters, generate video, and download the result.")

    with gr.Row():
        image_input = gr.File(file_types=[".png", ".jpg", ".jpeg"], label="Input Image")
        audio_input = gr.File(file_types=[".wav"], label="Input Audio (WAV)")

    with gr.Row():
        preset = gr.Dropdown(
            choices=list(PRESETS.keys()),
            value="Realistic (Recommended)",
            label="Parameter Preset",
        )
        apply_preset_btn = gr.Button("Apply Preset")

    with gr.Accordion("Advanced Parameters", open=True):
        pads_top = gr.Slider(0, 50, value=0, step=1, label="Face Pad Top")
        pads_bottom = gr.Slider(0, 80, value=24, step=1, label="Face Pad Bottom")
        resize_factor = gr.Slider(1, 4, value=1, step=1, label="Resize Factor")

        face_bs = gr.Slider(1, 32, value=8, step=1, label="Face Det Batch Size")
        wav_bs = gr.Slider(1, 64, value=16, step=1, label="Wav2Lip Batch Size")

        preprocess = gr.Dropdown(
            choices=["crop", "full", "extfull"],
            value="full",
            label="SadTalker Preprocess",
        )
        pose_style = gr.Slider(0, 45, value=1, step=1, label="Pose Style (0-45)")
        expression_scale = gr.Slider(0.5, 1.5, value=1.05, step=0.05, label="Expression Scale")

        fix_head = gr.Checkbox(value=False, label="Fix Head (less movement)")
        smooth_face = gr.Checkbox(value=True, label="Enable Wav2Lip detection smoothing")
        use_enhancer = gr.Checkbox(value=True, label="Use GFPGAN enhancer")
        run_wav2lip = gr.Checkbox(value=True, label="Run Wav2Lip")

    run_btn = gr.Button("Generate", variant="primary")

    output_video = gr.Video(label="Output Video")
    download_file = gr.File(label="Download Output")
    log_output = gr.Textbox(lines=20, label="Runtime Log")

    apply_preset_btn.click(
        fn=apply_preset,
        inputs=[preset],
        outputs=[
            pads_top,
            pads_bottom,
            resize_factor,
            face_bs,
            wav_bs,
            preprocess,
            pose_style,
            expression_scale,
            fix_head,
            smooth_face,
            use_enhancer,
            run_wav2lip,
        ],
    )

    run_btn.click(
        fn=run_pipeline,
        inputs=[
            image_input,
            audio_input,
            pads_top,
            pads_bottom,
            resize_factor,
            face_bs,
            wav_bs,
            pose_style,
            expression_scale,
            fix_head,
            preprocess,
            smooth_face,
            use_enhancer,
            run_wav2lip,
        ],
        outputs=[output_video, download_file, log_output],
    )

demo.launch(server_name="0.0.0.0", server_port=7860)
