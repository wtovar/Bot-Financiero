from fastapi import FastAPI, Form, Response
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# Diccionario con los grupos de URLs
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

def scrape_url(url: str):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=8)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        div_content = soup.find("div", {"id": "historical-desc"})
        if div_content:
            h2_content = div_content.find("h2", {"id": "description"})
            if h2_content:
                return h2_content.get_text(strip=True)
    except Exception as e:
        print(f"Error procesando {url}: {e}")
    return None

def process_category(category_key: str):
    urls = URL_GROUPS.get(category_key, [])
    results = [f"📊 *REPORTE DE {category_key}*\n"]
    
    for url in urls:
        text = scrape_url(url)
        if text:
            results.append(f"• {text}\n")
    
    if len(results) == 1:
        return f"No se pudo obtener información para {category_key} en este momento."
        
    return "\n".join(results)

@app.post("/whatsapp")
async def whatsapp_webhook(Body: str = Form('')):
    command = Body.strip().upper()
    
    if command in URL_GROUPS:
        reply_message = process_category(command)
    elif command == "TODOS":
        all_reports = []
        for cat in URL_GROUPS.keys():
            all_reports.append(process_category(cat))
        reply_message = "\n---\n".join(all_reports)
    else:
        reply_message = (
            "🤖 *Bot Financiero*\n\n"
            "Envía una de las siguientes opciones para recibir el reporte:\n\n"
            "• *FX*\n"
            "• *FIX INCOME*\n"
            "• *COMMODITIES*\n"
            "• *EQUITIES*\n"
            "• *TODOS*"
        )

    # Formatear respuesta en XML TwiML para Twilio
    twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{reply_message}</Message>
</Response>"""

    return Response(content=twiml_response, media_type="application/xml")
