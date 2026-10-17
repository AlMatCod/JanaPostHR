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

import json
import os
from datetime import date

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

import db
import integrations
from ai import ai
from i18n import tr

db.init()
app = FastAPI(title="Snalma · Jańa Post HR")
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "dev-only-change-me"))
app.mount("/style", StaticFiles(directory="style"), name="style")
templates = Jinja2Templates(directory="templates")

STATUS = {"pending_manager": "На согласовании у руководителя", "pending_hr": "На согласовании в HR",
          "approved": "Одобрена", "rejected": "Отклонена"}
TYPE = {"vacation": "Отпуск", "advance": "Аванс"}
ROLE = {"employee": "Сотрудник", "manager": "Руководитель", "hr": "HR"}


# ---------- вспомогательное ----------
def current_user(request):
    uid = request.session.get("uid")
    if not uid:
        return None
    with db.conn() as c:
        return c.execute("select * from users where id=?", (uid,)).fetchone()


def require_user(request):
    u = current_user(request)
    if not u:
        raise HTTPException(303, headers={"Location": "/"})
    return u


def render(request, name, user=None, **ctx):
    lang = request.session.get("lang", "ru")
    unread = 0
    if user:
        with db.conn() as c:
            unread = c.execute("select count(*) from notifications where user_id=? and is_read=0", (user["id"],)).fetchone()[0]
    ctx.update(user=user, unread=unread, lang=lang, t=lambda k: tr(k, lang),
               STATUS=STATUS, TYPE=TYPE, ROLE=ROLE, page=ctx.get("page", ""))
    return templates.TemplateResponse(request, name, ctx)


def can_view(u, r):
    """Права проверяются на сервере: сотрудник — своё, руководитель — команду, HR — всё."""
    return u["role"] == "hr" or r["user_id"] == u["id"] or (u["role"] == "manager" and r["manager_id"] == u["id"])


def can_decide(u, r):
    return (r["status"] == "pending_manager" and u["role"] == "manager" and r["manager_id"] == u["id"]) or \
           (r["status"] == "pending_hr" and u["role"] == "hr")


REQ_SQL = ("select r.*, e.full_name as emp, e.manager_id from requests r "
           "join users e on e.id=r.user_id ")


# ---------- главная и вход ----------
@app.get("/")
async def home(request: Request):
    u = current_user(request)
    if not u:
        return render(request, "home.html")
    with db.conn() as c:
        boss = c.execute("select full_name from users where id=?", (u["manager_id"],)).fetchone() if u["manager_id"] else None
        reqs = c.execute(REQ_SQL + "where r.user_id=? order by r.id desc limit 3", (u["id"],)).fetchall()
        courses = c.execute("select c.id, c.title, a.progress, a.completed from assignments a "
                            "join courses c on c.id=a.course_id where a.user_id=?", (u["id"],)).fetchall()
        notes = c.execute("select * from notifications where user_id=? order by id desc limit 3", (u["id"],)).fetchall()
        todo = 0
        if u["role"] == "manager":
            todo = c.execute(REQ_SQL + "where r.status='pending_manager' and e.manager_id=?", (u["id"],)).fetchall()
        elif u["role"] == "hr":
            todo = c.execute(REQ_SQL + "where r.status='pending_hr'").fetchall()
    return render(request, "dashboard.html", u, page="/", boss=boss, reqs=reqs, courses=courses,
                  notes=notes, todo=len(todo) if todo else 0)


@app.post("/login")
async def login(request: Request, login: str = Form(...), password: str = Form(...)):
    with db.conn() as c:
        u = c.execute("select * from users where login=? and password=?", (login.strip().lower(), db.hash_pw(password))).fetchone()
    if not u:
        return render(request, "home.html", error="Неверный логин или пароль")
    request.session["uid"] = u["id"]
    return RedirectResponse("/", 303)


@app.get("/logout")
async def logout(request: Request):
    lang = request.session.get("lang", "ru")
    request.session.clear()
    request.session["lang"] = lang
    return RedirectResponse("/", 303)


@app.get("/lang/{code}")
async def set_lang(request: Request, code: str):
    request.session["lang"] = "kz" if code == "kz" else "ru"
    return RedirectResponse(request.headers.get("referer") or "/", 303)


