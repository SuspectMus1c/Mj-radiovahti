import os
import requests
from bs4 import BeautifulSoup

# Täydellinen Lempäälän / Pirkanmaan taajuuskartta
TAAJUUDET = {
    "radio nova": "106.2 MHz",
    "hitmix": "99.2 MHz",
    "radio suomipop": "104.1 MHz",
    "ylex": "92.7 MHz",
    "radio rock": "92.2 MHz",
    "loop": "105.9 MHz",
    "kasari": "94.1 MHz",
    "iskelmä": "95.0 MHz / 100.9 MHz",
    "radio 957": "95.7 MHz",
    "radio city": "104.9 MHz",
    "nrj": "101.6 MHz",
    "basso": "103.1 MHz",
    "suomirock": "107.0 MHz",
    "suomiräp": "96.7 MHz",
    "aito iskelmä": "107.4 MHz",
    "groove fm": "90.0 MHz",
    "helmiradio": "98.3 MHz",
    "yle radio suomi tampere": "99.9 MHz",
    "yle radio 1": "88.3 MHz",
    "ysäri": "Nettiradio (Bauer Media)",
    "kasari radio": "94.1 MHz"
}

def tarkista_radiot():
    url = "https://nytsoi.fi/"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Käydään läpi kaikki sivuston kanavat
        for rivi in soup.find_all('div', class_='channel-row'):
            try:
                kanava_nimi = rivi.find('h3', class_='channel-name').text.strip()
                biisi_info = rivi.find('div', class_='current-song').text.strip()
                
                if " - " in biisi_info:
                    artisti, biisi = biisi_info.split(" - ", 1)
                else:
                    artisti, biisi = biisi_info, ""
                    
                artisti_lower = artisti.lower()
                biisi_lower = biisi.lower()
                kanava_lower = kanava_nimi.lower()
                
                osuma = False
                
                # 100% Tarkat hälytyskriteerit:
                if "michael jackson" in artisti_lower: osuma = True
                elif "jackson 5" in artisti_lower: osuma = True
                elif "the jacksons" in artisti_lower: osuma = True
                elif "we are the world" in biisi_lower: osuma = True
                elif "rockwell" in artisti_lower and "somebody" in biisi_lower: osuma = True
                
                if osuma:
                    # Haetaan taajuus kartasta, jos ei löydy niin käytetään oletusta
                    taajuus = TAAJUUDET.get(kanava_lower, "FM-kanava (Tarkista taajuus)")
                    laheta_telegram(kanava_nimi, taajuus, artisti, biisi)
            except Exception:
                continue
    except Exception as e:
        print(f"Virhe haussa: {e}")

def laheta_telegram(kanava, taajuus, artisti, biisi):
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    viesti = f"🕺 🚨 **KUNINGAS SOI RADIOSSA!**\n\n📻 **Kanava:** {kanava}\n📡 **Taajuus Lempäälässä:** {taajuus}\n🎵 **Biisi:** {artisti} - {biisi}"
    
    url = f"https://telegram.org{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": viesti, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

if __name__ == "__main__":
    tarkista_radiot()
