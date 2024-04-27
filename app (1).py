import streamlit as st
import openai
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
import re

MODEL_TYPE = 'gpt-3.5-turbo'

def clean_transcript(text):
    # Cleans up the transcript text by removing unwanted characters and spaces
    return re.sub(r'\[.*?\]', '', text).replace('um', '').translate(str.maketrans('', '', ',?!.\'"\“\”\‘\’:;[]{}\n\xa0\\')).strip().replace('\xa0', '').replace('  ', ' ').replace('"', '')

def get_video_length(last_transcript_section):
    # Calculates the video length from the last transcript section
    return (last_transcript_section['start'] + last_transcript_section['duration']) / 60

def get_video_url_id(video_url):
    # Extracts the video ID from a YouTube URL
    try:
        if "youtu.be" in video_url:
            video_id = video_url.split("/")[-1]
        else:
            video_id = video_url.split("v=")[1].split("&")[0]
        return video_id
    except:
        st.error("Please enter a valid YouTube video URL.")
        return None

def summarize_video(api_key, video_id):
    # Connect to OpenAI using the provided API key and summarize the video using the transcript
    openai.api_key = api_key
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_transcript(['en'])  # Attempt to get English transcripts
        transcript_list = transcript.fetch()
        video_length = get_video_length(transcript_list[-1])

        # Join and clean transcript texts
        clean_texts = [clean_transcript(t['text']) for t in transcript_list]
        full_text = ' '.join(clean_texts)
        prompt = "Summarize the following text into key points:"

        # Call OpenAI to summarize the transcript        
        response = openai.ChatCompletion.create(
            model=MODEL_TYPE,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": full_text}
            ],
            max_tokens=150
        )
        summary = response.choices[0].message['content'].strip()
        return summary
    except Exception as e:
        st.error(f"Failed to summarize video: {str(e)}")
        return None

def app():
    st.title("YouTube Video Summarizer")
    with st.sidebar:
        st.header("YouTube Summarizer")
        st.write("This is a demo application. It is limited, it requires you to enter your own OpenAI API Key and a YouTube URL. It will not work for longer videos that exceed the token length. For a more rounded application, visit www.clipnote.ai")

    # User inputs
    openai_api_key = st.text_input("Enter your OpenAI API Key:", type="password")
    youtube_url = st.text_input("Enter YouTube video URL:")

    if st.button("Summarize Video"):
        if openai_api_key and youtube_url:
            video_id = get_video_url_id(youtube_url)
            if video_id:
                summary = summarize_video(openai_api_key, video_id)
                if summary:
                    st.subheader("Summary")
                    st.write(summary)
                else:
                    st.write("No summary available.")
        else:
            st.warning("Please provide both an OpenAI API key and a YouTube URL.")

if __name__ == "__main__":
    app()
