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
# Tyt krch ya testiroval versii saita
# RU/KZ: словарь интерфейса. Новые тексты добавляются сюда, остальной код не меняется
T = {
    "ru": {
        "nav_home": "Кабинет", "nav_requests": "Заявки", "nav_academy": "Jana Academy",
        "nav_ai": "AI Jana", "nav_notifications": "Уведомления", "login": "Войти", "logout": "Выйти",
        "hero_title": "Простой HR для всех",
        "hero_sub": "Профиль, заявки, обучение и ответы HR в одном месте. Войдите, чтобы начать.",
        "profile": "Профиль", "leave_left": "Остаток отпуска", "days": "дн.",
        "my_requests": "Мои заявки", "new_request": "Новая заявка", "my_courses": "Моё обучение",
        "services": "Быстрые сервисы", "recent_notes": "Последние уведомления",
        "ask_ai": "Спросить AI Jana", "send": "Отправить", "all": "Все",
    },
    "kz": {
        "nav_home": "Кабинет", "nav_requests": "Өтінімдер", "nav_academy": "Jana Academy",
        "nav_ai": "AI Jana", "nav_notifications": "Хабарландырулар", "login": "Кіру", "logout": "Шығу",
        "hero_title": "Барлығына арналған қарапайым HR",
        "hero_sub": "Профиль, өтінімдер, оқу және HR жауаптары бір жерде. Бастау үшін жүйеге кіріңіз.",
        "profile": "Профиль", "leave_left": "Демалыс қалдығы", "days": "күн",
        "my_requests": "Менің өтінімдерім", "new_request": "Жаңа өтінім", "my_courses": "Менің оқуым",
        "services": "Жылдам сервистер", "recent_notes": "Соңғы хабарландырулар",
        "ask_ai": "AI Jana-дан сұрау", "send": "Жіберу", "all": "Барлығы",
    },
}

def tr(key, lang="ru"):
    return T.get(lang, T["ru"]).get(key) or T["ru"].get(key, key)
