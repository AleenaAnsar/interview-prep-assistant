# Interview Preparation Assistant

AI-powered mock interview tool: generates role-specific questions, accepts spoken
or typed answers, transcribes speech with Whisper, scores answers with Claude,
and gives structured feedback + a downloadable report.

**Stack:** Python, Streamlit, Anthropic Claude API (LLM), OpenAI Whisper (Speech-to-Text), textstat (NLP).

---

## Step-by-step setup in VS Code

### 1. Install prerequisites
- Python 3.10+ installed (`python --version` to check)
- [FFmpeg](https://ffmpeg.org/download.html) installed and on your PATH (Whisper needs it to read audio).
  - Windows: `winget install ffmpeg` or download from the site above.
  - Mac: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`
- VS Code with the **Python extension** (Microsoft) installed.

### 2. Get the project into VS Code
- Unzip `interview-prep-assistant.zip` anywhere on your machine.
- Open VS Code → `File > Open Folder` → select the `interview-prep-assistant` folder.

### 3. Create a virtual environment
Open VS Code's integrated terminal (`` Ctrl+` ``) and run:
```bash
python -m venv venv
```
Activate it:
- Windows: `venv\Scripts\activate`
- Mac/Linux: `source venv/bin/activate`

VS Code may prompt "Select Interpreter" — choose the one inside `venv`.

### 4. Install dependencies
```bash
pip install -r requirements.txt
```
> Note: `openai-whisper` pulls in PyTorch and will take a few minutes the first time.

### 5. Get an Anthropic API key
- Go to https://console.anthropic.com/ → create an API key.
- In the project folder, copy `.env.example` to a new file named `.env`:
```bash
cp .env.example .env       # Mac/Linux
copy .env.example .env     # Windows
```
- Open `.env` and paste your key:
```
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx
```

### 6. Run the app
```bash
streamlit run app.py
```
This opens the app in your browser at `http://localhost:8501`.

### 7. Use it
1. Enter a target role (e.g. "AI/ML Engineer"), experience level, and number of questions.
2. Click **Generate questions**.
3. For each question, either type an answer or click the mic icon to record one
   (it's transcribed automatically by Whisper).
4. Click **Submit answer** — you'll see scores and feedback after each one.
5. After the last question, view your full report and download it as a `.txt` file.

---

## Project structure
```
interview-prep-assistant/
├── app.py                     # Streamlit UI and app flow
├── requirements.txt
├── .env.example
├── README.md
└── src/
    ├── __init__.py
    ├── question_generator.py  # Generates questions via Claude
    ├── speech_to_text.py      # Whisper-based transcription
    ├── nlp_metrics.py         # Filler-word & readability metrics
    ├── scorer.py               # LLM scoring + NLP penalty blending
    ├── feedback.py              # Structured feedback generation
    └── utils.py                 # API key loading, report building
```

## Customization ideas (good for a dissertation/CV writeup)
- Swap Whisper's `"base"` model for `"small"` or `"medium"` in `speech_to_text.py` for higher accuracy at the cost of speed.
- Add a speaking-pace metric by tracking audio duration alongside word count in `nlp_metrics.py`.
- Add a question bank / resume-upload mode so questions are tailored to a candidate's actual CV.
- Persist results to a SQLite file to track score improvement across multiple practice sessions.

## Troubleshooting
- **"FFmpeg not found"** — install FFmpeg and restart your terminal/VS Code so PATH updates.
- **Whisper is slow on CPU** — this is expected for the first transcription (model loads into memory); subsequent ones in the same session are faster. A GPU machine will be much faster.
- **`ANTHROPIC_API_KEY not found`** — make sure your `.env` file (not `.env.example`) exists in the project root and the key has no quotes around it.
- **Microphone not recording in browser** — make sure you've granted microphone permission to `localhost:8501` in your browser settings.
