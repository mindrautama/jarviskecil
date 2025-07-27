# jarvis.py

# Impor yang sudah ada
import os
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
# LLMChain sudah deprecated, jadi kita tidak lagi mengimpornya
# from langchain.chains import LLMChain 

# Impor baru untuk Speech-to-Text
import speech_recognition as sr

# Impor baru untuk Eleven Labs Text-to-Speech
import requests # Pastikan Anda sudah menginstal requests: pip install requests
import playsound # Pastikan Anda sudah menginstal playsound: pip install playsound

# Impor baru untuk Supabase
from supabase import create_client, Client # Pastikan Anda sudah menginstal supabase: pip install supabase

# Impor baru untuk membuka browser
import webbrowser # Modul bawaan Python untuk membuka browser

# --- Konfigurasi OpenAI (pastikan kunci API Anda disetel sebagai variabel lingkungan) ---
# os.environ["OPENAI_API_KEY"] = "sk-YOUR_OPENAI_API_KEY_HERE" # HANYA JIKA TIDAK MENGGUNAKAN VARIABEL LINGKUNGAN

# Ganti dengan kunci API OpenAI Anda yang sebenarnya
os.environ["OPENAI_API_KEY"] = "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"

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

# --- Konfigurasi Supabase ---
# Dapatkan URL dan Kunci Anon Supabase Anda dari pengaturan proyek Supabase Anda.
SUPABASE_URL = "https://gvtgrmxkmjhgavvbvtxv.supabase.co" # GANTI DENGAN URL SUPABASE ANDA
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd2dGdybXhrbWpoZ2F2dmJ2dHh2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI4NDE5NzksImV4cCI6MjA2ODQxNzk3OX0.jAOe_HYnNAx86p_U2SS--T-moFd63hT2sQureDlI--A" # GANTI DENGAN ANON KEY SUPABASE ANDA

supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Define allowed Supabase tables ---
# PENTING: Ganti ini dengan nama tabel yang sebenarnya di database Supabase Anda.
# Pastikan nama-nama ini persis sama dengan nama tabel Supabase Anda (case-sensitive jika berlaku di DB Anda).
ALLOWED_TABLES = ["text_metrics", "karyawan", "chart_data", "dashboards","metrics"] 

# --- Template untuk LLM ---
template = """
Anda adalah Jarvis, asisten AI. Jawab pertanyaan pengguna.
Jika pengguna meminta data atau informasi dari tabel tertentu, coba ambil dari data Supabase yang disediakan.
Jika tidak ada data yang relevan ditemukan atau tabel tidak dikenal, nyatakan bahwa Anda tidak dapat menemukan data atau mengakses tabel tersebut.
Jika pengguna meminta untuk membuka browser atau mencari sesuatu di internet, gunakan fungsi open_browser.
Jika pengguna meminta untuk membuka Microsoft Excel, gunakan fungsi open_excel.

Pertanyaan pengguna: {pertanyaan}

Data Supabase (jika tersedia):
{supabase_data}
"""
prompt = PromptTemplate(template=template, input_variables=["pertanyaan", "supabase_data"])

# --- Mengganti LLMChain dengan sintaks LangChain terbaru (prompt | llm) ---
llm_chain = prompt | llm

# --- Fungsi untuk Menerima Input Suara ---
def get_audio_input():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Mendengarkan...")
        r.pause_threshold = 1 # jeda singkat untuk memastikan kalimat selesai diucapkan
        audio = r.listen(source)

    try:
        print("Mengenali suara...")
        # Menggunakan Bahasa Indonesia untuk pengenalan suara
        text = r.recognize_google(audio, language="id-ID")
        print(f"Anda berkata: {text}")
        return text
    except sr.UnknownValueError:
        print("Maaf, saya tidak dapat memahami audio Anda.")
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
        "model_id": "eleven_multilingual_v2", # Model mendukung berbagai bahasa, termasuk Bahasa Indonesia
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
            print("Kesalahan otentikasi. Harap periksa kembali ELEVEN_LABS_API_KEY Anda.")
        elif "400 Client Error" in str(e):
            print("Permintaan tidak valid. Harap pastikan VOICE_ID dan model_id benar.")
    except Exception as e:
        print(f"Terjadi kesalahan saat menghasilkan atau memutar audio: {e}")
        print(f"Detail kesalahan: {e}")
        # Pesan tambahan jika playsound bermasalah
        print("Jika Anda mengalami masalah pemutaran, pastikan playsound terinstal dengan benar dan sistem Anda dapat memutar file MP3.")

