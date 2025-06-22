# Youtube_VideoDownloader
# 🎬 YouTube Video Downloader & Description Analyzer

An advanced Gradio-powered web app that lets you:

- ✅ Download YouTube videos in various qualities or audio-only MP3 format.
- 🔍 Analyze video content using **Google Gemini API** to generate:
  - Timestamped scene-by-scene breakdowns
  - Inferred dialogues
  - Content type, background music, influencer status
- 📄 Export full video reports in beautifully styled **PDF** format
- 🍪 Utilize your own YouTube account cookies for premium/restricted video access

---

## 🚀 Features

| Feature | Description |
|--------|-------------|
| 🎥 Video Download | Download videos (Best, 720p, 480p) or Audio-only |
| 📊 Content Analysis | Summarized insights + visual-rich HTML report |
| 🤖 Gemini API Support | AI-powered scene descriptions and dialogues |
| 📝 PDF Generation | Export reports as downloadable PDFs |
| 🍪 Cookies Support | Analyze or download videos behind login |

---

## 🛠️ Installation & Setup

1. **Install dependencies:**

```bash
pip install -r requirements.txt
```

> Required Python version: 3.8+

2. **Run the app:**

```bash
python app.py
```

The app will launch in your browser automatically.

---

## 🔑 Get Google Gemini API Key

To enable AI-powered analysis, follow these steps:

1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Create/select a project
3. Enable **Generative Language API**
4. Go to **Credentials** → Create **API key**
5. Copy and paste the key into the app when prompted

---

## 🍪 How to Get YouTube Cookies File

To download videos that require login (e.g. age-restricted, private, premium), upload your cookies in `.txt` format.

### 🧩 Step-by-step (for Chrome / Firefox):

1. **Install Extension**:  
   Download the "Get cookies.txt" extension:
   - Chrome: [Get cookies.txt](https://chrome.google.com/webstore/detail/get-cookiestxt/nenlahapcbofgnanklpelkaejcehkggg)
   - Firefox: [Get cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)

2. **Log into YouTube** in your browser.

3. Click the extension icon → Select the **youtube.com** domain → Click **"Download"** to save `cookies.txt`.

4. **Upload this file** in the app interface.

---

## 🧪 Example Workflow

1. 🔑 Enter your **Gemini API Key**.
2. 🍪 Upload **cookies.txt** file.
3. 🎥 Paste any **YouTube URL**.
4. 📊 Click **"Analyze Video"** to get a detailed breakdown.
5. 📄 Optionally, download the full report as a PDF.
6. ⬇️ Switch tabs to download the video or audio.

---

## 📂 Project Structure

```
app.py                  # Main Gradio application
README.md               # You're here!
requirements.txt        # Python dependencies
```

---

## 💡 Tech Stack

- [Gradio](https://www.gradio.app/) for interactive UI
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for video download
- [xhtml2pdf](https://github.com/xhtml2pdf/xhtml2pdf) for PDF generation
- [Google Generative AI](https://ai.google.dev/) for scene analysis

---

## 📄 License

Apache 2.0 License

---

## 🙋‍♀️ Created by [Mukti Bhuyan]

This tool was built to help content creators, educators, and researchers get deep insights into YouTube videos with a few clicks.

---

## 🧠 Tip

Use Gemini API for **richer insights**, including:
- Mood/atmosphere inference
- Real-time dialogue reconstruction
- Advanced content tagging

---
