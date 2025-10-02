# 🚀 Cara Deploy ke Vercel

## Prerequisites
1. Account Vercel (https://vercel.com)
2. OpenAI API Key

## ⚠️ PENTING - Setup requirements.txt

Sebelum deploy, buat file `requirements.txt` di root folder dengan isi:
```
flask==3.1.2
openai==2.0.1
```

Atau copy dari file `deps.txt` yang sudah ada.

## Langkah-Langkah Deployment:

### 1. Push ke GitHub
```bash
git init
git add .
git commit -m "Initial commit: YAPS Content Generator"
git remote add origin <your-github-repo-url>
git push -u origin main
```

### 2. Deploy di Vercel
1. Buka https://vercel.com/new
2. Import repository GitHub Anda
3. Vercel akan auto-detect Flask app
4. Klik "Deploy"

### 3. Set Environment Variables
Di Vercel Dashboard → Settings → Environment Variables, tambahkan:

```
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### 4. Redeploy (jika perlu)
Setelah set environment variables, Vercel akan auto-redeploy.

## Struktur File untuk Vercel:
```
├── app.py              # Main Flask application
├── vercel.json         # Vercel configuration
├── templates/
│   └── index.html      # UI template
├── .gitignore          # Git ignore file
└── pyproject.toml      # Dependencies (auto-detected)
```

## Environment Variables yang Dibutuhkan:
- `OPENAI_API_KEY`: Your OpenAI API key

## Testing Lokal:
```bash
export OPENAI_API_KEY=your-key-here
python app.py
```

Buka: http://localhost:5000

## Features:
- ✅ Auto-detect projects dari Kaito Pre-TGE Arena
- ✅ 3 jenis prompt AI (Data-Driven, Competitive, Thesis)
- ✅ YAPS score analysis
- ✅ Copy to clipboard
- ✅ Fully responsive UI
