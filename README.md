# Netflix Meta-Scraper & Content Engine

![Project Banner](images/Title_Page.jpg)

## 🚀 Overview

**Netflix Meta-Scraper** is an advanced, automated content engine designed for social media creators (Xiaohongshu/Instagram). It combines web scraping, AI content generation, and dynamic image processing to produce ready-to-post "New on Netflix" updates in seconds.

## ✨ Key Features

- **🔍 Intelligent Scraper**: Automatically scrapes the latest Netflix "New to Watch" releases for any date range (handles pagination and dynamic loading).
- **🎨 Auto-Design Engine**: Generates high-fidelity "Ratings Champion" (收视冠军) cover images dynamically based on the date range.
- **🤖 AI Copywriter**: Integrated with GPT-4o-mini to write enthusiastic, emoji-rich social media posts (Little Red Book style).
- **📦 Smart Packaging**: One-click download of all assets (Cover Image + High-Res Movie Posters) in a clean Zip file (CSV removed).
- **⚡️ Modern UI**: Beautiful, responsive dashboard built with React + Vite + Tailwind CSS.

## 🛠️ Tech Stack

- **Backend**: Python 3.9+, FastAPI, Playwright (Async), OpenAI API
- **Frontend**: React 18, Vite, Tailwind CSS, Framer Motion, Lucide Icons
- **Image Processing**: Pillow (PIL), Playwright Screenshot Strategy

## 📦 Installation

### Prerequisites

- Python 3.9+
- Node.js 16+
- Google Chrome (for Playwright)

### 1. Clone the Repository

```bash
git clone https://github.com/StartToFinish-V/netflix-meta-scraper.git
cd netflix-meta-scraper
```

### 2. Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

### 4. Configuration (.env)

Create a `.env` file in the root directory:

```ini
OPENAI_API_KEY=sk-your-api-key-here
```

## 🚀 Usage

### Start the Application

1. **Start Backend** (Root Directory):
   ```bash
   python app.py
   ```
2. **Start Frontend** (Frontend Directory):
   ```bash
   cd frontend
   npm run dev
   ```
3. Open your browser at `http://localhost:5173`.

### Workflow

1. **Select Date Range**: Choose the dates you want to cover (e.g., Feb 11 - Feb 15).
2. **Initiate**: Click to start the scraper. The system will:
   - Scrape Netflix for new releases.
   - Download high-res posters.
   - Generate a custom "Title Page" cover.
3. **Generate Note**: AI will write a perfect social media caption for you.
4. **Download All**: Get a single Zip file with your Cover Image and all Movie Posters.

## 📂 Project Structure

```
.
├── app.py                 # FastAPI Backend & API Endpoints
├── netflix_scraper.py     # Core Playwright Scraper Logic
├── title_generator/       # Dynamic Cover Image Generator
├── images/                # Scraped Images & Generated Assets
├── frontend/              # React + Vite Frontend
│   ├── src/
│   │   ├── App.jsx        # Main UI Logic
│   │   └── index.css      # Tailwind & Global Styles
│   └── vite.config.js     # Frontend Config (Proxy to Backend)
└── requirements.txt       # Python Dependencies
```

## 📝 License

MIT License. Free to use and modify.

---

_Built with ❤️ for Creators._
