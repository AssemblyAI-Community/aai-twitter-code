#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audio-to-Tweet Generator
A simple Streamlit app that generates tweet suggestions from an audio or video file using AssemblyAI's LeMUR.
"""

import os
import tempfile
import streamlit as st
import assemblyai as aai
from dotenv import load_dotenv

load_dotenv()

SUPPORTED_FORMATS = ["mp3", "mp4", "wav", "m4a"]

def main():
    st.title("🐦 Audio-to-Tweet Generator")
    st.write("Upload audio/video to generate tweet suggestions using AI")
    
    uploaded_file = st.file_uploader("Choose an audio/video file", type=SUPPORTED_FORMATS)
    
    if uploaded_file and st.button("Generate Tweets"):
        with st.spinner("Processing... This may take a minute or two."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            try:
                # Transcribe the audio
                transcriber = aai.Transcriber()
                transcript = transcriber.transcribe(tmp_file_path)
                
                # Use LeMUR to generate tweets
                tweet_prompt = """
                Generate 3 catchy, engaging tweets based on the content of this audio.
                Each tweet should:
                - Be under 280 characters
                - Highlight a key insight or quote
                - Include an emoji
                - Be written in a conversational, shareable style
                - End with "#insight" or another relevant hashtag
                
                Format as three numbered tweets.
                """
                
                lemur_response = transcript.lemur.task(tweet_prompt.strip(), final_model=aai.LemurModel.claude3_5_sonnet)
                
                # Display results
                st.subheader("📱 Tweet Suggestions")
                st.write(lemur_response.response)
                
                st.download_button(
                    label="Download Tweets",
                    data=lemur_response.response,
                    file_name="tweet_suggestions.txt",
                    mime="text/plain"
                )
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.info("Make sure your AssemblyAI API key is set correctly and that you've uploaded a valid audio file.")
            finally:
                if os.path.exists(tmp_file_path):
                    os.remove(tmp_file_path)

if __name__ == "__main__":
    main()