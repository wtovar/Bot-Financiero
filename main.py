from fastapi import FastAPI, Form, Response
from twilio.twiml.messaging_response import MessagingResponse
import yfinance as yf

app = FastAPI()

SYMBOLS = {
    "FX": {
        "EUR/USD": "EURUSD=X",
        "GBP/USD": "GBPUSD=X",
        "USD/COP": "COP=X",
        "Bitcoin": "BTC-USD"
    },
    "COMMODITIES": {
        "Petroleo WTI": "CL=F",
        "Oro": "GC=F",
        "Cafe": "KC=F"
    },
    "EQUITIES": {
        "S&P 500": "^GSPC",
        "Nasdaq": "^IXIC"
    },
    "FIX INCOME": {
        "US Treasury 10Y": "^TNX"
    }
}

def get_market_data(category_key):
    items = SYMBOLS.get(category_key, {})
    lines = [f"*MERCADO {category_key}*"]
    
    tickers_string = " ".join(items.values())
    try:
        data = yf.Tickers(tickers_string)
        for label, ticker in items.items():
            try:
                price = data.tickers[ticker].fast_info['lastPrice']
                lines.append(f"{label}: {price:,.2f}")
            except Exception:
                lines.append(f"{label}: N/A")
    except Exception as e:
        return f"Error: {e}"

    return "\n".join(lines)

@app.post("/whatsapp")
async def whatsapp_webhook(Body: str = Form('')):
    command = Body.strip().upper()
    
    matched_key = None
    for key in SYMBOLS.keys():
        if key in command:
            matched_key = key
            break
            
    if matched_key:
        reply_text = get_market_data(matched_key)
    else:
        reply_text = "Bot Financiero. Envia: FX, COMMODITIES, EQUITIES o FIX INCOME"

    # Límite ultracorto para evitar fallo de concatenación SMS/WhatsApp
    if len(reply_text) > 300:
        reply_text = reply_text[:290] + "..."

    resp = MessagingResponse()
    resp.message(reply_text)
    
    return Response(content=str(resp), media_type="application/xml")