# ---------- заявки ----------
@app.get("/requests")
async def requests_list(request: Request, type: str = "vacation"):
    u = require_user(request)
    sql, args = REQ_SQL, ()
    if u["role"] == "manager":
        sql, args = REQ_SQL + "where r.user_id=? or e.manager_id=? ", (u["id"], u["id"])
    elif u["role"] == "employee":
        sql, args = REQ_SQL + "where r.user_id=? ", (u["id"],)
    with db.conn() as c:
        rows = c.execute(sql + "order by r.id desc", args).fetchall()
    return render(request, "requests.html", u, page="/requests", rows=rows, ptype=type,
                  can_decide=lambda r: can_decide(u, r), today=str(date.today()))


@app.post("/requests")
async def requests_create(request: Request, type: str = Form(...), start_date: str = Form(""),
                          end_date: str = Form(""), amount: str = Form(""), comment: str = Form("")):
    u = require_user(request)
    start = end = None
    amt = None
    if type == "vacation":
        try:
            start, end = date.fromisoformat(start_date), date.fromisoformat(end_date)
        except ValueError:
            raise HTTPException(400, "Укажите даты отпуска")
        days = (end - start).days + 1
        if days < 1 or days > u["leave_days"]:
            raise HTTPException(400, f"Недопустимый период: доступно {u['leave_days']} дн.")
        start, end = str(start), str(end)
    elif type == "advance":
        if not amount.isdigit() or int(amount) <= 0:
            raise HTTPException(400, "Укажите сумму аванса")
        amt = int(amount)
    else:
        raise HTTPException(400, "Неизвестный тип заявки")
    status = "pending_manager" if u["manager_id"] else "pending_hr"
    with db.conn() as c:
        cur = c.execute("insert into requests(user_id,type,start_date,end_date,amount,comment,status,created_at) values(?,?,?,?,?,?,?,?)",
                        (u["id"], type, start, end, amt, comment.strip(), status, db.now()))
        rid = cur.lastrowid
        doc = integrations.documentolog_register(rid, type)  # mock: точка подключения Documentolog
        db.add_history(c, rid, status, u["full_name"], f"Заявка создана. Документооборот (mock): {doc}")
        if u["manager_id"]:
            db.notify(c, u["manager_id"], f"Новая заявка №{rid} от {u['full_name']}", f"/requests/{rid}")
        else:
            for h in c.execute("select id from users where role='hr'").fetchall():
                db.notify(c, h["id"], f"Заявка №{rid} ждёт согласования в HR", f"/requests/{rid}")
        db.notify(c, u["id"], f"Заявка №{rid} создана: {STATUS[status]}", f"/requests/{rid}")
    return RedirectResponse(f"/requests/{rid}", 303)


@app.get("/requests/{rid}")
async def request_card(request: Request, rid: int):
    u = require_user(request)
    with db.conn() as c:
        r = c.execute(REQ_SQL + "where r.id=?", (rid,)).fetchone()
        if not r:
            raise HTTPException(404, "Заявка не найдена")
        if not can_view(u, r):
            raise HTTPException(403, "Нет доступа к этой заявке")
        hist = c.execute("select * from history where request_id=? order by id", (rid,)).fetchall()
    return render(request, "request_card.html", u, page="/requests", r=r, hist=hist, decide=can_decide(u, r))


@app.post("/requests/{rid}/decide")
async def request_decide(request: Request, rid: int, action: str = Form(...), note: str = Form("")):
    u = require_user(request)
    with db.conn() as c:
        r = c.execute(REQ_SQL + "where r.id=?", (rid,)).fetchone()
        if not r:
            raise HTTPException(404)
        if action not in ("approve", "reject") or not can_decide(u, r):
            raise HTTPException(403, "Нет прав на это действие")
        new = "rejected" if action == "reject" else ("pending_hr" if r["status"] == "pending_manager" else "approved")
        c.execute("update requests set status=? where id=?", (new, rid))
        db.add_history(c, rid, new, u["full_name"], note.strip() or ("Отклонено" if new == "rejected" else "Согласовано"))
        if new == "approved" and r["type"] == "vacation":
            days = (date.fromisoformat(r["end_date"]) - date.fromisoformat(r["start_date"])).days + 1
            c.execute("update users set leave_days=leave_days-? where id=?", (days, r["user_id"]))
        if new == "pending_hr":
            for h in c.execute("select id from users where role='hr'").fetchall():
                db.notify(c, h["id"], f"Заявка №{rid} ждёт согласования в HR", f"/requests/{rid}")
        db.notify(c, r["user_id"], f"Заявка №{rid}: {STATUS[new]}", f"/requests/{rid}")
    return RedirectResponse(f"/requests/{rid}", 303)


