from fastapi import FastAPI, Form, Response
import requests
from bs4 import BeautifulSoup

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

def scrape_url(url: str):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=3)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            div_content = soup.find("div", {"id": "historical-desc"})
            if div_content:
                h2_content = div_content.find("h2", {"id": "description"})
                if h2_content:
                    return h2_content.get_text(strip=True)
    except Exception:
        pass
    return None

def process_category(category_key: str):
    urls = URL_GROUPS.get(category_key, [])[:4] # Limita a las primeras 4 URLs para no exceder tiempo
    results = [f"📊 *REPORTE DE {category_key}*\n"]
    
    for url in urls:
        text = scrape_url(url)
        if text:
            results.append(f"• {text}\n")
    
    if len(results) == 1:
        return f"Procesando solicitud de {category_key}... intenta de nuevo en unos segundos."
        
    return "\n".join(results)

@app.post("/whatsapp")
async def whatsapp_webhook(Body: str = Form('')):
    command = Body.strip().upper()
    
    matched_key = None
    for key in URL_GROUPS.keys():
        if key in command:
            matched_key = key
            break
            
    if matched_key:
        reply_message = process_category(matched_key)
    elif "TODOS" in command:
        all_reports = [process_category(cat) for cat in URL_GROUPS.keys()]
        reply_message = "\n---\n".join(all_reports)
    else:
        reply_message = (
            "🤖 *Bot Financiero Activado*\n\n"
            "Responde con uno de los siguientes temas:\n"
            "• FX\n"
            "• COMMODITIES\n"
            "• EQUITIES\n"
            "• FIX INCOME"
        )

    twiml_response = f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{reply_message}</Message></Response>'
    return Response(content=twiml_response, media_type="application/xml")
