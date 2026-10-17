import hashlib
import json
import sqlite3
from datetime import date, datetime, timedelta

DB = "snalma.db"


def conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c


def hash_pw(p: str) -> str:
    # демо-соль; для продакшена: уникальная соль на пользователя
    return hashlib.pbkdf2_hmac("sha256", p.encode(), b"snalma-demo", 100_000).hex()


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def notify(c, user_id, text, link="/"):
    c.execute("insert into notifications(user_id,text,link,is_read,at) values(?,?,?,0,?)", (user_id, text, link, now()))


def add_history(c, rid, status, actor, note=""):
    c.execute("insert into history(request_id,status,actor,note,at) values(?,?,?,?,?)", (rid, status, actor, note, now()))


SCHEMA = """
create table if not exists users(id integer primary key, login text unique, password text, full_name text, role text,
  company text, position text, department text, manager_id integer, hire_date text, leave_days integer);
create table if not exists requests(id integer primary key, user_id integer, type text, start_date text, end_date text,
  amount integer, comment text, status text, created_at text);
create table if not exists history(id integer primary key, request_id integer, status text, actor text, note text, at text);
create table if not exists notifications(id integer primary key, user_id integer, text text, link text, is_read integer, at text);
create table if not exists courses(id integer primary key, title text, description text, material text, quiz text);
create table if not exists assignments(user_id integer, course_id integer, progress integer, score integer, completed integer,
  primary key(user_id, course_id));
"""

COURSES = [
    (1, "Охрана труда и техника безопасности", "Базовый курс для всех сотрудников склада и офиса.",
     "Перед началом работы осмотрите рабочее место и убедитесь, что проходы свободны.\n"
     "Тяжёлые грузы поднимают вдвоём или с помощью тележки.\n"
     "О любой травме или опасной ситуации сообщайте руководителю сразу.\n"
     "Эвакуационные выходы нельзя загромождать.",
     [{"q": "Что делать при обнаружении опасной ситуации?", "o": ["Сообщить руководителю", "Подождать до конца смены", "Решить самому"], "a": 0},
      {"q": "Как переносить тяжёлые грузы?", "o": ["В одиночку", "Вдвоём или тележкой", "Бегом"], "a": 1},
      {"q": "Можно ли загромождать эвакуационные выходы?", "o": ["Да", "Только на время", "Нет"], "a": 2}]),
    (2, "Знакомство с Jańa Post", "Миссия, ценности и устройство компании.",
     "Jańa Post — IT-логистическая компания, которая доставляет отправления между Китаем и странами Центральной Азии.\n"
     "Три ценности компании: открытость, надёжность и результат.\n"
     "У компании более 1000 филиалов и собственная IT-платформа.",
     [{"q": "Между какими регионами работает компания?", "o": ["Китай и Центральная Азия", "Европа и США", "Только Казахстан"], "a": 0},
      {"q": "Какая из этих ценностей относится к компании?", "o": ["Скорость любой ценой", "Надёжность", "Конкуренция"], "a": 1},
      {"q": "Что есть у компании кроме филиалов?", "o": ["Собственная IT-платформа", "Только call-центр", "Ничего"], "a": 0}]),
]


def init():
    with conn() as c:
        c.executescript(SCHEMA)
        if c.execute("select count(*) from users").fetchone()[0]:
            return
        pw = hash_pw("demo123")  # тестовые аккаунты, реальных данных нет
        users = [
            (1, "marat", pw, "Марат Сериков", "manager", "Jańa Post", "Руководитель отдела логистики", "Логистика", None, "2019-03-11", 24),
            (2, "aigerim", pw, "Айгерим Нурланова", "employee", "Jańa Post", "Специалист по обработке заказов", "Логистика", 1, "2022-06-01", 18),
            (3, "erlan", pw, "Ерлан Касымов", "employee", "Jańa Post", "Оператор склада", "Логистика", 1, "2023-09-15", 24),
            (4, "dana", pw, "Дана Ахметова", "hr", "Jańa Post", "HR-менеджер", "HR", None, "2020-01-20", 24),
        ]
        c.executemany("insert into users values(?,?,?,?,?,?,?,?,?,?,?)", users)
        for co in COURSES:
            c.execute("insert into courses values(?,?,?,?,?)", (*co[:4], json.dumps(co[4], ensure_ascii=False)))
        c.executemany("insert into assignments values(?,?,?,?,?)",
                      [(2, 1, 50, None, 0), (2, 2, 0, None, 0), (3, 1, 0, None, 0), (1, 2, 0, None, 0)])
        d = date.today()
        rows = [
            (1, 2, "vacation", str(d - timedelta(60)), str(d - timedelta(50)), None, "Семейные обстоятельства", "approved"),
            (2, 2, "advance", None, None, 150000, "На оплату обучения", "pending_manager"),
            (3, 3, "vacation", str(d + timedelta(30)), str(d + timedelta(36)), None, "", "pending_hr"),
        ]
        for r in rows:
            c.execute("insert into requests values(?,?,?,?,?,?,?,?,?)", (*r, now()))
            add_history(c, r[0], "pending_manager", "Система", "Заявка создана")
        add_history(c, 1, "pending_hr", "Марат Сериков", "Согласовано руководителем")
        add_history(c, 1, "approved", "Дана Ахметова", "Согласовано HR")
        add_history(c, 3, "pending_hr", "Марат Сериков", "Согласовано руководителем")
        notify(c, 2, "Вам назначен курс «Охрана труда и техника безопасности»", "/academy/1")
        notify(c, 2, "Вам назначен курс «Знакомство с Jańa Post»", "/academy/2")
        notify(c, 3, "Вам назначен курс «Охрана труда и техника безопасности»", "/academy/1")
        notify(c, 1, "Вам назначен курс «Знакомство с Jańa Post»", "/academy/2")
        notify(c, 4, "Заявка №3 ждёт согласования в HR", "/requests/3")