# ---------- Jana Academy ----------
@app.get("/academy")
async def academy(request: Request):
    u = require_user(request)
    with db.conn() as c:
        rows = c.execute("select c.*, a.progress, a.score, a.completed from assignments a "
                         "join courses c on c.id=a.course_id where a.user_id=?", (u["id"],)).fetchall()
    return render(request, "academy.html", u, page="/academy", rows=rows)


def _assignment(c, u, cid):
    a = c.execute("select * from assignments where user_id=? and course_id=?", (u["id"], cid)).fetchone()
    if not a:
        raise HTTPException(403, "Курс вам не назначен")
    return a


@app.get("/academy/{cid}")
async def course(request: Request, cid: int):
    u = require_user(request)
    with db.conn() as c:
        a = _assignment(c, u, cid)
        co = c.execute("select * from courses where id=?", (cid,)).fetchone()
        if a["progress"] < 50:
            c.execute("update assignments set progress=50 where user_id=? and course_id=?", (u["id"], cid))
            a = _assignment(c, u, cid)
    return render(request, "course.html", u, page="/academy", co=co, a=a, quiz=json.loads(co["quiz"]))


@app.post("/academy/{cid}/quiz")
async def course_quiz(request: Request, cid: int):
    u = require_user(request)
    form = await request.form()
    with db.conn() as c:
        _assignment(c, u, cid)
        co = c.execute("select * from courses where id=?", (cid,)).fetchone()
        quiz = json.loads(co["quiz"])
        ok = sum(1 for i, q in enumerate(quiz) if form.get(f"q{i}") == str(q["a"]))
        score = round(100 * ok / len(quiz))
        done = 1 if score >= 60 else 0
        c.execute("update assignments set score=?, completed=?, progress=? where user_id=? and course_id=?",
                  (score, done, 100 if done else 50, u["id"], cid))
        if done:
            db.notify(c, u["id"], f"Курс «{co['title']}» завершён: {score}%", f"/academy/{cid}")
    return RedirectResponse(f"/academy/{cid}", 303)


# ---------- уведомления ----------
@app.get("/notifications")
async def notifications(request: Request):
    u = require_user(request)
    with db.conn() as c:
        rows = c.execute("select * from notifications where user_id=? order by id desc", (u["id"],)).fetchall()
        c.execute("update notifications set is_read=1 where user_id=?", (u["id"],))
    return render(request, "notifications.html", u, page="/notifications", rows=rows)


# ---------- AI Jana ----------
@app.get("/ai")
async def ai_page(request: Request):
    u = require_user(request)
    return render(request, "ai.html", u, page="/ai")


@app.post("/api/ai")
async def ai_ask(request: Request):
    u = current_user(request)
    if not u:
        return JSONResponse({"error": "Требуется вход"}, 401)
    question = ((await request.json()).get("question") or "").strip()[:500]
    if not question:
        return JSONResponse({"answer": "Напишите вопрос.", "source": None, "escalate": False})
    # защита чужих данных: вопросы про конкретных сотрудников ассистент не обрабатывает
    with db.conn() as c:
        names = c.execute("select full_name from users where id != ?", (u["id"],)).fetchall()
    low = question.lower()
    if any(p.lower() in low for n in names for p in n["full_name"].split() if len(p) > 3):
        return {"answer": "Я не раскрываю данные других сотрудников. Могу ответить на общие HR-вопросы.",
                "source": None, "escalate": False}
    return await run_in_threadpool(ai.chat, question)


# Привета я бедни программист и я закончил в 23:13 писать это 🔥