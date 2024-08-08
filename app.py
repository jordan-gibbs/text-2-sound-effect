import streamlit as st
from elevenlabs.client import ElevenLabs
import concurrent.futures
import zipfile
import os

# Initialize ElevenLabs client
api_key = os.getenv("ELEVENLABS_API_KEY")
elevenlabs = ElevenLabs(api_key=api_key)

def generate_sound_effect(text: str, output_path: str):
    result = elevenlabs.text_to_sound_effects.convert(
        text=text,
        # duration_seconds=10,  # Optional, can be adjusted
        prompt_influence=0.3,  # Optional, can be adjusted
    )

    with open(output_path, "wb") as f:
        for chunk in result:
            f.write(chunk)


def create_zip(file_paths):
    zip_path = "all_sounds.zip"
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for file in file_paths:
            zipf.write(file, os.path.basename(file))
    return zip_path


# Streamlit app

# Streamlit app
st.set_page_config(
    page_title="Sound Effect Generator",
    page_icon="🔊",  # You can choose any emoji as the icon
    layout="wide",
    initial_sidebar_state="auto",
)

with open("style.css") as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

hide_streamlit_style = """
            <style>
            #root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 0rem;}
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("🔊 Sound Effect Generator")
st.markdown("###### Text-to-sound effect - type in any prompt to generate sounds.")
prompt = st.text_input("Enter a prompt for the sound effect:")
num_generations = st.slider("Number of generations", 1, 10, 3)

# Session state to keep track of generated files
if "generated_files" not in st.session_state:
    st.session_state.generated_files = []

if st.button("Generate Sound"):
    if len(prompt) > 200:
        st.warning("Prompt exceeds 200 characters. Please shorten your prompt.")
    elif prompt:
        output_paths = [f"{prompt}_{i+1}.mp3" for i in range(num_generations)]
        st.session_state.generated_files = output_paths
        
        with st.spinner(""):
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(generate_sound_effect, prompt, path) for path in output_paths]
                concurrent.futures.wait(futures)

# Display the audio files and download buttons
for path in st.session_state.generated_files:
    audio_file = open(path, "rb")
    audio_bytes = audio_file.read()
    col1, col2 = st.columns([9, 1])
    with col1:
        st.audio(audio_bytes, format="audio/mp3")
    with col2:
        st.download_button(
            label="⬇️",
            data=audio_bytes,
            file_name=path,
            mime="audio/mp3"
        )

if st.session_state.generated_files:
    zip_path = create_zip(st.session_state.generated_files)
    with open(zip_path, "rb") as zip_file:
        st.download_button(
            label="Download All",
            data=zip_file,
            file_name=zip_path,
            mime="application/zip"
        )
