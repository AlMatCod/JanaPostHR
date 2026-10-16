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
           <link rel="icon" type="image/png" href="/style/logo2.png">
           <link rel="stylesheet" href="/style/style.css">
           <style>@import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:ital,wght@0,200..900;1,200..900&display=swap');</style>
        </head>
        <body>
         <header style="background-color: #008C00; color: white; padding: 20px 30px; display: flex; align-items: center; justify-content: space-between;">
          <h1 style="margin: 0;">Добро пожаловать в Snalma-HR!</h1>
          <img src="/style/logo2.png" width="120" alt="Logo">
         </header>
         
         <main style="padding: 20px;">
            <p>Единая цифровая платформа для сотрудников.</p>  
            <span class="text-h1">Мы доставляем возможности</span>
            <p>{ai.chat("test")}</p>
         </main>
         
         <footer style="background-color: #008C00; color: white; padding: 30px;">
          <h3>Все права наверно защищены Snalma 2026</h3>
         </footer>
        </body>
    </html>
    """
