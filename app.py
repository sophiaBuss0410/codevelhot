import streamlit as st
from PIL import Image
import atexit
import os

from models.openai_client import OpenAIClient
from helpers import read_config, encode_image

config = read_config("config.yaml")

st.set_page_config(
    page_title="CodeVelhot Junction 2024",
    page_icon="🚀",
    layout= "wide",
    )

st.title("Zero friction: CodeVelhot Junction 2024 ✨")

container = st.container(border=True)

col_1, col_2, col_3, col_4 = st.columns(4)

with col_1:
    container = st.container(border=True)
    container.write("Topic 1: This is inside the container")

with col_2:
    container = st.container(border=True)
    container.write("Topic 2: This is inside the container")

with col_3:
    container = st.container(border=True)
    container.write("Topic 3: This is inside the container")

with col_4:
    container = st.container(border=True)
    container.write("Topic 4: This is inside the container")


col1, col2 = st.columns(2)

########### Side Bar  ##################
# use_tools = st.sidebar.checkbox("Enable Function Call")
model = st.sidebar.radio(
    "Please choose the AI model.",
    ["openai"],
    captions = ["gpt-4o-mini"]
)

image_path = st.sidebar.file_uploader("Upload Image 🚀", type=["png","jpg","bmp","jpeg"])
if image_path is not None:
    image =Image.open(image_path)
    st.sidebar.image(image_path, caption="Uploaded Image", use_column_width=True)


if st.sidebar.button('Clear Chat'):
    st.session_state.messages = [{"role": "system", "content": config["system_prompt"]}]
    st.rerun()

############################################    

def generate_response(model): #, use_tools: bool = False):
    if model == "openai":
        client = OpenAIClient(**config["openai"])
        st.session_state.messages[0]["content"] = config["openai"]["system_prompt"]
        return client.generate(st.session_state.messages) #, use_tools)


def delete_audio_file(audio_filename):
    if os.path.exists(audio_filename):
        os.remove(audio_filename)
        print(f"{audio_filename} has been deleted.")

with col1:
    audio_value = st.audio_input("Record your statement.")

    if audio_value is not None:
        st.audio(audio_value)
        with open("recording/recorded_audio.wav", "wb") as f:
            f.write(audio_value.getbuffer())
        
        st.success("Audio file has been saved as 'recorded_audio.wav'")

    # if st.sidebar.button('Clear Recording'):
    #     atexit.register(delete_audio_file(audio_filename="recording/recorded_audio.wav"))

with col2:
    components.iframe("http://localhost:3012/", height=500, scrolling=True)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [ {"role": "system", "content": config["system_prompt"]}]

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        if not isinstance(message, dict):
            continue
        if message["role"] == "user" or message["role"] == "assistant":
            with st.chat_message(message["role"]):
                if isinstance(message["content"], str):
                    st.markdown(message["content"])
                elif isinstance(message["content"], list):
                    st.markdown(message["content"][0]["text"])

    if prompt := st.chat_input("write your message here..."):
        if image_path is not None:
                base64_image = encode_image(image_path)
                st.session_state.messages.append({"role": "user", "content": [{
                    "type": "text",
                    "text": prompt
                    },
                    {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }]})
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            messages, stream = generate_response(model) #, use_tools)
            response = st.write_stream(stream)
            st.session_state.messages = messages
        st.session_state.messages.append({"role": "assistant", "content": response})
