# Snalma #0.1
# Made by #34Team
#Supperted by IST

# Programmer: Alexey Makarenko

import snail

snail.test()
print("Hi! its start of great project")

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def home():
    # Вот так Python может прямо в коде отдать кусок HTML
    return """
    <html>
        <head><title>Сналма HR</title></head>
        <body style="font-family: Arial;">
            <h1>Добро пожаловать в Сналма HR! 🐌</h1>
            <p>Единая цифровая платформа для сотрудников.</p>
            <a href="/profile">Перейти в профиль</a>
        </body>
    </html>
    """
