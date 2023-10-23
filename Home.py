import streamlit as st
import wave
import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd
import pyaudio

FRAMES_PER_BUFFER = 3200
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 16000


st.set_page_config(
    page_title="Audio Speech Analysis"
)


st.title("Audio Speech Analysis")

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

if "my_input" not in st.session_state:
    st.session_state["my_input"] = ""


st.sidebar.header("Record Audio")
my_input = st.sidebar.text_input(
    "Input File Name", st.session_state["my_input"])
submit = st.sidebar.button("Submit")

if submit:
    st.session_state["my_input"] = my_input

    p = pyaudio.PyAudio()

    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=FRAMES_PER_BUFFER

    )

    seconds = 5
    frames = []
    for i in range(0, int(RATE/FRAMES_PER_BUFFER*seconds)):
        data = stream.read(FRAMES_PER_BUFFER)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    obj = wave.open(my_input, "wb")
    obj.setnchannels(CHANNELS)
    obj.setsampwidth(p.get_sample_size(FORMAT))
    obj.setframerate(RATE)
    obj.writeframes(b"".join(frames))
    obj.close()


st.sidebar.header("Upload Audio")
audio_file = st.sidebar.file_uploader("", type=["wav"])


def voice_analysis():
    if audio_file is not None:

        obj = wave.open(audio_file, 'rb')

        sample_freq = obj.getframerate()
        frames = obj.getnframes()
        signal_wave = obj.readframes(-1)
        num_channels = obj.getnchannels()
        sample_width = obj.getsampwidth()

        obj.close()

        time = frames / sample_freq
        audio_array = np.frombuffer(signal_wave, dtype=np.int32)
        times = np.linspace(0, time, num=frames)

        fig, ax = plt.subplots(figsize=(8, 4))  # Adjust the figure size here
        ax.plot(times, audio_array)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amplitude")
        st.pyplot(fig)

        if st.button("Play Audio"):
            sd.play(audio_array, sample_freq)
            sd.wait()

        st.header("Parameters")
        col1, col2, col3 = st.columns(3)
        col1.metric("Number of Frequencies", int(sample_freq / 2))
        col2.metric("Peak Amplitude", np.max(np.abs(audio_array)))
        col3.metric("Average Amplitude", np.mean(np.abs(audio_array)))
        col1.metric("Number of Channels", num_channels)
        col2.metric("Frame Rate(Hz)", sample_freq)
        col3.metric("Number of Frames", frames)


voice_analysis()
