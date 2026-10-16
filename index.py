# Snalma #0.1
# Made by #34Team
#Supperted by IST

# Programmer: Alexey Makarenko

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import snail
from ai import ai

snail.test()
print("Hi! its start of great project")


app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def home():
    return f"""
    <html>
        <head>
           <title>Snalma HR</title>
           <body style="font-family: Arial;">
        </head>

        <header>
         <h1>Добро пожаловать в Сналма HR! 🐌</h1>
        </header>
        <head>
            <p>Единая цифровая платформа для сотрудников.</p>  
            <a>{ai.chat("hello")}</a>
        </head>
        <footer>
          <h3>Все права наверно защищены Snalma 2026</h3>
        </footer>
        </body>
    </html>
    """
