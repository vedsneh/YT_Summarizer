import streamlit as st
import os
import uuid
import yt_dlp
import whisper
from fpdf import FPDF
from transformers import pipeline

# Load Whisper model (use 'tiny' for Streamlit Cloud)
whisper_model = whisper.load_model("tiny")

# Hugging Face Summarizer
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")


def download_audio(video_url):
    output_path = "downloads"
    os.makedirs(output_path, exist_ok=True)

    unique_filename = str(uuid.uuid4())
    audio_path = os.path.join(output_path, f"{unique_filename}.m4a")

    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'outtmpl': audio_path,
        'postprocessors': [],  # 🚫 Disable all postprocessing
        'quiet': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)

    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    return audio_path, info


def transcribe(audio_path):
    result = whisper_model.transcribe(audio_path)
    return result["text"]


def generate_summary(text):
    max_chunk = 1000
    text = text.strip().replace("\n", " ")
    chunks = [text[i:i + max_chunk] for i in range(0, len(text), max_chunk)]
    summary = []
    for chunk in chunks:
        summary_text = summarizer(chunk, max_length=130, min_length=30, do_sample=False)[0]['summary_text']
        summary.append(summary_text)
    return "\n\n".join(summary)


def create_pdf(summary, filename="summary.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in summary.split('\n'):
        pdf.multi_cell(0, 10, line)
    pdf_path = os.path.join("downloads", filename)
    pdf.output(pdf_path)
    return pdf_path


# ------------------------------ Streamlit UI ------------------------------
st.set_page_config(page_title="YouTube Video Summarizer", layout="centered")
st.title("🎬 YouTube Video Summarizer (Streamlit + Whisper + HuggingFace)")

video_url = st.text_input("🔗 Paste YouTube video URL here:")

if st.button("Generate Summary"):
    if not video_url:
        st.warning("Please enter a valid URL.")
    else:
        with st.spinner("📥 Downloading audio..."):
            try:
                audio_path, info = download_audio(video_url)
            except Exception as e:
                st.error(f"❌ Failed to download audio: {e}")
                st.stop()

        with st.spinner("🎧 Transcribing with Whisper..."):
            try:
                transcript = transcribe(audio_path)
            except Exception as e:
                st.error(f"❌ Transcription failed: {e}")
                st.stop()

        with st.spinner("✍️ Summarizing..."):
            try:
                summary = generate_summary(transcript)
            except Exception as e:
                st.error(f"❌ Summarization failed: {e}")
                st.stop()

        st.success("✅ Summary Ready!")
        st.text_area("📝 Summary:", summary, height=300)

        pdf_path = create_pdf(summary)
        with open(pdf_path, "rb") as f:
            st.download_button("📄 Download Summary as PDF", f, file_name="summary.pdf", mime="application/pdf")

        st.markdown(f"**🎥 Title:** {info['title']}")
        st.markdown(f"**📅 Published:** {info.get('upload_date', 'N/A')}")
        st.markdown(f"**👁️ Views:** {info.get('view_count', 'N/A')}")
