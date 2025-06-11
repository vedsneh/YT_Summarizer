import streamlit as st
import os
import uuid
import yt_dlp
from fpdf import FPDF
from transformers import pipeline
from faster_whisper import WhisperModel

# Load Faster Whisper model
model_size = "base"  # use "tiny" if streamlit app runs out of memory
whisper_model = WhisperModel(model_size, device="cpu", compute_type="int8")

# Hugging Face Summarizer
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Audio downloader
def download_audio(video_url):
    output_path = "downloads"
    os.makedirs(output_path, exist_ok=True)

    unique_filename = str(uuid.uuid4())
    mp3_path = os.path.join(output_path, f"{unique_filename}.mp3")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_path, f"{unique_filename}.%(ext)s"),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)

    if not os.path.exists(mp3_path):
        raise FileNotFoundError(f"Audio file not found: {mp3_path}")

    return mp3_path, info

# Transcribe audio using faster-whisper
def transcribe(audio_path):
    segments, _ = whisper_model.transcribe(audio_path)
    return " ".join([segment.text for segment in segments])

# Summarize transcript
def generate_summary(text):
    max_chunk = 1000
    text = text.strip().replace("\n", " ")
    chunks = [text[i:i + max_chunk] for i in range(0, len(text), max_chunk)]
    summary = []
    for chunk in chunks:
        summary_text = summarizer(chunk, max_length=130, min_length=30, do_sample=False)[0]['summary_text']
        summary.append(summary_text)
    return "\n\n".join(summary)

# Create PDF
def create_pdf(summary, filename="summary.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in summary.split('\n'):
        pdf.multi_cell(0, 10, line)
    pdf_path = os.path.join("downloads", filename)
    pdf.output(pdf_path)
    return pdf_path

# ------------------------------
# Streamlit UI
# ------------------------------
st.set_page_config(page_title="YouTube Video Summarizer", layout="centered")
st.title("🎬 YouTube Video Summarizer (Free - Hugging Face + Faster Whisper)")

video_url = st.text_input("🔗 Paste YouTube video URL here:")

if st.button("Generate Summary"):
    if not video_url:
        st.warning("Please enter a valid URL.")
    else:
        with st.spinner("📥 Downloading audio..."):
            try:
                audio_path, info = download_audio(video_url)
                st.success("Audio downloaded successfully!")
                st.write(f"🔊 Saved at: `{audio_path}`")
            except Exception as e:
                st.error(f"❌ Failed to download audio: {e}")
                st.stop()

        with st.spinner("🎧 Transcribing with Faster Whisper..."):
            try:
                transcript = transcribe(audio_path)
            except Exception as e:
                st.error(f"❌ Transcription failed: {e}")
                st.stop()

        with st.spinner("✍️ Summarizing with Hugging Face..."):
            try:
                summary = generate_summary(transcript)
            except Exception as e:
                st.error(f"❌ Summarization failed: {e}")
                st.stop()

        st.success("✅ Summary Ready!")
        st.text_area("📝 Summary:", summary, height=300)

        pdf_path = create_pdf(summary)
        with open(pdf_path, "rb") as f:
            st.download_button("📄 Download PDF", f, file_name="summary.pdf", mime="application/pdf")

        st.markdown(f"**🎥 Title:** {info['title']}")
        st.markdown(f"**📅 Published:** {info.get('upload_date', 'N/A')}")
        st.markdown(f"**👁️ Views:** {info.get('view_count', 'N/A')}")

