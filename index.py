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
           <title> Jańa Post HR</title>
           <link rel="icon" type="image/png" href="/style/logo.png">
           <link rel="stylesheet" href="/style/style.css">
           <style>@import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:ital,wght@0,200..900;1,200..900&display=swap');</style>
        </head>
        <body>
         <header style="background-color: white; color: white; padding: 20px 30px; display: flex; align-items: center; justify-content: space-between;">
          <h1 style="color: #008C00; margin: 0;">Jańa Post HR</h1>
          <img src="/style/logo.png" width="120" alt="Logo">
         </header>
         
         <main style="padding: 20px;">
              
            <h1 style="color: black; font-weight: 1000;">Простой HR для всех</h1>
            <p style="text-align: center;">{ai.chat("test")}</p>
         </main>
         
         <footer style="background-color: black; color: white; padding: 30px;">
          <h3 style="color: white; ">Все права наверно защищены Snalma 2026</h3>
         </footer>
        </body>
    </html>
    """
