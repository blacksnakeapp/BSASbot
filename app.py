import os
import requests
from flask import Flask, request

app = Flask(__name__)

# --- GANTI DENGAN DATA ANDA YANG SUDAH DISALIN DARI META ---
ACCESS_TOKEN = "EAAj6b97cT7kBPGXsHOyKW4SK7mUQH6dlgN4p1ijyXzPa6LioBMGMZB9uOQwhel943NAxxPgvdp6kNFAsvtSGB7YaAuoB3xP6e6QQ9iR9OfQIviXnGS4pMRsKcGsPcLSy6iqZAvrYzzTRsYaAI1tsOG0ZBpTlnr7EAkZC3RXZChVJHatJN209FtideFK1J5MXBGhhmWrARvYE4NOTcpD3URJ04ZB8the3rVZBzfJ4wo5ZCXpCbZAsZD"
PHONE_NUMBER_ID = "658039050737312"
VERIFY_TOKEN = "BSASBOT" # Contoh: 'chatbotku123'
# -------------------------------------------------------------

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

def send_whatsapp_message(to_number, message_text):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = { "messaging_product": "whatsapp", "to": to_number, "type": "text", "text": { "body": message_text } }
    response = requests.post(url, headers=headers, json=data)
    print(f"Status Kirim Pesan: {response.status_code}, Response: {response.json()}")

@app.route('/webhook', methods=['POST'])
def handle_message():
    body = request.get_json()
    print("Payload diterima:", body)

    try:
        if body.get("object"):
            message = body['entry'][0]['changes'][0]['value']['messages'][0]
            from_number = message['from']
            message_text = message['text']['body']

            # --- LOGIKA CHATBOT ANDA DIMULAI DI SINI ---
            balasan = f"Anda bilang: '{message_text}'. Saya bot sederhana!"
            if "halo" in message_text.lower():
                balasan = "Halo kembali dari BSAS-BOT GANTENG!"
            if "BSAS" in message_text:
                balasan = "Tentu, kami menyediakan jasa pembuatan Custom App, Web Builder, Server Managed DLL, Anda tertarik yang mana?"
            elif "TONGSOLOP" in message_text:
                balasan = "Oh itu akun live kami tentang Game, kalian bisa follow tiktok kami di https://www.tiktok.com/@tongsolop untuk konten menarik"
            elif "terima kasih" in message_text:
                balasan = "Sama-sama! Senang bisa membantu."
            elif "BLACKAXE" in message_text:
                balasan = "BLACK AXE adalah grup whatsapp kami yang berisi para orang ganteng seperti, Rendy Mambo sang pelor, Danny Cagur sang Play-Lor, Raffles Rooftop sang pengendali Angin, Hans Bara Bere sang dewa Galau dam tentunya Dewa Ular Hitam sang pawang Ular Hitam kecil imut yang lucu, Apakah informasi ini membantu?"
            else:
                balasan = f"Maaf, saya belum mengerti maksud dari '{message_text}'. Coba tanya tentang 'BSAS' atau 'TONGSOLOP' atau 'BLACKAXE'."

            send_whatsapp_message(from_number, balasan)
    except Exception as e:
        print(f"Error: {e}")

    return "OK", 200

if __name__ == '__main__':
    app.run(debug=True)