from fastapi import FastAPI, Form, Response
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

@app.post("/whatsapp")
async def whatsapp_webhook(Body: str = Form('')):
    command = Body.strip().upper()
    
    matched_key = None
    for key in SYMBOLS.keys():
        if key in command:
            matched_key = key
            break
            
    if matched_key:
        items = SYMBOLS[matched_key]
        lines = [f"*MERCADO {matched_key}*"]
        tickers_str = " ".join(items.values())
        try:
            data = yf.Tickers(tickers_str)
            for label, ticker in items.items():
                try:
                    price = data.tickers[ticker].fast_info['lastPrice']
                    lines.append(f"• {label}: {price:,.2f}")
                except Exception:
                    lines.append(f"• {label}: N/A")
        except Exception as e:
            lines.append(f"Error: {e}")
        reply_text = "\n".join(lines)
    else:
        reply_text = "Bot Financiero Activo. Opciones: FX, COMMODITIES, EQUITIES, FIX INCOME"

    # XML TwiML ultra limpio sin saltos extra
    twiml = f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{reply_text}</Message></Response>'
    return Response(content=twiml, media_type="application/xml")
