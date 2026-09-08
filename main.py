from fastapi import FastAPI, Form, Response
from twilio.twiml.messaging_response import MessagingResponse
import yfinance as yf

app = FastAPI()

SYMBOLS = {
    "FX": {
        "EUR/USD": "EURUSD=X",
        "GBP/USD": "GBPUSD=X",
        "USD/JPY": "JPY=X",
        "USD/COP": "COP=X",
        "USD/MXN": "MXN=X",
        "Bitcoin": "BTC-USD"
    },
    "COMMODITIES": {
        "Petróleo WTI": "CL=F",
        "Oro": "GC=F",
        "Cobre": "HG=F",
        "Café": "KC=F"
    },
    "EQUITIES": {
        "S&P 500": "^GSPC",
        "Dow Jones": "^DJI",
        "Nasdaq": "^IXIC",
        "Bovespa": "^BVSP"
    },
    "FIX INCOME": {
        "US Treasury 10Y": "^TNX",
        "US Treasury 30Y": "^TYX"
    }
}

def get_market_data(category_key):
    items = SYMBOLS.get(category_key, {})
    results = [f"📊 *MERCADO {category_key}*\n"]
    
    tickers_string = " ".join(items.values())
    try:
        data = yf.Tickers(tickers_string)
        for label, ticker in items.items():
            try:
                price = data.tickers[ticker].fast_info['lastPrice']
                results.append(f"• *{label}*: {price:,.2f}")
            except Exception:
                results.append(f"• *{label}*: No disponible")
    except Exception as e:
        return f"Error al consultar datos: {e}"

    return "\n".join(results)

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
        reply_text = (
            "🤖 *Bot Financiero*\n\n"
            "Opciones:\n"
            "• FX\n"
            "• COMMODITIES\n"
            "• EQUITIES\n"
            "• FIX INCOME"
        )

    # CORTE DE SEGURIDAD ABSOLUTO (Máximo 800 caracteres)
    if len(reply_text) > 800:
        reply_text = reply_text[:750] + "\n\n...(texto recortado)"

    resp = MessagingResponse()
    resp.message(reply_text)
    return Response(content=str(resp), media_type="application/xml")
