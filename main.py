from fastapi import FastAPI, Form, Response
import yfinance as yf

app = FastAPI()

# Mapeo de símbolos financieros reales
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
        "US Treasury 30Y": "^TYX",
        "US Treasury 5Y": "^FVX"
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
        return f"Error consultando mercado: {e}"

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
        reply = get_market_data(matched_key)
    else:
        reply = (
            "🤖 *Bot Financiero*\n\n"
            "Envía una de las siguientes opciones:\n\n"
            "• *FX*\n"
            "• *COMMODITIES*\n"
            "• *EQUITIES*\n"
            "• *FIX INCOME*"
        )

    twiml = f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{reply}</Message></Response>'
    return Response(content=twiml, media_type="application/xml")
