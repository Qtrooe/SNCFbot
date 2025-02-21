import os
import requests
import time
import logging
from datetime import datetime
from telegram import Bot
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# 🔹 Configuration via variables d'environnement
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SNCF_API_KEY = os.getenv("SNCF_API_KEY")

# 🔹 Liste des trains à surveiller
TRAIN_NUMBERS = ['872633', '872603', '872701']

# 🔹 Configuration du logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 🔹 Fonction pour obtenir la date du jour (format AAAAMMJJ)
def get_today_date():
    return datetime.now().strftime('%Y%m%d')

# 🔹 URL API SNCF correcte pour un train donné
def get_train_url(train_number):
    return f"https://api.sncf.com/v1/coverage/sncf/vehicle_journeys/{train_number}"

# 🔹 Vérifier l'état du train
def check_train_status(train_number):
    today_date = get_today_date()
    url = get_train_url(train_number)
    
    try:
        response = requests.get(url, headers={"Authorization": f"Bearer {SNCF_API_KEY}"}, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Erreur API SNCF pour le train {train_number} : {e}")
        return None

    # Vérifie si le train est trouvé
    if "vehicle_journeys" not in data or not data["vehicle_journeys"]:
        logging.warning(f"Train {train_number} non trouvé !")
        return None

    train = data["vehicle_journeys"][0]
    status = "✅ A l'heure"

    # Vérifie s'il y a des perturbations globales
    if "disruptions" in data and data["disruptions"]:
        for disruption in data["disruptions"]:
            if train_number in str(disruption):  # Vérifie si le train est impacté
                status = f"⚠️ {disruption['severity'].capitalize()} : {disruption['cause']}"

    message = f"🚆 **Train {train_number} ({today_date})**\n📍 Statut : {status}"
    logging.info(message)

    return message

# 🔹 Envoyer une alerte Telegram
def send_telegram_alert(message):
    if TELEGRAM_TOKEN and CHAT_ID:
        try:
            bot = Bot(token=TELEGRAM_TOKEN)
            bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")
            logging.info("✅ Notification envoyée avec succès")
        except Exception as e:
            logging.error(f"Erreur envoi Telegram : {e}")
    else:
        logging.error("⚠️ Erreur : Clés API non trouvées")

# 🔹 Boucle principale avec gestion du délai
def main():
    logging.info("🚀 Démarrage du bot SNCF...")

    while True:
        for train_number in TRAIN_NUMBERS:
            message = check_train_status(train_number)
            if message:
                send_telegram_alert(message)
            
            time.sleep(120)  # Attendre 2 minutes entre chaque train
        
        logging.info("⏳ Attente avant la prochaine vérification...")
        time.sleep(600)  # Vérifie toutes les 10 minutes

if __name__ == "__main__":
    main()
