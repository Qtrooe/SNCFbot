
import requests
import time
from datetime import datetime
from telegram import Bot

# 🔹 Remplis tes informations de configuration
TELEGRAM_TOKEN =  "7227192058:AAGGV7RszhDZ2nx55SdKSu_sepWcc8480sw" #Mets ton vrai token ici
CHAT_ID = "5112294865"  # Ton chat ID Telegram
SNCF_API_KEY = "ee585a7f-fd4a-4740-a007-18539990488b"  # Mets ta clé API SNCF

# 🔹 Liste des numéros de trains à suivre (ajoute ici tes 3 trains)
TRAIN_NUMBERS = ['872633', '872603', '872701']  # Remplace par les numéros des 3 trains

# 🔹 Fonction pour obtenir la date du jour au format AAAAMMJJ
def get_today_date():
    return datetime.now().strftime('%Y%m%d')  # Format AAAAMMJJ

# 🔹 URL de l'API SNCF pour obtenir les informations du train
def get_train_url(train_number, date):
    return f"https://api.sncf.com/v1/coverage/sncf/vehicle_journeys?filter=vehicle_journey.id={train_number}&datetime={date}T000000"

# 🔹 Fonction pour vérifier l'état du train
def check_train_status(train_number):
    today_date = get_today_date()  # Obtenir la date du jour
    url = get_train_url(train_number, today_date)  # Mettre à jour l'URL avec la date du jour
    
    response = requests.get(url, headers={"Authorization": f"Bearer {SNCF_API_KEY}"})
    if response.status_code != 200:
        print(f"Erreur API SNCF pour le train {train_number} :", response.text)
        return None
    
    data = response.json()
    
    if not data.get("vehicle_journeys"):
        print(f"Train {train_number} non trouvé !")
        return None
    
    train = data["vehicle_journeys"][0]
    status = "A l'heure"  # Par défaut, le train est à l'heure
    
    # Vérifier s'il y a une perturbation
    if "disruptions" in train and train["disruptions"]:
        status = f"Perturbé : {train['disruptions'][0]['severity']}"
    
    return f"🚆 Train {train_number} ({today_date})\nStatut : {status}"

# 🔹 Fonction pour envoyer une notification sur Telegram
def send_telegram_alert(message):
    bot = Bot(token=TELEGRAM_TOKEN)
    bot.send_message(chat_id=CHAT_ID, text=message)

# 🔹 Fonction principale pour faire tourner le bot et vérifier tous les trains chaque jour
def main():
    while True:
        # Vérifier l'état de chaque train
        for train_number in TRAIN_NUMBERS:
            message = check_train_status(train_number)
            if message:
                send_telegram_alert(message)
        
        time.sleep(86400)  # Vérifier tous les jours (86400 secondes = 24 heures)

if __name__ == "__main__":
    main()