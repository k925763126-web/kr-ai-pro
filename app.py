import streamlit as st
import requests
import pyttsx3
import serial
import time
from streamlit_mic_recorder import speech_to_text

# --- ARDUINO BAĞLANTISI ---
arduino_port = "/dev/cu.usbmodem206EF1334D682" # Kendi portunla değiştir!
try:
    if 'arduino' not in st.session_state:
        st.session_state.arduino = serial.Serial(port=arduino_port, baudrate=115200, timeout=0.1)
except:
    st.session_state.arduino = None

# --- SES MOTORU ---
engine = pyttsx3.init()
def speak_and_animate(text):
    if st.session_state.arduino:
        st.session_state.arduino.write(b'T') # Arduino'ya 'Talk' sinyali
    engine.say(text)
    engine.runAndWait()

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Kr AI", layout="centered")
st.title("👑 Kr AI: Hibrit Asistan")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "processing" not in st.session_state:
    st.session_state.processing = False

# Sidebar: Sohbeti Temizle
with st.sidebar:
    if st.button("Sohbeti Sıfırla"):
        st.session_state.messages = []
        st.session_state.processing = False
        st.rerun()

# Eski Mesajları Göster
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- GİRİŞ ALANI (YAZI + SES) ---
if not st.session_state.processing:
    col1, col2 = st.columns([1, 4])
    
    with col1:
        # Mikrofon Girişi
        voice_input = speech_to_text(language='tr', start_prompt="🎙️", stop_prompt="🛑", key='stt')
    
    with col2:
        # Klavye Girişi
        text_input = st.chat_input("Kr AI'ya bir şeyler yazın...")

    # Eğer herhangi bir giriş varsa (Ses veya Yazı)
    user_query = voice_input if voice_input else text_input

    if user_query:
        st.session_state.processing = True
        st.session_state.messages.append({"role": "user", "content": user_query})
        st.rerun()

# --- YANIT MANTIĞI ---
if st.session_state.processing:
    with st.chat_message("assistant"):
        with st.spinner("Kr AI yanıtlıyor..."):
            try:
                url = "http://localhost:11434/api/chat"
                payload = {
                    "model": "llama3",
                    "messages": [{"role": "system", "content": "Sen Kr AI'sın. Türkçe ve kısa cevaplar ver."}] + st.session_state.messages,
                    "stream": False
                }
                response = requests.post(url, json=payload)
                ans = response.json()['message']['content']
                
                st.markdown(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
                
                # Sesli yanıt ve Arduino hareketi
                speak_and_animate(ans)
                
            except Exception as e:
                st.error(f"Hata: {e}")
    
    st.session_state.processing = False
    time.sleep(0.5)
    st.rerun()