# Snalma #0.1
# Made by #34Team
#Supperted by IST

# Programmer: Alexey Makarenko

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import snail
from ai import ai

snail.test()
print("Hi! its start of great project")


app = FastAPI()
app.mount("/style", StaticFiles(directory="style"), name="style")

@app.get("/", response_class=HTMLResponse)
async def home():
    return f"""
    <html>
        <head>
           <title>Snalma HR</title>
           <link rel="icon" type="image/png" href="logo2.png">
           <link rel="stylesheet" href="style/style.css">
        </head>
        <body>
         <header style="background-color: #c90e07; color; white; padding: 30px;">
          <style></style>
          <h1>Добро пожаловать в Snalma-HR! 🐌</h1>
         </header>
         <head>
            <p>Единая цифровая платформа для сотрудников.</p>  
            <a>{ai.chat("test")}</a>
         </head>
         <footer style="background-color: #c90e07; color; white; padding: 30px;">
          <h3>Все права наверно защищены Snalma 2026</h3>
         </footer>
        </body>
    </html>
    """
