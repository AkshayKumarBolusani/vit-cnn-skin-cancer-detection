# Skin Disease Prediction ViT — Quick Start Guide

## What This Project Does

A **Vision Transformer (ViT) / DINOv2** based **skin disease prediction** system. The main app is in `Transformer_Skin_canser/`: it provides an API and UI for uploading skin images and getting predictions, with optional RL agent and Groq/LangChain chat. Includes a smaller Flask app in `skin-disease/`.

## Prerequisites

- **Python 3.10+**
- pip
- **Groq API key** (for chat features, if used)

## Step-by-Step: Run on Any System

1. **Open a terminal** and go to the inner project folder:
   ```bash
   cd path/to/Skin\ Disease\ Prediction\ ViT/Transformer_Skin_canser
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables:**  
   Copy `.env.example` to `.env` if present and set `GROQ_API_KEY` (or other keys) as needed.

5. **Run the FastAPI app:**
   ```bash
   uvicorn main:app --reload
   ```
   Or run `main.py` as indicated in the project.

6. **Open in a browser:**  
   API: **http://localhost:8000** — Docs: **http://localhost:8000/docs**.  
   If there is a static HTML UI (e.g. `Static/index.html`), open it or serve it via the app.

## Alternative: Simple Flask skin-disease app

```bash
cd path/to/Skin\ Disease\ Prediction\ ViT/Transformer_Skin_canser/skin-disease
pip install -r requirements.txt
python app.py
```
Then open the URL shown (e.g. http://127.0.0.1:5000).

## Notes

- Keep `model/` weights (e.g. `dinov2_finetuned.pth`, `model_weights_RESNET50.pth`) in place.
- Training/notebook: use `cnn-vs-vision-transformer.ipynb` in the same folder with Jupyter.
