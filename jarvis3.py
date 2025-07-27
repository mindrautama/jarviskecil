# jarvis.py

# Impor yang sudah ada
import os
# Mengganti ChatGoogleGenerativeAI dengan ChatOpenAI untuk model OpenAI
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
# LLMChain sudah deprecated, jadi kita tidak lagi mengimpornya
# from langchain.chains import LLMChain 

# Impor baru untuk Speech-to-Text
import speech_recognition as sr

# Impor baru untuk Eleven Labs Text-to-Speech
import requests # Pastikan Anda sudah menginstal requests: pip install requests
import playsound # Pastikan Anda sudah menginstal playsound: pip install playsound

# --- Konfigurasi OpenAI (pastikan kunci API Anda disetel sebagai variabel lingkungan) ---
# os.environ["OPENAI_API_KEY"] = "sk-YOUR_OPENAI_API_KEY_HERE" # HANYA JIKA TIDAK MENGGUNAKAN VARIABEL LINGKUNGAN

# Ganti dengan kunci API OpenAI Anda yang sebenarnya
os.environ["OPENAI_API_KEY"] = "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"

# Menghapus konfigurasi GOOGLE_API_KEY karena tidak lagi menggunakan Gemini
# GOOGLE_API_KEY = "AIzaSyCwkLCQbIHCw444tXnzBwELtgwu5OoPOqQ" 

# Menggunakan ChatOpenAI untuk model GPT-4.0
llm = ChatOpenAI(temperature=0.7, model_name="gpt-4")

# --- Konfigurasi Eleven Labs ---
# Dapatkan API Key Anda dari Eleven Labs (https://elevenlabs.io/)
# Anda bisa menyimpannya sebagai variabel lingkungan atau menggantinya langsung di sini.
# Contoh: os.environ.get("ELEVEN_LABS_API_KEY")
ELEVEN_LABS_API_KEY = "sk_dd25eabdcf9066155dfeaa1d43bf6437c51022dc81f4d152" # GANTI DENGAN KUNCI API ELEVEN LABS ANDA

# ID suara laki-laki dari Eleven Labs. Anda bisa menemukan lebih banyak di dashboard Eleven Labs.
# Contoh ID suara laki-laki: "21m00Tcm4TlvDq8ikWAM" (Adam), "pNInz6obpgDQGXGN6ie5" (Antoni)
# Pilih ID suara yang paling Anda suka dari daftar suara di Eleven Labs.
VOICE_ID = "l88WmPeLH7L0O0VA9lqm" # GANTI DENGAN ID SUARA LAKI-LAKI PILIHAN ANDA

# URL endpoint Eleven Labs Text-to-Speech
ELEVEN_LABS_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

# --- Template untuk LLM ---
template = """
{pertanyaan}
"""
prompt = PromptTemplate(template=template, input_variables=["pertanyaan"])

# --- Mengganti LLMChain dengan sintaks LangChain terbaru (prompt | llm) ---
llm_chain = prompt | llm

# --- Fungsi untuk Menerima Input Suara ---
def get_audio_input():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Dengarkan...")
        r.pause_threshold = 1 # jeda singkat untuk memastikan kalimat selesai diucapkan
        audio = r.listen(source)

    try:
        print("Mengenali suara...")
        # Menggunakan bahasa Indonesia untuk pengenalan suara
        text = r.recognize_google(audio, language="id-ID")
        print(f"Anda berkata: {text}")
        return text
    except sr.UnknownValueError:
        print("Maaf, tidak dapat mengenali suara Anda.")
        return ""
    except sr.RequestError as e:
        print(f"Maaf, ada masalah dengan layanan pengenalan suara; {e}")
        return ""

# --- Fungsi untuk Mengubah Teks Menjadi Suara Menggunakan Eleven Labs dan Memutarnya ---
def speak(text):
    print(f"Jarvis menjawab: {text}")
    audio_file = "response.mp3"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVEN_LABS_API_KEY
    }

    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2", # Model yang mendukung berbagai bahasa, termasuk Indonesia
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }

    try:
        response = requests.post(ELEVEN_LABS_URL, headers=headers, json=data)
        response.raise_for_status() # Akan memunculkan HTTPError untuk status kode 4xx/5xx

        with open(audio_file, 'wb') as f:
            f.write(response.content)

        playsound.playsound(audio_file)
        os.remove(audio_file) # Hapus file audio setelah diputar
    except requests.exceptions.RequestException as e:
        print(f"Terjadi kesalahan saat memanggil Eleven Labs API: {e}")
        print("Pastikan ELEVEN_LABS_API_KEY Anda benar dan Anda memiliki koneksi internet.")
        if "401 Client Error" in str(e):
            print("Kesalahan otentikasi. Periksa kembali ELEVEN_LABS_API_KEY Anda.")
        elif "400 Client Error" in str(e):
            print("Permintaan tidak valid. Pastikan VOICE_ID dan model_id benar.")
    except Exception as e:
        print(f"Terjadi kesalahan saat memutar suara: {e}")
        print(f"Detail kesalahan: {e}")
        # Pesan tambahan jika playsound bermasalah
        print("Jika Anda mengalami masalah pemutaran, pastikan playsound terinstal dengan benar dan sistem Anda dapat memutar file MP3.")


# --- Main Program ---
if __name__ == "__main__":
    # Sambutan awal dalam Bahasa Indonesia
    speak("Halo, saya Jarvis. Ada yang bisa saya bantu?")

    while True: # Loop agar Jarvis bisa terus menerima pertanyaan
        print("\nSiap menerima pertanyaan (ucapkan 'berhenti' untuk keluar).")
        user_input_text = get_audio_input()

        if user_input_text.lower() == "berhenti":
            speak("Terima kasih, Jarvis berhenti.")
            break
        elif user_input_text: # Hanya proses jika ada teks yang dikenali
            # Menggunakan .invoke() pada chain baru
            # Untuk ChatOpenAI, responsnya adalah objek AIMessage, jadi kita perlu mengakses .content
            response = llm_chain.invoke({"pertanyaan": user_input_text})
            speak(response.content) # Jarvis merespons dengan suara
        else:
            speak("Silakan coba lagi.")
