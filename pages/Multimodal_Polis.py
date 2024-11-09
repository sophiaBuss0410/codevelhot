import streamlit as st
import os

from models.openai_client import OpenAIClient
from helpers import read_config, encode_image

config = read_config("config.yaml")

st.title("Multimodal Polis 📈")

def generate_response(model): #, use_tools: bool = False):
    if model == "openai":
        client = OpenAIClient(**config["openai"])
        st.session_state.messages[0]["content"] = config["openai"]["system_prompt"]
        return client.generate(st.session_state.messages) #, use_tools)


def delete_audio_file(audio_filename):
    if os.path.exists(audio_filename):
        os.remove(audio_filename)
        print(f"{audio_filename} has been deleted.")


col_1, col_2, col_3, col_4 = st.columns(4)

with col_1:
    container = st.container(border=True, height=180)

    container.write("2_media_the_of_democracy:  \nDemocracy always tries to postpone solving problems until the next election.")

with col_2:
    container = st.container(border=True, height=180)

    container.write("4_school_students_education_schools:  \nThe educational material of schools should be implemented on the principle of open source code.")

with col_3:
    container = st.container(border=True, height=180)

    container.write("11_society_wellbeing_life_people:  \nPeople lack a hopeful vision of the future.")

with col_4:
    container = st.container(border=True, height=180)

    container.write("23_strike_strikes_right_agreements:  \nThe right to strike belongs to Western democracy.")


col1, col2 = st.columns(2)

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
    # components.iframe("http://localhost:3012/", height=500, scrolling=True)

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
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            messages, stream = generate_response(model) #, use_tools)
            response = st.write_stream(stream)
            st.session_state.messages = messages
        st.session_state.messages.append({"role": "assistant", "content": response})

    if st.button('Clear Chat'):
        st.session_state.messages = [{"role": "system", "content": config["system_prompt"]}]
        st.rerun()

