# app.py (Versi AI dengan Google Gemini)

import os
import requests
import json
import google.generativeai as genai
from flask import Flask, request

# Inisialisasi aplikasi Flask
app = Flask(__name__)

# --- Konfigurasi Kredensial dari Environment Variables ---
# Sekarang kita tambahkan kunci API untuk Gemini
ACCESS_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Konfigurasi Google Gemini
try:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
    print("Model Gemini berhasil dikonfigurasi.")
except Exception as e:
    print(f"Error saat konfigurasi Gemini: {e}")
    gemini_model = None

# --- Otak Utama Chatbot ---
def main_chatbot_logic(message_text):
    """
    Fungsi ini bertindak sebagai router:
    - Cek apakah pesan adalah perintah khusus.
    - Jika tidak, kirim pesan ke AI untuk dijawab.
    """
    # Cek apakah pesan diawali dengan simbol perintah, misal "/" atau "!"
    if message_text.startswith('/'):
        # Panggil fungsi untuk menangani perintah
        return handle_command(message_text)
    else:
        # Panggil fungsi untuk menghasilkan respons dari AI
        return generate_ai_response(message_text)


def handle_command(command_text):
    """
    Fungsi ini menangani perintah-perintah khusus yang sudah ditentukan.
    """
    command = command_text.lower().strip() # Bersihkan dan ubah ke huruf kecil
    
    if command == '/menu':
        return "Halo! Ini menu layanan dari BSAS:\n\n1. Pembuatan Aplikasi Kustom\n2. Jasa Web Builder\n3. Server Managed\n\nKetik pertanyaanmu untuk detail lebih lanjut!"
    elif command == '/kontak':
        return "Anda dapat menghubungi kami melalui email di admin@bsas.com atau kunjungi website kami di bsas.id."
    elif command == '/promo':
        return "Saat ini sedang ada promo diskon 20% untuk jasa Web Builder. Gunakan kode BSAS20!"
    else:
        return "Maaf, perintah tidak dikenali. Ketik '/menu' untuk melihat daftar layanan."


def generate_ai_response(user_prompt):
    """
    Fungsi ini berinteraksi dengan Gemini API untuk mendapatkan jawaban AI.
    """
    if not gemini_model:
        return "Maaf, layanan AI sedang mengalami gangguan. Silakan coba lagi nanti."
        
    try:
        # --- Kustomisasi Persona AI Anda di Sini ---
        # Anda bisa memberikan instruksi kepada AI agar memiliki kepribadian tertentu.
        system_instruction = "Anda adalah BSAS-BOT, asisten virtual yang ramah, membantu, dan sedikit humoris dari perusahaan teknologi bernama BSAS. Jawab semua pertanyaan pengguna dengan gaya ini."
        
        # Mengirim prompt ke model Gemini
        response = gemini_model.generate_content(
            f"{system_instruction}\n\nPertanyaan Pengguna: {user_prompt}",
            # Konfigurasi keamanan untuk menghindari respons yang tidak pantas
            safety_settings={
                'HARM_CATEGORY_HARASSMENT': 'BLOCK_ONLY_HIGH',
                'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_ONLY_HIGH',
            }
        )
        return response.text
    except Exception as e:
        print(f"Error saat memanggil Gemini API: {e}")
        return "Waduh, sepertinya AI saya sedang butuh istirahat. Coba tanyakan hal lain ya."


# --- Fungsi-Fungsi Teknis (Sama seperti sebelumnya) ---

def send_whatsapp_message(to_number, message_text):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp", "to": to_number,
        "text": { "body": message_text }
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print(f"Pesan balasan terkirim: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Error saat mengirim pesan balasan: {e}")


@app.route('/webhook', methods=['POST'])
def handle_webhook():
    body = request.get_json()
    print("Payload diterima:", json.dumps(body, indent=2))
    try:
        if body.get("object") and body.get("entry"):
            message_info = body['entry'][0]['changes'][0]['value']['messages'][0]
            if 'text' in message_info:
                from_number = message_info['from']
                message_text = message_info['text']['body']
                
                # Panggil otak utama chatbot untuk mendapatkan balasan
                balasan = main_chatbot_logic(message_text)
                send_whatsapp_message(from_number, balasan)
    except Exception as e:
        print(f"Error pada webhook handler: {e}")
    return "OK", 200


@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    if mode == 'subscribe' and token == VERIFY_TOKEN:
        print("WEBHOOK_VERIFIED")
        return challenge, 200
    else:
        return "Forbidden", 403


@app.route('/')
def index():
    return "Server chatbot AI dengan Gemini aktif!", 200