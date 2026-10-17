#████  █      ███  ████  █      ███  █   █ ████       █     ████ 
#█   █ █     █   █ █   █ █     █   █ █   █ █   █     ██         █
#████  █     █████ ████  █     █████ █████ ████       █      ███ 
#█   █ █     █   █ █   █ █     █   █ █   █ █  █       █         █
#████  █████ █   █ ████  █████ █   █ █   █ █   █    █████ █ ████ 
# Made by #34Team
# For Post-Tech Hackathon 2026

# Programmer: Alexey Makarenko
# Точки подключения внешних систем типо 1С и бла-бла
import itertools

_doc_counter = itertools.count(1)


def zup_get_employee(login: str) -> dict:
    """1С:ЗУП (read-only): кадровые данные. Сейчас данные берутся из таблицы users."""
    return {"source": "mock-1c-zup", "login": login}


def documentolog_register(request_id: int, kind: str) -> str:
    """Documentolog: регистрация заявки в документообороте. Сейчас возвращает фиктивный номер."""
    return f"DOC-{next(_doc_counter):05d}"
