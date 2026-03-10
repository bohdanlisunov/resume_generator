# 📄 AI Resume Generator

Automatically generates tailored resumes for job vacancies using AI. Parses vacancy data, adapts your base resume to each position, and saves results to Google Docs via the Drive API.

## ✨ Features

- 🤖 AI-powered resume tailoring per vacancy
- 📂 Supports multiple tech stacks: Python, JavaScript, PHP, Java, .NET, Frontend, Full Stack, WordPress, AI/ML
- ☁️ Auto-upload to Google Docs / Google Drive
- 🎭 Playwright-based automation for job board scraping
- 📁 Local output in `.txt` / `.rtf` formats

## 🛠 Tech Stack

- **Python 3.12**
- **Google Docs & Drive API**
- **Playwright** — browser automation
- **OAuth 2.0** — Google authentication

## 📁 Project Structure

```
resume_generator/
├── src/
│   ├── generator.py        # AI resume generation logic
│   └── playwright_bot.py   # Browser automation / vacancy scraping
├── data/
│   └── vacancies.json      # Vacancy data
├── vacancies_*.json        # Per-stack vacancy lists
├── main.py                 # Entry point
├── auth.py                 # Google OAuth setup
├── upload.py               # Google Drive uploader
├── requirements.txt
└── .env.example
```

## ⚙️ Setup

### 1. Clone the repo

```bash
git clone https://github.com/bohdanlisunov/resume_generator.git
cd resume_generator
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your values
```

`.env` structure:

```env
TEMPLATE_ID=your_google_doc_template_id
GOOGLE_CREDENTIALS=credentials.json
FOLDER_ID=your_google_drive_folder_id
```

### 4. Set up Google credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project and enable **Google Docs API** and **Google Drive API**
3. Create a **Service Account** and download `credentials.json`
4. Place `credentials.json` in the project root (it's in `.gitignore`)

### 5. Run

```bash
python main.py
```

## 🔒 Security Notes

The following files are excluded from the repository via `.gitignore` and should **never** be committed:

- `credentials*.json` — Google Service Account keys
- `oauth_credentials.json` — OAuth client secrets
- `token.pickle` / `token.json` — saved auth tokens
- `.env` — environment variables
- `data/base_resume.txt` — personal resume data

## 📜 License

MIT
