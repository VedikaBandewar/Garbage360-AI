# Garbage360 AI — Complete Beginner Guide

You asked for a project you can test first and then upload as a live link. This version is designed exactly for that.

# PHASE 1 — Run the project on your computer

## Step 1: Extract

Extract:

`Garbage360_AI_COMPLETE.zip`

Open the extracted folder in VS Code.

## Step 2: Open terminal

In VS Code:

**Terminal → New Terminal**

## Step 3: Create a virtual environment

```bat
python -m venv venv
```

Activate it:

```bat
venv\Scripts\activate
```

You should see `(venv)` in the terminal.

## Step 4: Install packages

```bat
pip install -r requirements.txt
```

This may take a little time.

## Step 5: Start the app

```bat
streamlit run app.py
```

Your browser should open automatically.

If it does not, open the URL printed in the terminal, normally:

`http://localhost:8501`

---

# PHASE 2 — Test the complete workflow

## Test 1: Demo reports

On the left sidebar click:

**Load demo reports**

Then go to:

**Admin Dashboard**

You should see multiple reports.

## Test 2: Create a critical report

Go to:

**Citizen Report**

Description:

```text
Huge mixed garbage pile beside a blocked drain. Plastic bottles,
bags and food waste are scattered across the road.
```

Location:

```text
Nagpur Central
```

Click:

**Submit & Analyze with AI**

You should get a high/critical priority result.

## Test 3: Create a low-priority report

Description:

```text
Small paper waste near a public dustbin.
```

Location:

```text
Nagpur Central
```

Submit it.

Compare the two results.

## Test 4: Status workflow

Go to:

**Admin Dashboard**

Select a report and change:

```text
Reported
→ Verified
→ Assigned
→ In Progress
→ Resolved
```

## Test 5: Hotspot

Go to:

**Hotspot Intelligence**

Because the demo data contains repeated locations, you can see hotspot signals.

## Test 6: Before/after

Go to:

**Resolution Verification**

Upload two images.

Click:

**Verify cleanup**

The prototype calculates a visual-change score.

---

# PHASE 3 — Turn on real multimodal AI

The project works without an API key.

For a stronger hackathon demo, configure Gemini.

Create:

```text
.streamlit/secrets.toml
```

Use:

```toml
GEMINI_API_KEY = "YOUR_KEY"
```

Then restart:

```bat
streamlit run app.py
```

Now the app will try Gemini first and fall back to the local engine if the service fails.

Do not upload the secret file to GitHub.

---

# PHASE 4 — Prepare GitHub

Create a new GitHub repository, for example:

`garbage360-ai`

Upload:

```text
app.py
ai_engine.py
database.py
hotspot.py
verification.py
requirements.txt
requirements-minimal.txt
README.md
GUIDE.md
HACKATHON_PITCH.md
.streamlit/secrets.toml.example
demo/
```

Do NOT upload:

```text
venv/
garbage360.db
.streamlit/secrets.toml
```

---

# PHASE 5 — Deploy a public link

Use Streamlit Community Cloud.

When creating the app:

- Repository: your GitHub repository
- Branch: main
- Main file: `app.py`

Deploy.

After deployment, Streamlit gives you a public URL.

Example format:

```text
https://your-app-name.streamlit.app
```

Put that URL in the hackathon submission.

If using Gemini:
go to the deployed app's Secrets settings and add:

```toml
GEMINI_API_KEY = "YOUR_KEY"
```

---

# PHASE 6 — What to demonstrate to judges

Do NOT spend the whole demo showing code.

Show this:

## 1. Citizen

Upload garbage photo.

## 2. AI

Show:

```text
Waste type
Severity
Drain risk
Priority
Recommended action
```

## 3. Admin

Show dashboard.

## 4. Hotspot

Show repeated garbage locations.

## 5. Action

Change:

```text
Reported → Assigned → In Progress
```

## 6. Verification

Show before/after cleanup verification.

## 7. Impact

Explain:

> Garbage360 AI is not only a complaint portal. It converts citizen reports into prioritized waste-management intelligence so limited municipal resources can be directed to the problems that need attention first.

---

# PHASE 7 — What we should improve after the first live link

Do not immediately rebuild everything.

First get the link working.

Then upgrade one feature at a time:

1. Real waste detector
2. Better duplicate detection
3. Better hotspot clustering
4. Real map
5. Route optimization
6. Voice input
7. Multilingual support
8. Before/after AI verification
9. Authentication
10. Final pitch

This keeps the project stable while making it more impressive.