# --- Fungsi untuk Mengambil Data dari Supabase ---
def get_data_from_supabase(table_name: str, limit: int = 10) -> str:
    """
    Mengambil data dari tabel Supabase yang ditentukan.
    Mengembalikan string yang diformat dari data yang diambil.
    """
    try:
        # Periksa apakah tabel yang diminta ada dalam daftar yang diizinkan
        if table_name.lower() not in [t.lower() for t in ALLOWED_TABLES]:
            return f"Saya tidak dapat mengakses data dari tabel '{table_name}' karena tidak ada dalam daftar yang diizinkan. Harap minta data dari salah satu tabel ini: {', '.join(ALLOWED_TABLES)}.\n"

        # Mengambil semua kolom dari tabel yang ditentukan, membatasi jumlah baris.
        response = supabase_client.from_(table_name).select("*").limit(limit).execute()
        data = response.data
        if data:
            # Memformat data menjadi string yang mudah dibaca untuk LLM
            formatted_data = "\n".join([str(row) for row in data])
            return f"Berikut adalah data yang relevan dari tabel '{table_name}':\n{formatted_data}\n"
        else:
            return f"Tidak ada data ditemukan di tabel '{table_name}'.\n"
    except Exception as e:
        return f"Terjadi kesalahan saat mengambil data dari Supabase: {e}\n"

# --- Fungsi untuk Membuka Browser ---
def open_browser(query: str = ""):
    """
    Membuka browser web dengan URL pencarian Google untuk kueri yang diberikan.
    Jika tidak ada kueri, akan membuka halaman utama Google.
    """
    if query:
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        speak(f"Membuka browser untuk mencari {query}.")
    else:
        search_url = "https://www.google.com"
        speak("Membuka browser web.")
    
    try:
        webbrowser.open(search_url)
    except Exception as e:
        speak(f"Maaf, saya tidak dapat membuka browser: {e}")

# --- Fungsi untuk Membuka Microsoft Excel ---
def open_excel():
    """
    Membuka aplikasi Microsoft Excel.
    """
    speak("Membuka Microsoft Excel.")
    try:
        # Pada Windows, 'excel.exe' biasanya ada di PATH atau dapat diakses langsung.
        # Jika ini tidak berfungsi, Anda mungkin perlu memberikan jalur lengkap,
        # misalnya: r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE"
        os.startfile("excel.exe") 
    except FileNotFoundError:
        speak("Maaf, aplikasi Microsoft Excel tidak ditemukan di sistem Anda.")
    except Exception as e:
        speak(f"Maaf, saya tidak dapat membuka Excel: {e}")


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
            # Logika untuk mendeteksi niat membuka Microsoft Excel
            if "buka excel" in user_input_text.lower() or \
               "buka microsoft excel" in user_input_text.lower():
                open_excel()
                continue # Lanjut ke iterasi berikutnya setelah membuka Excel

            # Logika untuk mendeteksi niat membuka browser
            if "buka browser" in user_input_text.lower() or \
               "cari di internet" in user_input_text.lower() or \
               "buka google" in user_input_text.lower():
                
                # Ekstrak kueri pencarian jika ada
                query_parts = user_input_text.lower().split("cari di internet")
                if len(query_parts) > 1:
                    search_query = query_parts[1].strip()
                else:
                    query_parts = user_input_text.lower().split("buka browser untuk")
                    if len(query_parts) > 1:
                        search_query = query_parts[1].strip()
                    else:
                        search_query = "" # Tidak ada kueri spesifik

                open_browser(search_query)
                continue # Lanjut ke iterasi berikutnya setelah membuka browser

            supabase_data_for_llm = ""
            detected_table = None

            # Logika untuk mendeteksi nama tabel dalam kueri pengguna
            # Prioritaskan kecocokan persis atau frasa umum
            for table in ALLOWED_TABLES:
                # Periksa nama tabel yang persis atau frasa "data dari <nama_tabel>"
                if table.lower() in user_input_text.lower() or \
                   f"data dari {table.lower()}" in user_input_text.lower():
                    detected_table = table
                    break
            
            if detected_table:
                print(f"Terdeteksi permintaan data dari tabel: {detected_table}")
                # Batasi hingga 10 baris untuk menghindari membanjiri LLM dengan terlalu banyak data
                supabase_data_for_llm = get_data_from_supabase(detected_table, limit=10) 
            elif "data" in user_input_text.lower() or \
                 "informasi" in user_input_text.lower() or \
                 "database" in user_input_text.lower():
                # Jika permintaan data umum tetapi tidak ada tabel spesifik, informasikan kepada pengguna
                supabase_data_for_llm = f"Harap tentukan tabel mana yang Anda inginkan datanya. Tabel yang dapat saya akses adalah: {', '.join(ALLOWED_TABLES)}.\n"
                print(f"Permintaan data umum, meminta pengguna untuk nama tabel.")

            # Gabungkan data Supabase (jika ada) dengan pertanyaan pengguna ke dalam prompt LLM
            # Template sekarang secara eksplisit menyertakan placeholder untuk supabase_data
            response = llm_chain.invoke({"pertanyaan": user_input_text, "supabase_data": supabase_data_for_llm})
            
            speak(response.content) # Jarvis merespons dengan suara
        else:
            speak("Harap coba lagi.")
