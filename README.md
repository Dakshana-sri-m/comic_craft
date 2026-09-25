# 🎨 ComicCraft - AI Comic Story Creator

**ComicCraft** is a web-based application that uses AI to generate personalized comic book stories and illustrations based on user-provided prompts. Built with **FastAPI** and integrated with **Google's Gemini AI** models along with **Stable Diffusion**, ComicCraft streamlines the creative process of generating storylines, dialogues, and vivid comic-style imagery automatically.

## ✨ Features

- **AI Story Generation** - Powered by Google Gemini (Flash for outlines, Pro for narration)
- **AI Illustrations** - Comic-style images via Stable Diffusion (Hugging Face API)
- **5-Panel Comics** - Structured comic panels with titles, scenes, and dialogues
- **PDF Export** - Download your comic as a professionally formatted PDF
- **Premium UI** - Dark theme with glassmorphism, animations, and responsive design

## 🛠️ Tech Stack

- **Backend**: FastAPI + Uvicorn
- **Frontend**: HTML, CSS, Jinja2 Templates
- **AI Models**: Google Gemini 1.5 (Flash + Pro), Stable Diffusion XL
- **PDF**: fpdf2
- **API**: Hugging Face Inference API

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/Dakshana-sri-m/comic_craft.git
cd comic_craft
```

### 2. Create virtual environment
```bash
python -m venv env
env\Scripts\activate   # Windows
# source env/bin/activate  # macOS/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Edit `.env` file with your API keys:
```
GEMINI_API_KEY=your_gemini_api_key_here
HF_API_KEY=your_huggingface_api_key_here
```

### 5. Run the server
```bash
uvicorn app.main:app --reload
```

### 6. Open in browser
- **App**: http://127.0.0.1:8000
- **API Docs**: http://127.0.0.1:8000/docs

## 📁 Project Structure

```
comic_craft/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── routes.py             # Route handlers
│   ├── gemini_flash.py       # Outline generation (Gemini Flash)
│   ├── gemini_pro.py         # Story generation (Gemini Pro)
│   ├── image_generator.py    # Image generation (Stable Diffusion)
│   ├── layout_builder.py     # Comic layout organizer
│   ├── exporters.py          # PDF export
│   └── schemas.py            # Pydantic models
├── templates/
│   ├── index.html            # Homepage
│   ├── comic_preview.html    # Comic preview
│   └── export_success.html   # Export confirmation
├── static/
│   ├── css/style.css
│   ├── panels/               # Generated images
│   └── exports/              # Generated PDFs
├── .env
├── requirements.txt
└── README.md
```

## 🔗 API Endpoints

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Homepage with creation form |
| `/generate` | POST | Form-based comic generation |
| `/generate-comic/json` | POST | JSON API comic generation |
| `/export-success` | GET | Export success page |
| `/download-pdf` | GET | PDF file download |
| `/test-image` | GET | Test image generation |

## 📝 License

This project is for educational purposes.
