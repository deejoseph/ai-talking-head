# 🎬 AI Talking Head Pipeline

A fully automated pipeline to generate talking head videos from text, using:

- 🧠 SadTalker (AI talking head generation)
- 🔊 TTS (text-to-speech)
- 🎞 FFmpeg (video post-processing)

---

## 🚀 Features

- End-to-end pipeline: **Text → Audio → Talking Video**
- Works locally (Windows + GPU)
- Compatible with Kaggle environment
- Automatic video formatting (vertical / social media ready)
- Modular design for future expansion

---

## 📂 Project Structure
ai_video_pipeline/
├── run.py # Main entry point
├── config.py # Configurations
├── inputs/ # Input assets
│ ├── face.png
│ └── audio.wav
├── outputs/ # Generated videos
├── sadtalker/ # SadTalker source code
├── tts/ # TTS module
└── gfpgan/ # Face enhancement models

## 🔽 Model Download

Due to GitHub file size limits, model files are not included.

Please download manually:

- SadTalker:
  https://github.com/OpenTalker/SadTalker/releases

- GFPGAN weights will be downloaded automatically on first run.

Place them under:

sadtalker/checkpoints/

## ⚙️ Requirements

- Python 3.10 (recommended)
- NVIDIA GPU (tested on RTX 3070 / T4)
- CUDA-compatible PyTorch

---

## 🔧 Installation

```bash
conda create -n pixel_ai python=3.10
conda activate pixel_ai

pip install -r requirements.txt

▶️ Usage
python run.py

Pipeline will:

Generate audio from text
Run SadTalker to create talking head video
Optimize video using ffmpeg
📹 Output

Generated videos will be saved in:

outputs/
⚠️ Notes
Some dependencies are sensitive to versions:
numpy < 2.0
torchvision compatibility required
First run may download model weights automatically
🧠 Future Improvements
Better lip-sync quality (Wav2Lip integration)
Emotion / expression control
Web UI (Gradio / Flask)
Batch generation support
👤 Author

Joseph Dee

⭐ If this project helps you, feel free to star the repo!