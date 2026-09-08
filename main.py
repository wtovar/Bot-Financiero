from fastapi import FastAPI, Form, Response
import yfinance as yf

app = FastAPI()

SYMBOLS = {
    "FX": {"EUR/USD": "EURUSD=X", "USD/COP": "COP=X", "Bitcoin": "BTC-USD"},
    "COMMODITIES": {"Petroleo": "CL=F", "Oro": "GC=F"},
    "EQUITIES": {"S&P 500": "^GSPC", "Nasdaq": "^IXIC"},
    "FIX INCOME": {"US 10Y": "^TNX"}
}

@app.post("/whatsapp")
async def whatsapp_webhook(Body: str = Form('')):
    cmd = Body.strip().upper()
    
    selected_key = next((k for k in SYMBOLS.keys() if k in cmd), None)
    
    if selected_key:
        items = SYMBOLS[selected_key]
        lines = [f"MERCADO {selected_key}:"]
        try:
            tickers = " ".join(items.values())
            data = yf.Tickers(tickers)
            for label, ticker in items.items():
                p = data.tickers[ticker].fast_info['lastPrice']
                lines.append(f"- {label}: {p:,.2f}")
        except Exception:
            lines.append("- Datos no disponibles")
        txt = "\n".join(lines)
    else:
        txt = "Bot Financiero. Responde: FX, COMMODITIES, EQUITIES o FIX INCOME"

    # Forzar TwiML plano sin saltos ni espacios extra
    xml_data = f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{txt}</Message></Response>'
    return Response(content=xml_data, media_type="application/xml")
