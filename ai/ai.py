#┌─────────────────────────────────────────────────────────────────────┐
#│ ████  █      ███  ████  █      ███     █   █ ████       █     ████  │
#│ █   █ █     █   █ █   █ █     █   █    █   █ █   █     ██         █ │
#│ ████  █     █████ ████  █     █████    █████ ████       █      ███  │
#│ █   █ █     █   █ █   █ █     █   █    █   █ █  █       █         █ │
#│ ████  █████ █   █ ████  █████ █   █    █   █ █   █    █████ █ ████  │
#└─────────────────────────────────────────────────────────────────────┘
# Made by #34Team
# For Post-Tech Hackathon 2026

# Programmer: Alexey Makarenko
# Вы сейчас можете наблюдать в этом коде творение Homo-Sapiens(а) по имени Алексей, Знакомтесь Жана пост ИИ блабла мега супер 2.0!
import os
import re
from pathlib import Path

import requests

from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("AI_API_KEY", "")  # ключ берём из переменной окружения, не из кода
API_URL = "https://apifreellm.com/api/v1/chat"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
THRESHOLD = 0.34  # ниже этого порога считаем, что ответа в базе нет

NO_ANSWER = ("В базе знаний нет надёжной информации по этому вопросу. "
             "Рекомендую обратиться в HR-отдел.")


def _tokens(text: str) -> set:
    # грубая основа слова: первые 5 букв, чтобы «отпуск/отпуска/отпуске» совпадали
    return {w[:5] for w in re.findall(r"\w+", text.lower()) if len(w) > 3}


def _load_kb() -> list:
    chunks = []
    for f in sorted(DATA_DIR.glob("*.txt")):
        for part in re.split(r"\n\s*\n", f.read_text(encoding="utf-8")):
            part = part.strip()
            if part:
                chunks.append({"source": f.name, "title": part.split(".")[0], "text": part, "tokens": _tokens(part)})
    return chunks


KB = _load_kb()


def search(question: str):
    q = _tokens(question)
    if not q:
        return None, 0.0
    best, best_score = None, 0.0
    for c in KB:
        score = len(q & c["tokens"]) / len(q)
        if score > best_score:
            best, best_score = c, score
    return best, best_score


def _ask_llm(context: str, question: str):
    if not API_KEY:
        return None
    prompt = ("Ты HR-ассистент AI Jana. Отвечай ТОЛЬКО на основе фрагмента базы знаний ниже. "
              "Не придумывай правила, не раскрывай персональные данные, не принимай кадровых решений. "
              f"Отвечай коротко.\n\nФрагмент:\n{context}\n\nВопрос сотрудника: {question}")
    try:
        r = requests.post(API_URL, headers={"Authorization": f"Bearer {API_KEY}"},
                          json={"message": prompt}, timeout=20)
        data = r.json()
        if data.get("success"):
            return data["response"]
    except Exception:
        pass
    return None


GREETINGS = {"привет", "здравствуйте", "здравствуй", "салем", "сәлем", "добрый", "hello", "hi", "хай"}
WHO = ("кто ты", "ты ии", "ты ai", "ты бот", "что ты умеешь", "что умеешь")
HELLO = ("Здравствуйте! Я AI Jana, HR-ассистент. Отвечаю на вопросы про отпуск, аванс, "
         "статусы заявок и обучение по базе знаний компании.")


def chat(question: str) -> dict:
    low = question.lower().strip(" !?.")
    words = re.findall(r"\w+", low)
    if any(p in low for p in WHO) or (words and len(words) <= 3 and words[0] in GREETINGS):
        return {"answer": HELLO, "source": None, "escalate": False}
    chunk, score = search(question)
    if chunk is None or score < THRESHOLD:
        return {"answer": NO_ANSWER, "source": None, "escalate": True}
    answer = _ask_llm(chunk["text"], question) or chunk["text"]  # без LLM отдаём сам фрагмент
    return {"answer": answer, "source": f'{chunk["source"]} · {chunk["title"]}', "escalate": False}