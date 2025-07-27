# jarvis.py

# Impor yang sudah ada
import os
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Impor baru untuk Speech-to-Text
import speech_recognition as sr

# --- Konfigurasi OpenAI (pastikan kunci API Anda disetel sebagai variabel lingkungan) ---
# os.environ["OPENAI_API_KEY"] = "sk-YOUR_OPENAI_API_KEY_HERE" # HANYA JIKA TIDAK MENGGUNAKAN VARIABEL LINGKUNGAN

os.environ["OPENAI_API_KEY"] = "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" # Ganti dengan kunci API Anda yang sebenarnya
from langchain_openai import OpenAI

llm = OpenAI(temperature=0.7)

# --- Template untuk LLM ---
template = """
{pertanyaan}
"""
prompt = PromptTemplate(template=template, input_variables=["pertanyaan"])
llm_chain = LLMChain(prompt=prompt, llm=llm)

# --- Fungsi untuk Menerima Input Suara ---
def get_audio_input():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Dengarkan...")
        r.pause_threshold = 1 # jeda singkat untuk memastikan kalimat selesai diucapkan
        audio = r.listen(source)

    try:
        print("Mengenali suara...")
        # Anda bisa memilih bahasa di sini, misalnya language="id-ID" untuk Bahasa Indonesia
        text = r.recognize_google(audio, language="id-ID")
        print(f"Anda berkata: {text}")
        return text
    except sr.UnknownValueError:
        print("Maaf, tidak dapat mengenali suara Anda.")
        return ""
    except sr.RequestError as e:
        print(f"Maaf, ada masalah dengan layanan pengenalan suara; {e}")
        return ""

# --- Main Program ---
if __name__ == "__main__":
    while True: # Loop agar Jarvis bisa terus menerima pertanyaan
        print("\nSiap menerima pertanyaan (ucapkan 'berhenti' untuk keluar).")
        user_input_text = get_audio_input()

        if user_input_text.lower() == "berhenti":
            print("Terima kasih, Jarvis berhenti.")
            break
        elif user_input_text: # Hanya proses jika ada teks yang dikenali
            response = llm_chain.run(user_input_text)
            print(f"Jarvis menjawab: {response}")
        else:
            print("Silakan coba lagi.")