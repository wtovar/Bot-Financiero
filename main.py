from fastapi import FastAPI, Form, Response
import yfinance as yf

app = FastAPI()

@app.post("/whatsapp")
async def whatsapp_webhook(Body: str = Form('')):
    command = Body.strip().upper()
    
    # Evaluación del comando
    if "FX" in command:
        try:
            # Consultamos un solo activo para probar velocidad
            ticker = yf.Ticker("COP=X")
            precio = ticker.fast_info['lastPrice']
            mensaje = f"💵 *USD/COP*: ${precio:,.2f} COP"
        except Exception as e:
            mensaje = f"⚠️ Error consultando precio: {e}"
    else:
        mensaje = "🤖 *Bot Financiero*\n\nEscribe *FX* para ver el precio del Dólar."

    # TwiML directo
    twiml = f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{mensaje}</Message></Response>'
    return Response(content=twiml, media_type="application/xml")
