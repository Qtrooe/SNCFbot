import os
import requests
import time
from datetime import datetime
from telegram import Bot
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# 🔹 Configuration via variables d'environnement
TELEGRAM_TOKEN =7227192058:AAGGV7RszhDZ2nx55SdKSu_sepWcc8480sw
CHAT_ID = 5112294865
SNCF_API_KEY = ee585a7f-fd4a-4740-a007-18539990488b


# 🔹 Liste des trains à surveiller
TRAIN_NUMBERS = ['872633', '872603', '872701']

# 🔹 Fonction pour obtenir la date du jour (format AAAAMMJJ)
def get_today_date():
    return datetime.now().strftime('%Y%m%d')

# 🔹 URL API SNCF (structure corrigée)
def get_train_url(train_number, date):
    return f"https://api.sncf.com/v1/coverage/sncf/vehicle_journeys?datetime={date}T000000"

# 🔹 Vérifier l'état du train
def check_train_status(train_number):
    today_date = get_today_date()
    url = get_train_url(train_number, today_date)
    
    try:
        response = requests.get(url, headers={"Authorization": f"Bearer {SNCF_API_KEY}"}, timeout=10)
        response.raise_for_status()  # Vérifie si la requête est correcte
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erreur API SNCF : {e}")
        return None

    if not data.get("vehicle_journeys"):
        print(f"Train {train_number} non trouvé !")
        return None

    train = data["vehicle_journeys"][0]
    status = "A l'heure"

    if "disruptions" in train and train["disruptions"]:
        status = f"⚠️ Perturbé : {train['disruptions'][0]['severity']}"

    return f"🚆 Train {train_number} ({today_date})\nStatut : {status}"

# 🔹 Envoyer une alerte Telegram
def send_telegram_alert(message):
    if TELEGRAM_TOKEN and CHAT_ID:
        try:
            bot = Bot(token=TELEGRAM_TOKEN)
            bot.send_message(chat_id=CHAT_ID, text=message)
        except Exception as e:
            print(f"Erreur envoi Telegram : {e}")
    else:
        print("⚠️ Erreur : Clés API non trouvées")

# 🔹 Boucle principale avec vérification plus fréquente
def main():
    while True:
        for train_number in TRAIN_NUMBERS:
            message = check_train_status(train_number)
            if message:
                send_telegram_alert(message)
        
        time.sleep(600)  # Vérifie toutes les 10 minutes

if __name__ == "__main__":
    main()
