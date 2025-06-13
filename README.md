# 🎬 SaranshAI – Your AI-powered Video Summarizer

**SaranshAI** is a simple yet powerful tool designed to extract meaningful summaries from YouTube videos. Whether you're revising lectures, catching up on talks, or just want to save time – SaranshAI gets the job done, fast and smart.

> 🚀 *Currently supports English-language videos with short to moderate duration.*  
> 🌐 *Deployment coming soon! Stay tuned!*

---

## 🔍 Features

- 🎧 **Audio Extraction** from YouTube videos  
- 📝 **Transcription** using OpenAI Whisper  
- ✨ **Summarization** with HuggingFace's DistilBART  
- 📄 **Downloadable Summary PDF**  
- 💡 Easy-to-use **Streamlit UI**

---

## ⚙️ Tech Stack

| Layer        | Technology                          |
|--------------|--------------------------------------|
| Backend      | Python                               |
| Transcription| OpenAI Whisper                       |
| Summarization| HuggingFace Transformers (`distilbart-cnn-12-6`) |
| Frontend UI  | Streamlit                            |
| PDF Export   | FPDF                                 |
| YouTube Audio| yt-dlp                               |

---

## 🚦 Limitations (for now)

- ❗ Only English videos are supported.
- ⏳ Works best with **short to medium-length** videos.
- 📶 Requires stable internet (especially during download and model inference).

Actively working on:
- 🌍 Multilingual support
- ⏱️ Handling longer videos with better chunking
- ☁️ One-click web deployment
