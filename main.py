from fastapi import FastAPI, Form, Response

app = FastAPI()

@app.post("/whatsapp")
async def whatsapp_webhook(Body: str = Form('')):
    # Respuesta ultra simple en TwiML
    twiml_response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>¡Hola! Tu bot financiero está conectado correctamente. 🚀</Message>
</Response>"""
    return Response(content=twiml_response, media_type="text/xml")
