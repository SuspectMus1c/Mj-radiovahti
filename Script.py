import os
import requests
from bs4 import BeautifulSoup
import time

# Täydellinen Tampereen / Lempäälän seudun taajuuskartta
TAAJUUDET = {
    "radio nova": "104.7 MHz / 106.2 MHz",
    "hitmix": "99.2 MHz",
    "radio suomipop": "91.0 MHz / 91.6 MHz",
    "ylex": "93.7 MHz",
    "radio rock": "104.2 MHz",
    "loop": "105.6 MHz / 105.9 MHz",
    "kasari": "94.1 MHz",
    "kasari radio": "94.1 MHz",
    "ysäri": "Nettiradio",
    "iskelmä": "103.8 MHz / 100.9 MHz",
    "radio 957": "95.7 MHz",
    "radio city": "88.7 MHz / 97.2 MHz",
    "nrj": "90.0 MHz",
    "basso": "89.6 MHz",
    "suomirock": "107.0 MHz",
    "suomiräp": "96.7 MHz",
    "aito iskelmä": "95.3 MHz",
    "groove fm": "88.7 MHz",
    "helmiradio": "98.3 MHz",
    "tampereen kiakkoradio": "89.0 MHz",
    "pispalan radio": "99.5 MHz",
    "radio dei": "98.8 MHz",
    "radio nostalgia": "92.7 MHz",
    "radio moreeni": "98.4 MHz",
    "yle radio suomi tampere": "99.9 MHz",
    "yle radio suomi": "99.9 MHz",
    "yle radio 1": "90.7 MHz",
    "yle x": "93.7 MHz"
}

def tarkista_radiot():
    url = "https://nytsoi.fi/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Etsitään kaikki kanavarivit NytSoi-sivustolta
        for rivi in soup.find_all('div', class_='channel-row'):
            try:
                kanava_nimi = rivi.find('h3', class_='channel-name').text.strip()
                biisi_info = rivi.find('div', class_='current-song').text.strip()
                
                if " - " in biisi_info:
                    artisti, biisi = biisi_info.split(" - ", 1)
                else:
                    artisti, biisi = biisi_info, ""
                    
                artisti_l = artisti.lower()
                biisi_l = biisi.lower()
                kanava_l = kanava_nimi.lower()
                
                osuma = False
                
                # Bonushälytykset ja Michael Jackson -kriteerit (100% tarkka)
                if "michael jackson" in artisti_l: osuma = True
                elif "jackson 5" in artisti_l: osuma = True
                elif "the jacksons" in artisti_l: osuma = True
                elif "we are the world" in biisi_l: osuma = True
                elif "rockwell" in artisti_l and "somebody" in biisi_l: osuma = True
                
                if osuma:
                    # Jos kanavaa ei löydy taajuuskartasta, käytetään oletustekstiä
                    taajuus = TAAJUUDET.get(kanava_l, "FM-kanava (Tarkista paikallinen taajuus)")
                    laheta_telegram(kanava_nimi, taajuus, artisti, biisi)
            except Exception:
                continue
    except Exception as e:
        print(f"Virhe sivuston lukemisessa: {e}")

def laheta_telegram(kanava, taajuus, artisti, biisi):
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    viesti = f"🕺 🚨 **KUNINGAS SOI RADIOSSA!**\n\n📻 **Kanava:** {kanava}\n📡 **Taajuus Lempäälässä:** {taajuus}\n🎵 **Biisi:** {artisti} - {biisi}"
    
    url = f"https://telegram.org{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": viesti, "parse_mode": "Markdown"}
    
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Virhe Telegram-viestin lähetyksessä: {e}")

if __name__ == "__main__":
    # Ajetaan skripti 5 kertaa minuutin välein (kattamaan GitHub Actionsin 5min cron-rajoitus)
    for i in range(5):
        tarkista_radiot()
        if i < 4:
            time.sleep(60) # Odotetaan 1 minuutti ennen seuraavaa tarkistusta
                
