from fastapi import FastAPI, Form, Response
import requests
from bs4 import BeautifulSoup
import concurrent.futures

app = FastAPI()

URL_GROUPS = {
    "FX": [
        "https://tradingeconomics.com/united-states/currency",
        "https://tradingeconomics.com/euro-area/currency",
        "https://tradingeconomics.com/united-kingdom/currency",
        "https://tradingeconomics.com/japan/currency",
        "https://tradingeconomics.com/canada/currency",
        "https://tradingeconomics.com/mexico/currency",
        "https://tradingeconomics.com/brazil/currency",
        "https://tradingeconomics.com/chile/currency",
        "https://tradingeconomics.com/china/currency",
        "https://tradingeconomics.com/btcusd:cur",
        "https://tradingeconomics.com/ethusd:cur"
    ],
    "FIX INCOME": [
        "https://tradingeconomics.com/china/government-bond-yield",
        "https://tradingeconomics.com/india/government-bond-yield",
        "https://tradingeconomics.com/chile/government-bond-yield",
        "https://tradingeconomics.com/mexico/government-bond-yield",
        "https://tradingeconomics.com/brazil/government-bond-yield",
        "https://tradingeconomics.com/colombia/government-bond-yield",
        "https://tradingeconomics.com/canada/government-bond-yield",
        "https://tradingeconomics.com/united-states/government-bond-yield",
        "https://tradingeconomics.com/germany/government-bond-yield",
        "https://tradingeconomics.com/france/government-bond-yield",
        "https://tradingeconomics.com/italy/government-bond-yield",
        "https://tradingeconomics.com/spain/government-bond-yield",
        "https://tradingeconomics.com/united-kingdom/government-bond-yield"
    ],
    "COMMODITIES": [
        "https://tradingeconomics.com/commodity/crude-oil",
        "https://tradingeconomics.com/commodity/brent-crude-oil",
        "https://tradingeconomics.com/commodity/natural-gas",
        "https://tradingeconomics.com/commodity/gold",
        "https://tradingeconomics.com/commodity/copper",
        "https://tradingeconomics.com/commodity/wheat",
        "https://tradingeconomics.com/commodity/coffee",
        "https://tradingeconomics.com/commodity/sugar",
        "https://tradingeconomics.com/commodity/corn",
        "https://tradingeconomics.com/commodity/beef",
        "https://tradingeconomics.com/commodity/aluminum",
        "https://tradingeconomics.com/commodity/nickel",
        "https://tradingeconomics.com/commodity/crb"
    ],
    "EQUITIES": [
        "https://tradingeconomics.com/united-states/stock-market",
        "https://tradingeconomics.com/indu:ind",
        "https://tradingeconomics.com/us100:ind",
        "https://tradingeconomics.com/japan/stock-market",
        "https://tradingeconomics.com/united-kingdom/stock-market",
        "https://tradingeconomics.com/euro-area/stock-market",
        "https://tradingeconomics.com/germany/stock-market",
        "https://tradingeconomics.com/france/stock-market",
        "https://tradingeconomics.com/italy/stock-market",
        "https://tradingeconomics.com/spain/stock-market",
        "https://tradingeconomics.com/china/stock-market",
        "https://tradingeconomics.com/shsz300:ind",
        "https://tradingeconomics.com/india/stock-market",
        "https://tradingeconomics.com/hong-kong/stock-market",
        "https://tradingeconomics.com/taiwan/stock-market",
        "https://tradingeconomics.com/canada/stock-market",
        "https://tradingeconomics.com/brazil/stock-market",
        "https://tradingeconomics.com/mexico/stock-market",
        "https://tradingeconomics.com/argentina/stock-market",
        "https://tradingeconomics.com/colombia/stock-market",
        "https://tradingeconomics.com/chile/stock-market"
    ]
}

def fetch_data(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(url, headers=headers, timeout=2.5)
        if res.status_code == 200:
            soup = BeautifulSoup(res.content, "html.parser")
            div = soup.find("div", {"id": "historical-desc"})
            if div:
                h2 = div.find("h2", {"id": "description"})
                if h2:
                    return h2.get_text(strip=True)
    except Exception:
        pass
    return None

def process_category(category_key):
    urls = URL_GROUPS.get(category_key, [])[:5]  # Muestra los primeros 5 por velocidad
    results = [f"📊 *REPORTE {category_key}*\n"]
    
    # Procesa todas las páginas al mismo tiempo en paralelo
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        scraped_texts = list(executor.map(fetch_data, urls))
        
    for text in scraped_texts:
        if text:
            results.append(f"• {text}\n")
            
    if len(results) == 1:
        return f"No se pudo obtener información de {category_key} en este momento."
        
    return "\n".join(results)

@app.post("/whatsapp")
async def whatsapp_webhook(Body: str = Form('')):
    command = Body.strip().upper()
    
    selected_key = None
    for key in URL_GROUPS.keys():
        if key in command:
            selected_key = key
            break
            
    if selected_key:
        reply = process_category(selected_key)
    else:
        reply = (
            "🤖 *Bot Financiero*\n\n"
            "Envía una de las siguientes opciones para recibir el reporte:\n\n"
            "• *FX*\n"
            "• *FIX INCOME*\n"
            "• *COMMODITIES*\n"
            "• *EQUITIES*"
        )

    twiml = f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{reply}</Message></Response>'
    return Response(content=twiml, media_type="application/xml")
