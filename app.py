import streamlit as st
import os
import uuid
import yt_dlp
import whisper
from fpdf import FPDF
from transformers import pipeline

whisper_model = whisper.load_model("tiny")

# Hugging Face Summarizer
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")


def download_audio(video_url):
    output_path = "downloads"
    os.makedirs(output_path, exist_ok=True)

    unique_filename = str(uuid.uuid4())
    audio_path = os.path.join(output_path, f"{unique_filename}.m4a")

    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio',
        'outtmpl': audio_path,
        'quiet': True,
        'postprocessors': []  
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

st.set_page_config(page_title="YouTube Video Summarizer", layout="centered")
st.markdown(
    """
    <div style='text-align: center; padding: 20px 0;'>
        <h1 style='font-size: 2.5em; margin-bottom: 0.2em;'>🎬 SaranshAI</h1>
        <h3 style='font-weight: normal; color: #A9A9A9;'>Your AI-powered video distiller</h3>
        <p style='max-width: 600px; margin: auto; font-size: 1.05em; line-height: 1.6;'>
            Get concise and clear summaries of any YouTube video in minutes!<br>
            🎧 <b>Powered by</b> OpenAI's <i>Whisper</i> for transcription and Hugging Face for summarization.<br>
            🚫 No sign-up, no ads — just paste the video link and let AI do the work!
        </p>
    </div>
    """,
    unsafe_allow_html=True
)



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
        from datetime import datetime

        upload_date_raw = info.get('upload_date', '')
        if upload_date_raw:
            try:
                formatted_date = datetime.strptime(upload_date_raw, '%Y%m%d').strftime('%B %d, %Y')
            except:
                formatted_date = upload_date_raw
        else:
            formatted_date = 'N/A'

        st.markdown(f"**📅 Published:** {formatted_date}")

        st.markdown(f"**👁️ Views:** {info.get('view_count', 'N/A')}")
