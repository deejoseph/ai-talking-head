# 馃幀 AI Talking Head Pipeline

## UI Preview

![UI](UI.png)


A fully automated pipeline to generate talking head videos from text, using:

- 馃 SadTalker (AI talking head generation)
- 馃攰 TTS (text-to-speech)
- 馃帪 FFmpeg (video post-processing)

---

## 馃殌 Features

- End-to-end pipeline: **Text 鈫?Audio 鈫?Talking Video**
- Works locally (Windows + GPU)
- Compatible with Kaggle environment
- Automatic video formatting (vertical / social media ready)
- Modular design for future expansion

---

## 馃搨 Project Structure
ai_video_pipeline/
鈹溾攢鈹€ run.py # Main entry point
鈹溾攢鈹€ config.py # Configurations
鈹溾攢鈹€ inputs/ # Input assets
鈹?鈹溾攢鈹€ face.png
鈹?鈹斺攢鈹€ audio.wav
鈹溾攢鈹€ outputs/ # Generated videos
鈹溾攢鈹€ sadtalker/ # SadTalker source code
鈹溾攢鈹€ tts/ # TTS module
鈹斺攢鈹€ gfpgan/ # Face enhancement models

## 馃斀 Model Download

Due to GitHub file size limits, model files are not included.

Please download manually:

- SadTalker:
  https://github.com/OpenTalker/SadTalker/releases

- GFPGAN weights will be downloaded automatically on first run.

Place them under:

sadtalker/checkpoints/

## 鈿欙笍 Requirements

- Python 3.10 (recommended)
- NVIDIA GPU (tested on RTX 3070 / T4)
- CUDA-compatible PyTorch

---

## 馃敡 Installation

```bash
conda create -n pixel_ai python=3.10
conda activate pixel_ai

pip install -r requirements.txt

鈻讹笍 Usage
python run.py

Pipeline will:

Generate audio from text
Run SadTalker to create talking head video
Optimize video using ffmpeg
馃摴 Output

Generated videos will be saved in:

outputs/
鈿狅笍 Notes
Some dependencies are sensitive to versions:
numpy < 2.0
torchvision compatibility required
First run may download model weights automatically
馃 Future Improvements
Better lip-sync quality (Wav2Lip integration)
Emotion / expression control
Web UI (Gradio / Flask)
Batch generation support
馃懁 Author

Joseph Dee

猸?If this project helps you, feel free to star the repo!

