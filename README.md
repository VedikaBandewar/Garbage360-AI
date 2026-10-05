# Garbage360 AI 🚮

### Report. Understand. Prioritize. Clean. Verify.

A complete, runnable Streamlit hackathon MVP for an AI-first approach to India's garbage problem.

## Why this version?

The original Smart Fixers / SmartCity 360 concept already had:
- citizen reporting
- image/audio/text input
- location tracking
- AI categorization
- duplicate-report handling
- status tracking
- multilingual/voice support
- maps
- escalation

Garbage360 AI narrows that idea to waste management and adds:
- waste classification
- severity and priority
- drain-risk detection
- hotspot intelligence
- duplicate/location signals
- before/after cleanup verification
- optional real multimodal AI through Gemini

## What you can test now

### Citizen Report
Upload an image, enter a description and location, then submit.

### Admin Dashboard
View all reports, statistics and change status.

### Hotspot Intelligence
View repeated locations and a map when coordinates exist.

### Resolution Verification
Upload before/after images and get a visual-change score.

## AI modes

### 1. Local demo mode
Works without any API key. It is transparent, lightweight and designed for testing the full workflow.

### 2. Gemini multimodal mode
If `GEMINI_API_KEY` is configured, the app sends the report and optional image to Gemini and asks for structured waste analysis.

The app falls back to local demo inference if the optional AI service fails.

Do not describe the local keyword engine as a trained ML model.

## Run locally

### Windows

```bat
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

If you do not want the optional Gemini dependency:

```bat
pip install -r requirements-minimal.txt
streamlit run app.py
```

## Demo data

Open the sidebar and click:

**Load demo reports**

Then inspect the Admin Dashboard and Hotspot Intelligence pages.

## Optional Gemini key

Create a `.streamlit/secrets.toml` file:

```toml
GEMINI_API_KEY = "your-key-here"
```

Never commit that file to GitHub.

For Streamlit Community Cloud, put the same key under the app's Secrets settings.

## Deployment

The easiest deployment route is Streamlit Community Cloud.

1. Create a GitHub repository.
2. Upload all project files except `venv/`, `garbage360.db` and `.streamlit/secrets.toml`.
3. Open Streamlit Community Cloud.
4. Select the GitHub repository.
5. Set the main file to `app.py`.
6. Deploy.
7. Add `GEMINI_API_KEY` under Secrets if you want real multimodal AI.
8. Copy the public app URL into the hackathon submission form.

## Important limitation

Streamlit Community Cloud is suitable for a prototype/demo. For production municipal deployment, use a proper database, authentication, object storage, model serving and secure backend.

## Suggested final hackathon upgrades

1. Train or fine-tune a waste image detector.
2. Add real GPS/map integration.
3. Add image-embedding duplicate detection.
4. Add proper geospatial hotspot clustering.
5. Add collection-route optimization.
6. Add multilingual voice input.
7. Add real before/after object detection.
8. Add citizen/admin authentication.
9. Add deployment architecture.
10. Measure model performance with precision, recall and F1.

## Project structure

```text
Garbage360_AI_COMPLETE/
├── app.py
├── ai_engine.py
├── database.py
├── hotspot.py
├── verification.py
├── requirements.txt
├── requirements-minimal.txt
├── README.md
├── GUIDE.md
├── HACKATHON_PITCH.md
├── .gitignore
├── .streamlit/
│   └── secrets.toml.example
└── demo/
    └── demo_garbage.jpg
```
