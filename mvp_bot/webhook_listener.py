from flask import Flask, request, jsonify
import subprocess
import os
from dotenv import load_dotenv, dotenv_values

app = Flask(__name__)

# Esetleg titkos kulcs beállítása (ha használtál titkosítást a webhook beállításánál)
load_dotenv()
SECRET = os.getenv("SECRET")  # csak akkor szükséges, ha titkos kulcsot használsz

@app.route('/webhook', methods=['POST'])
def webhook():
    # Ellenőrizd a titkos kulcsot, ha beállítottad
    if request.headers.get('X-Hub-Signature') != SECRET:
        return jsonify({'message': 'Unauthorized'}), 401

    # Git pull parancs
    try:
        # A repó helye
        os.chdir('root/MVP/')  # cseréld le a repó helyére
        subprocess.run(['git', 'pull', 'origin', 'main'], check=True)  # Cseréld le 'main'-re, ha másik ágat használsz

        # (Opció) A Discord bot újraindítása
        subprocess.run(['systemctl', 'restart', 'discord-bot'], check=True)

        return jsonify({'message': 'Success'}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
