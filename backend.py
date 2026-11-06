#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
💎 STAKE 2011 • NEON CASINO & FIGHT CLUB v5.0 ULTRA (FastAPI + SQLite3) 💎
================================================================================
Полностью переработанный сервер профессионального уровня (12 игр + Live PvP Вызовы
Онлайн на Карты и на Бойцов + Живой Чат + Переводы денег друзьям + VIP Ранги):

🎮 12 ПОЛНОЦЕННЫХ ИГРОВЫХ РЕЖИМОВ (СЕРВЕРНЫЙ РАСЧЁТ + HOUSE EDGE):
 1. 🍏 Apple of Fortune (8 этажей вверх, 5 колонок, до 45.0x)
 2. 💣 Stake Mines 5x5 (25 плиток, выбор 1–20 мин, до 100x)
 3. 🟣 Plinko Physics (Пирамида 12 рядов, режимы Low / Medium / High до 110x)
 4. 🚀 Crash / Aviator (Живая ракета иксов с ручным и авто-кэшаутом)
 5. 🎡 Crazy Neon Wheel (16 секторов с точным расчётом угла остановки)
 6. 🃏 Blackjack 21 Pro (Карточный стол против Дилера: Hit, Stand, Double Down)
 7. 🐲 Dragon Tower (Башня Дракона — 9 уровней по 3 ячейки, до 85x)
 8. 🎚 Dice Slider (Ползунок 2%–98%, Roll Over / Roll Under)
 9. ⚡ Limbo Target (Мгновенный пробив икса от 1.05x до 500x)
10. 🪙 3D Coinflip (Орёл / Решка с серией удвоений подряд!)
11. 💎 Keno 40 (Выбор до 10 номеров из 40, выпадение 10 шаров)
12. 🥊 Cyber-Octagon 2011 (11 легендарных друзей с боевой тактикой до 15x) + 🎰 Slots 777

⚔️ ОНЛАЙН-ВЫЗОВЫ ДРУЗЬЯМ (LIVE PVP DUELS):
 - Видишь всех друзей, кто сейчас Online, и кидаешь им живой вызов:
   • Режим 1: Карточная Дуэль (Королевский Покер-Баттл / 21 на банк)
   • Режим 2: Битва Персонажей 2011 (каждый выбирает своего бойца и секретный удар!)
 - У друга прямо на экране выскакивает неоновое окно вызова со звуком!

🚀 ЗАПУСК:
    python backend.py
    Открой в браузере: http://127.0.0.1:8000
================================================================================
"""

import hashlib
import hmac
import logging
import math
import os
import random
import secrets
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import uvicorn
from fastapi import Cookie, Depends, FastAPI, Header, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

# ==============================================================================
# ⚙️ КОНФИГУРАЦИЯ СЕРВЕРА
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = str(BASE_DIR / "neon_stake_2011.db")

SECRET_KEY = os.getenv("CASINO_SECRET_KEY", "davron_2011_ultra_neon_secret_key_v5")
START_BALANCE = 10000          # Стартовый баланс каждого друга: 10 000$
CASHBACK_FLOOR = 1000          # Несгораемый кэшбэк при падении < 100$: всегда возвращает 1 000$!
ONLINE_WINDOW_SEC = 90         # Честный онлайн: 90 секунд с последнего пинга
TOKEN_TTL_SEC = 365 * 86400    # Вечная сессия на 365 дней

DEFAULT_ADMIN_USERNAMES = {"davron", "davrik", "luxekraken", "admin"}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("NeonStakeV5Ultra")

app = FastAPI(title="Stake 2011 Ultra API", version="5.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Активные игровые сессии в памяти сервера
ACTIVE_MINES_GAMES: Dict[int, Dict[str, Any]] = {}
ACTIVE_APPLE_GAMES: Dict[int, Dict[str, Any]] = {}
ACTIVE_TOWER_GAMES: Dict[int, Dict[str, Any]] = {}
ACTIVE_CRASH_GAMES: Dict[int, Dict[str, Any]] = {}
ACTIVE_BJ_GAMES: Dict[int, Dict[str, Any]] = {}
ACTIVE_COINFLIP_STREAKS: Dict[int, Dict[str, Any]] = {}
USER_WIN_STREAK: Dict[int, int] = {}

AVATAR_PRESETS = [
    "neon_wolf",
    "cyber_skull",
    "gold_crown",
    "emerald_viper",
    "crimson_samurai",
    "plasma_tiger",
    "diamond_king",
    "shadow_ninja",
    "laser_eagle",
    "toxic_rhino",
]


# ==============================================================================
# 🥊 БАЗА 11 ЛЕГЕНДАРНЫХ ДРУЗЕЙ 2011 (С КАСТОМНЫМИ ВЕКТОРНЫМИ КОДАМИ И ЦВЕТАМИ)
# ==============================================================================
FIGHTERS_DATA: Dict[str, Dict[str, Any]] = {
    "davrik": {
        "key": "davrik",
        "name": "Даврик",
        "code": "DVR",
        "birth_year": 2011,
        "height_cm": 175,
        "weight_kg": 54,
        "weight_class": "Легчайший (54 кг)",
        "power_score": 67,
        "title": "Молния Тхэквондо",
        "style": "Тхэквондо + Качалка (2 мес.)",
        "color": "#00e701",
        "accent": "#059669",
        "skills": ["Вертушка 360° в челюсть", "Памп бицепса", "Двойной хай-кик"],
        "bio": "Ходит в зал 2 месяца и совмещает железо с тхэквондо. Молниеносная скорость ног.",
        "crit_phrase": "ДАВРИК ловит идеальный тайминг и вколачивает вертушку с разворота точно в цель!",
        "win_quote": "«Два месяца в зале и база тхэквондо — это вам не шутки, пацаны!»",
    },
    "muham": {
        "key": "muham",
        "name": "Мухам",
        "code": "MHM",
        "birth_year": 2011,
        "height_cm": 178,
        "weight_kg": 59,
        "weight_class": "Полулёгкий (59 кг)",
        "power_score": 70,
        "title": "Мастер Чёрного Пояса",
        "style": "Чёрный пояс Тхэквондо + Атлет",
        "color": "#a855f7",
        "accent": "#6b21a8",
        "skills": ["Торнадо-кик 540°", "Сухая выносливость", "Встречный кик на отходе"],
        "bio": "Сухое тело спортсмена и официальный чёрный пояс по тхэквондо. Технарь высшей пробы.",
        "crit_phrase": "МУХАМ активирует технику Чёрного Пояса и сносит соперника торнадо-киком в прыжке!",
        "win_quote": "«Чёрный пояс просто так не дают. Уважение сопернику!»",
    },
    "asad": {
        "key": "asad",
        "name": "Асад",
        "code": "ASD",
        "birth_year": 2011,
        "height_cm": 182,
        "weight_kg": 62,
        "weight_class": "Лёгкий вес (62 кг)",
        "power_score": 71,
        "title": "Длиннорукий Хищник",
        "style": "Вольная борьба + Плавание (182 см)",
        "color": "#38bdf8",
        "accent": "#0284c7",
        "skills": ["Проход в ноги с 2 метров", "Дыхалка пловца", "Контроль рычагами"],
        "bio": "Самый высокий в компании (182 см!). База вольной борьбы и плавания даёт бесконечное кардио.",
        "crit_phrase": "АСАД ныряет под руку, поднимает соперника над головой и с грохотом впечатывает в канвас!",
        "win_quote": "«С высоты 182 сантиметра ваши удары читаются как букварь!»",
    },
    "oybek": {
        "key": "oybek",
        "name": "Ойбек",
        "code": "OBK",
        "birth_year": 2011,
        "height_cm": 175,
        "weight_kg": 53,
        "weight_class": "Наилегчайший (53 кг)",
        "power_score": 69,
        "title": "Сухой Титан",
        "style": "Опытный качок на жёсткой сушке",
        "color": "#facc15",
        "accent": "#ca8a04",
        "skills": ["Секущий панч предплечьем", "0% лишнего жира", "Пулемётная двойка"],
        "bio": "При весе 53 кг обладает чистейшей сухой мышечной массой — ходит в зал очень давно и бьёт как током.",
        "crit_phrase": "ОЙБЕК напрягает все стальные волокна и выдаёт такой сухой панч, что искры летят из глаз!",
        "win_quote": "«Масса — ничто, сухая форма и стаж в зале — всё!»",
    },
    "afruz": {
        "key": "afruz",
        "name": "Афруз",
        "code": "AFR",
        "birth_year": 2011,
        "height_cm": 176,
        "weight_kg": 70,
        "weight_class": "Полусредний (70 кг)",
        "power_score": 66,
        "title": "Бронированный Носорог",
        "style": "Силовой качок на плотной массе",
        "color": "#f97316",
        "accent": "#c2410c",
        "skills": ["Броня корпуса (гасит урон)", "Тяжёлый свинг 70 кг", "Таран у сетки"],
        "bio": "Солидные 70 кг при росте 176 см. Пробить или сдвинуть его корпус почти нереально — прёт как танк.",
        "crit_phrase": "АФРУЗ включает режим Броне-Танка и сносит оппонента чугунным правым крюком на 70 кг!",
        "win_quote": "«Против 70 килограмм чистой массы и брони приёмов нет, пацаны!»",
    },
    "kamri": {
        "key": "kamri",
        "name": "Камри",
        "code": "KMR",
        "birth_year": 2011,
        "height_cm": 168,
        "weight_kg": 55,
        "weight_class": "Легчайший (55 кг)",
        "power_score": 71,
        "title": "Король Партера 3.5",
        "style": "Профи-борец + Плавание",
        "color": "#10b981",
        "accent": "#047857",
        "skills": ["Суплекс с прогибом", "Низкий центр тяжести", "Удушающий сзади"],
        "bio": "Компактный борцовский танк (168 см). Профи в борьбе — если схватит за корпус, полёт обеспечен.",
        "crit_phrase": "КАМРИ 3.5 оформляет легендарный борцовский прогиб через грудь — весь октагон дрожит!",
        "win_quote": "«Если ты не умеешь бороться — ты уже проиграл до гонга!»",
    },
    "nekit": {
        "key": "nekit",
        "name": "Некит",
        "code": "NKT",
        "birth_year": 2011,
        "height_cm": 175,
        "weight_kg": 65,
        "weight_class": "Атлетичный (65 кг)",
        "power_score": 73,
        "title": "Гора Чистых Мышц",
        "style": "Профи-бодибилдер (1+ год в зале)",
        "color": "#ef4444",
        "accent": "#b91c1c",
        "skills": ["Кувалда из 65 кг мышц", "Медвежий захват", "Стальной корпус"],
        "bio": "Главный силовик компании: 65 кг отборных мышц при 175 см, пашет в зале больше года без пропусков.",
        "crit_phrase": "НЕКИТ попадает чистым правым молотом — стальная клетка трещит по швам!",
        "win_quote": "«Больше года в зале без пропусков. Железо решает!»",
    },
    "bilol": {
        "key": "bilol",
        "name": "Билол",
        "code": "BLL",
        "birth_year": 2011,
        "height_cm": 173,
        "weight_kg": 84,
        "weight_class": "Супертяж (84 кг!)",
        "power_score": 69,
        "title": "Босс Тяжёлого Веса",
        "style": "Супертяж 84 кг + Зал + Плавание",
        "color": "#ec4899",
        "accent": "#be185d",
        "skills": ["Цунами-пресс 84 кг", "Непробиваемая стойкость", "Сплэш сверху"],
        "bio": "Абсолютный рекордсмен по массе — 84 КГ! Сдвинуть его с места невозможно, один навал решает бой.",
        "crit_phrase": "БИЛОЛ обрушивает все свои 84 кг сверху — настоящее землетрясение в октагоне!",
        "win_quote": "«Весовые категории придумали, чтобы спасать вас от моих 84 кг!»",
    },
    "zabik": {
        "key": "zabik",
        "name": "Забик",
        "code": "ZBK",
        "birth_year": 2011,
        "height_cm": 174,
        "weight_kg": 48,
        "weight_class": "Ультра-Ниндзя (48 кг)",
        "power_score": 56,
        "title": "Легенда Ультра-Инстинкта",
        "style": "Ультра-Инстинкт & Лаки-Панч",
        "color": "#06b6d4",
        "accent": "#0e7490",
        "skills": ["Ультра-Инстинкт уворота", "Костяшка Судьбы (Крит)", "Режим 2D-тени"],
        "bio": "Забик (48 кг) в режиме Ультра-Инстинкта! Пока качки мажут по воздуху, он выдаёт апсеты до 15x!",
        "crit_phrase": "СЕНСАЦИЯ ВЕКА! ЗАБИК ВКЛЮЧИЛ УЛЬТРА-ИНСТИНКТ, УШЁЛ В МАТРИЦУ И ОДНОЙ КОСТЯШКОЙ ВЫРУБИЛ ФАВОРИТА!",
        "win_quote": "«НУ И ЧЁ, КТО ТЕПЕРЬ СЛАБЫЙ?! 48 КГ ЧИСТОГО СКИЛЛА, СЮДА БАБКИ ПАЦАНЫ!»",
    },
    "ibo": {
        "key": "ibo",
        "name": "Ибо",
        "code": "IBO",
        "birth_year": 2011,
        "height_cm": 175,
        "weight_kg": 53,
        "weight_class": "Наилегчайший (53 кг)",
        "power_score": 64,
        "title": "Скрытый Джокер",
        "style": "Сила Спокойствия & Стрит-Файт",
        "color": "#60a5fa",
        "accent": "#2563eb",
        "skills": ["Аура спокойствия", "Внезапный кросс", "Хладнокровие в финале"],
        "bio": "Хороший и спокойный парень в жизни, но в клетке бьёт точно в цель, когда соперник открывается.",
        "crit_phrase": "ИБО включает режим тихого шторма и выдаёт идеальный нокаутирующий кросс!",
        "win_quote": "«Пацаны, без обид, я хороший парень, но сегодня куш мой!»",
    },
    "adham": {
        "key": "adham",
        "name": "Адхам",
        "code": "ADH",
        "birth_year": 2011,
        "height_cm": 173,
        "weight_kg": 62,
        "weight_class": "Атлетичный (62 кг)",
        "power_score": 72,
        "title": "Брутальный Страйкер",
        "style": "Профессиональный футболист",
        "color": "#22c55e",
        "accent": "#15803d",
        "skills": ["Пенальти-кик 120 км/ч", "Прессинг 90 минут", "Стальные голени"],
        "bio": "Профессиональный футболист с сухим телом атлета и брутальным ударом ноги.",
        "crit_phrase": "АДХАМ бьёт с подъёма ноги как с пенальти в финале ЛЧ — чистая пушка без шансов!",
        "win_quote": "«На поле или в октагоне — брутальный стиль всегда забирает кубок!»",
    },
}

# ==============================================================================
# 🎡 КОНФИГУРАЦИИ ИГР (WHEEL, APPLE, TOWER, PLINKO, KENO)
# ==============================================================================
WHEEL_SEGMENTS: List[Dict[str, Any]] = [
    {"index": 0,  "multiplier": 0.0,  "label": "0x",   "color": "#1e293b", "weight": 150},
    {"index": 1,  "multiplier": 1.5,  "label": "1.5x", "color": "#00e701", "weight": 120},
    {"index": 2,  "multiplier": 0.0,  "label": "0x",   "color": "#1e293b", "weight": 150},
    {"index": 3,  "multiplier": 2.0,  "label": "2x",   "color": "#3b82f6", "weight": 85},
    {"index": 4,  "multiplier": 0.5,  "label": "0.5x", "color": "#475569", "weight": 110},
    {"index": 5,  "multiplier": 3.0,  "label": "3x",   "color": "#a855f7", "weight": 55},
    {"index": 6,  "multiplier": 0.0,  "label": "0x",   "color": "#1e293b", "weight": 150},
    {"index": 7,  "multiplier": 1.5,  "label": "1.5x", "color": "#00e701", "weight": 120},
    {"index": 8,  "multiplier": 5.0,  "label": "5x",   "color": "#f59e0b", "weight": 30},
    {"index": 9,  "multiplier": 0.0,  "label": "0x",   "color": "#1e293b", "weight": 150},
    {"index": 10, "multiplier": 2.0,  "label": "2x",   "color": "#3b82f6", "weight": 85},
    {"index": 11, "multiplier": 0.5,  "label": "0.5x", "color": "#475569", "weight": 110},
    {"index": 12, "multiplier": 1.5,  "label": "1.5x", "color": "#00e701", "weight": 120},
    {"index": 13, "multiplier": 0.0,  "label": "0x",   "color": "#1e293b", "weight": 150},
    {"index": 14, "multiplier": 3.0,  "label": "3x",   "color": "#a855f7", "weight": 55},
    {"index": 15, "multiplier": 15.0, "label": "15x",  "color": "#ef4444", "weight": 8},
]

APPLE_LEVELS_CONFIG: List[Dict[str, Any]] = [
    {"level": 1, "bad_count": 1, "multiplier": 1.23},
    {"level": 2, "bad_count": 1, "multiplier": 1.54},
    {"level": 3, "bad_count": 1, "multiplier": 1.93},
    {"level": 4, "bad_count": 2, "multiplier": 2.85},
    {"level": 5, "bad_count": 2, "multiplier": 4.75},
    {"level": 6, "bad_count": 3, "multiplier": 9.50},
    {"level": 7, "bad_count": 3, "multiplier": 18.00},
    {"level": 8, "bad_count": 4, "multiplier": 45.00},
]

DRAGON_TOWER_LEVELS: List[Dict[str, Any]] = [
    {"level": 1, "cols": 3, "eggs": 2, "multiplier": 1.42},
    {"level": 2, "cols": 3, "eggs": 2, "multiplier": 2.05},
    {"level": 3, "cols": 3, "eggs": 2, "multiplier": 2.98},
    {"level": 4, "cols": 3, "eggs": 2, "multiplier": 4.35},
    {"level": 5, "cols": 3, "eggs": 2, "multiplier": 6.40},
    {"level": 6, "cols": 3, "eggs": 1, "multiplier": 14.50},
    {"level": 7, "cols": 3, "eggs": 1, "multiplier": 32.00},
    {"level": 8, "cols": 3, "eggs": 1, "multiplier": 75.00},
]

# Таблицы множителей Plinko (12 рядов = 13 корзин снизу)
PLINKO_BUCKETS: Dict[str, List[float]] = {
    "low":    [8.5, 3.0, 1.6, 1.2, 1.0, 0.7, 0.5, 0.7, 1.0, 1.2, 1.6, 3.0, 8.5],
    "medium": [22.0, 7.0, 3.0, 1.5, 0.9, 0.4, 0.2, 0.4, 0.9, 1.5, 3.0, 7.0, 22.0],
    "high":   [110.0, 24.0, 6.5, 2.0, 0.6, 0.2, 0.1, 0.2, 0.6, 2.0, 6.5, 24.0, 110.0],
}

# Выплаты Keno (зависят от того, сколько чисел выбрал игрок 1..10 и сколько совпало)
KENO_PAYOUT_TABLE: Dict[int, List[float]] = {
    1:  [0.0, 3.5],
    2:  [0.0, 1.5, 7.5],
    3:  [0.0, 0.5, 2.8, 18.0],
    4:  [0.0, 0.0, 1.8, 7.0, 42.0],
    5:  [0.0, 0.0, 1.2, 3.5, 16.0, 85.0],
    6:  [0.0, 0.0, 0.5, 2.2, 8.0, 38.0, 150.0],
    7:  [0.0, 0.0, 0.5, 1.5, 4.5, 18.0, 75.0, 250.0],
    8:  [0.0, 0.0, 0.0, 1.2, 3.0, 10.0, 40.0, 140.0, 400.0],
    9:  [0.0, 0.0, 0.0, 1.0, 2.2, 6.5, 24.0, 85.0, 250.0, 600.0],
    10: [0.0, 0.0, 0.0, 0.5, 1.8, 5.0, 15.0, 50.0, 160.0, 400.0, 1000.0],
}


# ==============================================================================
# 🗄 БАЗА ДАННЫХ SQLITE (ПОЛЬЗОВАТЕЛИ, LIVE PVP ВЫЗОВЫ, ЧАТ, БОНУСЫ)
# ==============================================================================
def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str, salt: Optional[str] = None) -> str:
    if not salt:
        salt = secrets.token_hex(8)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        (salt + SECRET_KEY).encode("utf-8"),
        100_000,
    ).hex()
    return f"{salt}${digest}"


def verify_password(password: str, stored_hash: str) -> bool:
    if "$" not in stored_hash:
        return False
    salt, _ = stored_hash.split("$", 1)
    return hmac.compare_digest(hash_password(password, salt), stored_hash)


def init_db() -> None:
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS web_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                display_name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                avatar TEXT DEFAULT 'neon_wolf',
                balance INTEGER DEFAULT 10000,
                total_won INTEGER DEFAULT 0,
                total_wagered INTEGER DEFAULT 0,
                biggest_win INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                cashbacks_received INTEGER DEFAULT 0,
                is_admin INTEGER DEFAULT 0,
                last_seen INTEGER DEFAULT 0,
                created_at INTEGER DEFAULT 0
            )
            """
        )
        try:
            cur.execute("ALTER TABLE web_users ADD COLUMN total_wagered INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS web_sessions (
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at INTEGER NOT NULL,
                expires_at INTEGER NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS custom_fighter_powers (
                fighter_key TEXT PRIMARY KEY,
                power_score INTEGER NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS live_feed (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                avatar TEXT NOT NULL,
                game TEXT NOT NULL,
                bet INTEGER NOT NULL,
                multiplier REAL NOT NULL,
                payout INTEGER NOT NULL,
                is_win INTEGER NOT NULL,
                created_at INTEGER NOT NULL
            )
            """
        )
        # Таблица Live PvP Вызовов между друзьями (Карты или Бойцы 2011)
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS web_pvp_challenges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                challenger_id INTEGER NOT NULL,
                challenger_name TEXT NOT NULL,
                challenger_avatar TEXT NOT NULL,
                target_id INTEGER NOT NULL,
                target_name TEXT NOT NULL,
                mode TEXT NOT NULL,            -- 'cards' или 'fighters'
                bet INTEGER NOT NULL,
                c_fighter TEXT DEFAULT 'davrik',
                c_tactic TEXT DEFAULT 'head',
                t_fighter TEXT DEFAULT '',
                t_tactic TEXT DEFAULT '',
                status TEXT DEFAULT 'pending', -- 'pending', 'completed', 'declined'
                winner_id INTEGER DEFAULT 0,
                winner_name TEXT DEFAULT '',
                summary_json TEXT DEFAULT '{}',
                created_at INTEGER NOT NULL
            )
            """
        )
        # Таблица Живого Чата друзей
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS web_chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                display_name TEXT NOT NULL,
                avatar TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0,
                text TEXT NOT NULL,
                created_at INTEGER NOT NULL
            )
            """
        )

        cur.execute("SELECT fighter_key, power_score FROM custom_fighter_powers")
        for row in cur.fetchall():
            fkey = row["fighter_key"]
            if fkey in FIGHTERS_DATA:
                FIGHTERS_DATA[fkey]["power_score"] = row["power_score"]

        cur.execute("SELECT COUNT(*) AS cnt FROM web_users")
        if cur.fetchone()["cnt"] == 0:
            now = int(time.time())
            cur.execute(
                """
                INSERT INTO web_users
                (username, display_name, password_hash, avatar, balance, total_won, total_wagered, biggest_win, wins, is_admin, last_seen, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
                """,
                (
                    "davron",
                    "Даврон",
                    hash_password("2011"),
                    "gold_crown",
                    25000,
                    50000,
                    80000,
                    15000,
                    12,
                    now,
                    now,
                ),
            )
            cur.execute(
                """
                INSERT INTO web_chat_messages (user_id, username, display_name, avatar, is_admin, text, created_at)
                VALUES (1, 'davron', 'Даврон', 'gold_crown', 1, 'Салам пацаны! Добро пожаловать в наш закрытый клуб STAKE 2011 ULTRA!', ?)
                """,
                (now,),
            )
        conn.commit()


# ==============================================================================
# 🔐 СЕССИЯ, VIP-РАНГИ И АВТОМАТИЧЕСКИЙ КЭШБЭК 1000$
# ==============================================================================
def compute_vip_rank(total_wagered: int, is_admin: int = 0) -> Dict[str, str]:
    if is_admin:
        return {"title": "ROOT OWNER", "color": "#facc15"}
    if total_wagered >= 250000:
        return {"title": "DIAMOND VIP", "color": "#38bdf8"}
    if total_wagered >= 100000:
        return {"title": "PLATINUM", "color": "#a855f7"}
    if total_wagered >= 35000:
        return {"title": "GOLD MAJOR", "color": "#f59e0b"}
    if total_wagered >= 10000:
        return {"title": "SILVER", "color": "#94a3b8"}
    return {"title": "BRONZE", "color": "#00e701"}


def create_session_token(user_id: int) -> str:
    now = int(time.time())
    raw_token = f"{user_id}.{secrets.token_urlsafe(32)}"
    with get_db() as conn:
        conn.execute(
            "INSERT INTO web_sessions (token, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)",
            (raw_token, user_id, now, now + TOKEN_TTL_SEC),
        )
        conn.commit()
    return raw_token


def has_active_game(user_id: int) -> bool:
    return (
        user_id in ACTIVE_MINES_GAMES
        or user_id in ACTIVE_APPLE_GAMES
        or user_id in ACTIVE_TOWER_GAMES
        or user_id in ACTIVE_CRASH_GAMES
        or user_id in ACTIVE_BJ_GAMES
        or user_id in ACTIVE_COINFLIP_STREAKS
    )


def apply_cashback_if_needed(user_id: int) -> Tuple[int, bool]:
    if has_active_game(user_id):
        with get_db() as conn:
            row = conn.execute("SELECT balance FROM web_users WHERE id = ?", (user_id,)).fetchone()
            return (row["balance"] if row else 0), False

    with get_db() as conn:
        cur = conn.cursor()
        row = cur.execute("SELECT balance FROM web_users WHERE id = ?", (user_id,)).fetchone()
        if not row:
            return 0, False
        bal = row["balance"]
        if bal < 100:
            cur.execute(
                """
                UPDATE web_users
                SET balance = ?, cashbacks_received = cashbacks_received + 1
                WHERE id = ?
                """,
                (CASHBACK_FLOOR, user_id),
            )
            conn.commit()
            return CASHBACK_FLOOR, True
        return bal, False


def record_game_result(
    user_id: int,
    username: str,
    avatar: str,
    game_name: str,
    bet: int,
    payout: int,
    multiplier: float,
    is_win: bool,
) -> Tuple[int, bool]:
    now = int(time.time())
    net_profit = max(0, payout - bet) if is_win else 0

    with get_db() as conn:
        cur = conn.cursor()
        row = cur.execute(
            "SELECT balance, total_won, biggest_win FROM web_users WHERE id = ?",
            (user_id,),
        ).fetchone()
        if not row:
            return 0, False

        if is_win:
            USER_WIN_STREAK[user_id] = USER_WIN_STREAK.get(user_id, 0) + 1
            new_big = max(row["biggest_win"], payout)
            cur.execute(
                """
                UPDATE web_users
                SET balance = balance + ?,
                    total_won = total_won + ?,
                    total_wagered = total_wagered + ?,
                    biggest_win = ?,
                    wins = wins + 1,
                    last_seen = ?
                WHERE id = ?
                """,
                (payout, net_profit if net_profit > 0 else payout, bet, new_big, now, user_id),
            )
        else:
            USER_WIN_STREAK[user_id] = 0
            cur.execute(
                """
                UPDATE web_users
                SET losses = losses + 1,
                    total_wagered = total_wagered + ?,
                    last_seen = ?
                WHERE id = ?
                """,
                (bet, now, user_id),
            )

        cur.execute(
            """
            INSERT INTO live_feed (username, avatar, game, bet, multiplier, payout, is_win, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (username, avatar, game_name, bet, round(multiplier, 2), payout, 1 if is_win else 0, now),
        )
        cur.execute(
            "DELETE FROM live_feed WHERE id NOT IN (SELECT id FROM live_feed ORDER BY id DESC LIMIT 45)"
        )
        conn.commit()

    return apply_cashback_if_needed(user_id)


def serialize_user(row: sqlite3.Row) -> Dict[str, Any]:
    now = int(time.time())
    last_seen = row["last_seen"] or 0
    is_online = last_seen > 0 and (now - last_seen) <= ONLINE_WINDOW_SEC
    wagered = row["total_wagered"] if "total_wagered" in row.keys() else 0
    vip = compute_vip_rank(wagered or 0, row["is_admin"])
    return {
        "id": row["id"],
        "username": row["username"],
        "display_name": row["display_name"],
        "avatar": row["avatar"],
        "balance": row["balance"],
        "total_won": row["total_won"],
        "total_wagered": wagered or 0,
        "biggest_win": row["biggest_win"],
        "wins": row["wins"],
        "losses": row["losses"],
        "cashbacks_received": row["cashbacks_received"],
        "is_admin": bool(row["is_admin"]),
        "is_online": is_online,
        "last_seen": last_seen,
        "vip_title": vip["title"],
        "vip_color": vip["color"],
    }


def get_current_user(
    authorization: Optional[str] = Header(default=None),
    casino_session: Optional[str] = Cookie(default=None),
) -> Dict[str, Any]:
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
    elif casino_session:
        token = casino_session.strip()

    if not token:
        raise HTTPException(status_code=401, detail="Необходима авторизация")

    now = int(time.time())
    with get_db() as conn:
        cur = conn.cursor()
        sess = cur.execute(
            "SELECT user_id, expires_at FROM web_sessions WHERE token = ?",
            (token,),
        ).fetchone()
        if not sess or sess["expires_at"] < now:
            raise HTTPException(status_code=401, detail="Сессия истекла, войдите снова")

        uid = sess["user_id"]
        cur.execute("UPDATE web_users SET last_seen = ? WHERE id = ?", (now, uid))
        conn.commit()

    apply_cashback_if_needed(uid)

    with get_db() as conn:
        user_row = conn.execute("SELECT * FROM web_users WHERE id = ?", (uid,)).fetchone()
        if not user_row:
            raise HTTPException(status_code=401, detail="Пользователь не найден")
        return serialize_user(user_row)


# ==============================================================================
# 📋 МОДЕЛИ ДАННЫХ (PYDANTIC)
# ==============================================================================
class AuthRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=24)
    password: str = Field(..., min_length=2, max_length=64)
    display_name: Optional[str] = Field(default=None, max_length=28)
    avatar: Optional[str] = Field(default=None)


class BetSimpleRequest(BaseModel):
    bet: int = Field(..., ge=10)


class ApplePickRequest(BaseModel):
    col: int = Field(..., ge=0, le=4)


class MinesStartRequest(BaseModel):
    bet: int = Field(..., ge=10)
    mines_count: int = Field(default=5, ge=1, le=20)


class MinesClickRequest(BaseModel):
    cell_index: int = Field(..., ge=0, le=24)


class TowerPickRequest(BaseModel):
    col: int = Field(..., ge=0, le=2)


class PlinkoDropRequest(BaseModel):
    bet: int = Field(..., ge=10)
    risk: str = Field(default="medium", pattern="^(low|medium|high)$")


class CrashStartRequest(BaseModel):
    bet: int = Field(..., ge=10)
    auto_cashout: Optional[float] = Field(default=None)


class CrashCashoutRequest(BaseModel):
    current_multiplier: float = Field(..., ge=1.01, le=200.0)


class BlackjackActionRequest(BaseModel):
    action: str = Field(..., pattern="^(hit|stand|double)$")


class DicePlayRequest(BaseModel):
    bet: int = Field(..., ge=10)
    target: int = Field(..., ge=5, le=95)
    condition: str = Field(default="over", pattern="^(over|under)$")


class LimboPlayRequest(BaseModel):
    bet: int = Field(..., ge=10)
    target_multiplier: float = Field(..., ge=1.05, le=500.0)


class CoinflipStartRequest(BaseModel):
    bet: int = Field(..., ge=10)


class CoinflipPickRequest(BaseModel):
    side: str = Field(..., pattern="^(heads|tails)$")


class KenoPlayRequest(BaseModel):
    bet: int = Field(..., ge=10)
    picks: List[int]


class FightBetRequest(BaseModel):
    fighter1_key: str
    fighter2_key: str
    picked_key: str
    tactic: str = Field(default="head")
    bet: int = Field(default=0, ge=0)


class PvpCreateRequest(BaseModel):
    target_id: int  # 0 = открытый вызов для любого онлайн, либо конкретный ID друга
    mode: str = Field(..., pattern="^(cards|fighters)$")
    bet: int = Field(..., ge=50)
    fighter_key: str = Field(default="davrik")
    tactic: str = Field(default="head")


class PvpAcceptRequest(BaseModel):
    challenge_id: int
    fighter_key: str = Field(default="muham")
    tactic: str = Field(default="kick")


class TransferMoneyRequest(BaseModel):
    target_user_id: int
    amount: int = Field(..., ge=50)


class ChatMessageRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=220)


class AdminBalanceRequest(BaseModel):
    target_user_id: int
    mode: str = Field(..., pattern="^(add|set)$")
    amount: int


class AdminGlobalBalanceRequest(BaseModel):
    mode: str = Field(..., pattern="^(bonus_all|reset_all)$")
    amount: int = Field(default=10000)


class AdminFighterPowerRequest(BaseModel):
    fighter_key: str
    power_score: int = Field(..., ge=25, le=95)


# ==============================================================================
# 🔐 АВТОРИЗАЦИЯ И ПИНГ ОНЛАЙНА
# ==============================================================================
@app.post("/api/auth/register")
def api_register(req: AuthRequest, response: Response):
    clean_uname = req.username.strip().lower()
    if not clean_uname.isalnum() and "_" not in clean_uname:
        raise HTTPException(
            status_code=400,
            detail="Ник должен содержать только латинские буквы, цифры или _",
        )

    disp_name = (req.display_name or req.username).strip()[:24]
    avatar = req.avatar if req.avatar in AVATAR_PRESETS else random.choice(AVATAR_PRESETS)
    now = int(time.time())

    with get_db() as conn:
        cur = conn.cursor()
        existing = cur.execute(
            "SELECT id FROM web_users WHERE LOWER(username) = ?", (clean_uname,)
        ).fetchone()
        if existing:
            raise HTTPException(status_code=400, detail="Этот ник уже занят! Переключись на «Вход».")

        total_users = cur.execute("SELECT COUNT(*) AS c FROM web_users").fetchone()["c"]
        is_admin = 1 if (clean_uname in DEFAULT_ADMIN_USERNAMES or total_users == 0) else 0

        cur.execute(
            """
            INSERT INTO web_users
            (username, display_name, password_hash, avatar, balance, total_won, total_wagered, biggest_win, wins, losses, is_admin, last_seen, created_at)
            VALUES (?, ?, ?, ?, ?, 0, 0, 0, 0, 0, ?, ?, ?)
            """,
            (
                clean_uname,
                disp_name,
                hash_password(req.password),
                avatar,
                START_BALANCE,
                is_admin,
                now,
                now,
            ),
        )
        uid = cur.lastrowid
        conn.commit()
        user_row = cur.execute("SELECT * FROM web_users WHERE id = ?", (uid,)).fetchone()

    token = create_session_token(uid)
    response.set_cookie(
        key="casino_session",
        value=token,
        max_age=TOKEN_TTL_SEC,
        httponly=True,
        samesite="lax",
    )
    return {"status": "ok", "token": token, "user": serialize_user(user_row)}


@app.post("/api/auth/login")
def api_login(req: AuthRequest, response: Response):
    clean_uname = req.username.strip().lower()
    now = int(time.time())

    with get_db() as conn:
        cur = conn.cursor()
        user_row = cur.execute(
            "SELECT * FROM web_users WHERE LOWER(username) = ?", (clean_uname,)
        ).fetchone()
        if not user_row or not verify_password(req.password, user_row["password_hash"]):
            raise HTTPException(status_code=401, detail="Неверный логин или пароль!")

        uid = user_row["id"]
        if clean_uname in DEFAULT_ADMIN_USERNAMES and not user_row["is_admin"]:
            cur.execute("UPDATE web_users SET is_admin = 1, last_seen = ? WHERE id = ?", (now, uid))
        else:
            cur.execute("UPDATE web_users SET last_seen = ? WHERE id = ?", (now, uid))
        conn.commit()

    apply_cashback_if_needed(uid)
    with get_db() as conn:
        user_row = conn.execute("SELECT * FROM web_users WHERE id = ?", (uid,)).fetchone()

    token = create_session_token(uid)
    response.set_cookie(
        key="casino_session",
        value=token,
        max_age=TOKEN_TTL_SEC,
        httponly=True,
        samesite="lax",
    )
    return {"status": "ok", "token": token, "user": serialize_user(user_row)}


@app.post("/api/auth/logout")
def api_logout(
    response: Response,
    authorization: Optional[str] = Header(default=None),
    casino_session: Optional[str] = Cookie(default=None),
):
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
    elif casino_session:
        token = casino_session.strip()

    if token:
        with get_db() as conn:
            conn.execute("DELETE FROM web_sessions WHERE token = ?", (token,))
            conn.commit()
    response.delete_cookie("casino_session")
    return {"status": "ok"}


@app.get("/api/auth/me")
def api_me(user: Dict[str, Any] = Depends(get_current_user)):
    uid = user["id"]
    return {
        "status": "ok",
        "user": user,
        "has_active_mines": uid in ACTIVE_MINES_GAMES,
        "has_active_apple": uid in ACTIVE_APPLE_GAMES,
        "has_active_tower": uid in ACTIVE_TOWER_GAMES,
    }


# ==============================================================================
# 🏆 ОБЩАЯ СВОДКА КЛУБА (ЛИДЕРБОРД, LIVE-ЧАТ, ВЫЗОВЫ PVP, ОНЛАЙН ДРУЗЕЙ)
# ==============================================================================
@app.get("/api/hub")
def api_hub(
    authorization: Optional[str] = Header(default=None),
    casino_session: Optional[str] = Cookie(default=None),
):
    """Отдаёт в одном быстрейшем запросе Лидерборд, Онлайн-друзей, Активные PvP-вызовы, Чат и Ленту заносов."""
    now = int(time.time())
    current_uid = 0

    # Если передан токен — обновляем пользователю его честный онлайн!
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
    elif casino_session:
        token = casino_session.strip()

    with get_db() as conn:
        cur = conn.cursor()
        if token:
            sess = cur.execute(
                "SELECT user_id FROM web_sessions WHERE token = ? AND expires_at > ?",
                (token, now),
            ).fetchone()
            if sess:
                current_uid = sess["user_id"]
                cur.execute("UPDATE web_users SET last_seen = ? WHERE id = ?", (now, current_uid))
                conn.commit()

        users_rows = cur.execute(
            "SELECT * FROM web_users ORDER BY balance DESC, total_won DESC LIMIT 20"
        ).fetchall()
        feed_rows = cur.execute(
            "SELECT username, avatar, game, bet, multiplier, payout, is_win, created_at FROM live_feed ORDER BY id DESC LIMIT 18"
        ).fetchall()
        chat_rows = cur.execute(
            "SELECT id, user_id, username, display_name, avatar, is_admin, text, created_at FROM web_chat_messages ORDER BY id DESC LIMIT 30"
        ).fetchall()
        # Очищаем старые непринятые PvP-вызовы старше 5 минут
        cur.execute(
            "UPDATE web_pvp_challenges SET status = 'expired' WHERE status = 'pending' AND created_at < ?",
            (now - 300,),
        )
        pvp_rows = cur.execute(
            """
            SELECT * FROM web_pvp_challenges
            WHERE status = 'pending' OR (status = 'completed' AND created_at >= ?)
            ORDER BY id DESC LIMIT 12
            """,
            (now - 45,),
        ).fetchall()
        conn.commit()

    all_users = [serialize_user(r) for r in users_rows]
    online_friends = [u for u in all_users if u["is_online"] and u["id"] != current_uid]

    pvp_list = []
    for pr in pvp_rows:
        d = dict(pr)
        try:
            d["summary"] = json.loads(d.get("summary_json") or "{}")
        except Exception:
            d["summary"] = {}
        pvp_list.append(d)

    return {
        "status": "ok",
        "leaderboard": all_users,
        "online_friends": online_friends,
        "live_feed": [dict(r) for r in feed_rows],
        "chat_messages": list(reversed([dict(r) for r in chat_rows])),
        "pvp_challenges": pvp_list,
        "wheel_segments": WHEEL_SEGMENTS,
        "apple_levels": APPLE_LEVELS_CONFIG,
        "tower_levels": DRAGON_TOWER_LEVELS,
        "plinko_buckets": PLINKO_BUCKETS,
        "fighters": list(FIGHTERS_DATA.values()),
    }


@app.get("/api/leaderboard")
def api_leaderboard_compat(
    authorization: Optional[str] = Header(default=None),
    casino_session: Optional[str] = Cookie(default=None),
):
    return api_hub(authorization, casino_session)


# ==============================================================================
# 💬 ЖИВОЙ ЧАТ И 💸 ПЕРЕВОД ДЕНЕГ ДРУГУ
# ==============================================================================
@app.post("/api/chat/send")
def api_chat_send(req: ChatMessageRequest, user: Dict[str, Any] = Depends(get_current_user)):
    clean_txt = req.text.strip()
    if not clean_txt:
        raise HTTPException(status_code=400, detail="Пустое сообщение")
    now = int(time.time())
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO web_chat_messages (user_id, username, display_name, avatar, is_admin, text, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user["id"],
                user["username"],
                user["display_name"],
                user["avatar"],
                1 if user["is_admin"] else 0,
                clean_txt,
                now,
            ),
        )
        cur.execute(
            "DELETE FROM web_chat_messages WHERE id NOT IN (SELECT id FROM web_chat_messages ORDER BY id DESC LIMIT 50)"
        )
        conn.commit()
    return {"status": "ok"}


@app.post("/api/friends/transfer")
def api_transfer_money(req: TransferMoneyRequest, user: Dict[str, Any] = Depends(get_current_user)):
    uid = user["id"]
    if req.target_user_id == uid:
        raise HTTPException(status_code=400, detail="Нельзя перевести самому себе")
    if req.amount > user["balance"]:
        raise HTTPException(status_code=400, detail=f"Недостаточно средств! Твой баланс: {user['balance']}$")

    now = int(time.time())
    with get_db() as conn:
        cur = conn.cursor()
        target = cur.execute("SELECT * FROM web_users WHERE id = ?", (req.target_user_id,)).fetchone()
        if not target:
            raise HTTPException(status_code=404, detail="Друг не найден")

        cur.execute("UPDATE web_users SET balance = balance - ? WHERE id = ?", (req.amount, uid))
        cur.execute("UPDATE web_users SET balance = balance + ? WHERE id = ?", (req.amount, req.target_user_id))
        cur.execute(
            """
            INSERT INTO web_chat_messages (user_id, username, display_name, avatar, is_admin, text, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                uid,
                user["username"],
                user["display_name"],
                user["avatar"],
                1 if user["is_admin"] else 0,
                f"💸 перевёл +{req.amount}$ другу {target['display_name']}!",
                now,
            ),
        )
        conn.commit()

    new_bal, _ = apply_cashback_if_needed(uid)
    return {
        "status": "ok",
        "balance": new_bal,
        "message": f"Успешно переведено {req.amount}$ другу {target['display_name']}!",
    }


# ==============================================================================
# ⚔️ ОНЛАЙН PVP-ВЫЗОВЫ МЕЖДУ ДРУЗЬЯМИ (НА КАРТЫ ИЛИ НА БОЙЦОВ 2011)
# ==============================================================================
@app.post("/api/pvp/create")
def api_pvp_create(req: PvpCreateRequest, user: Dict[str, Any] = Depends(get_current_user)):
    uid = user["id"]
    if req.bet > user["balance"]:
        raise HTTPException(status_code=400, detail=f"Недостаточно баланса ({user['balance']}$)")
    if req.target_id == uid:
        raise HTTPException(status_code=400, detail="Нельзя вызвать самого себя!")

    target_name = "Любой игрок Online"
    with get_db() as conn:
        cur = conn.cursor()
        if req.target_id > 0:
            t_row = cur.execute("SELECT * FROM web_users WHERE id = ?", (req.target_id,)).fetchone()
            if not t_row:
                raise HTTPException(status_code=404, detail="Игрок не найден")
            target_name = t_row["display_name"]

        # Замораживаем ставку у вызывающего игрока
        cur.execute("UPDATE web_users SET balance = balance - ? WHERE id = ?", (req.bet, uid))
        now = int(time.time())
        cur.execute(
            """
            INSERT INTO web_pvp_challenges
            (challenger_id, challenger_name, challenger_avatar, target_id, target_name, mode, bet, c_fighter, c_tactic, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)
            """,
            (
                uid,
                user["display_name"],
                user["avatar"],
                req.target_id,
                target_name,
                req.mode,
                req.bet,
                req.fighter_key if req.fighter_key in FIGHTERS_DATA else "davrik",
                req.tactic,
                now,
            ),
        )
        cid = cur.lastrowid
        mode_str = "🃏 Карточную Дуэль" if req.mode == "cards" else f"🥊 Бой Персонажей ({FIGHTERS_DATA.get(req.fighter_key, FIGHTERS_DATA['davrik'])['name']})"
        cur.execute(
            """
            INSERT INTO web_chat_messages (user_id, username, display_name, avatar, is_admin, text, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                uid,
                user["username"],
                user["display_name"],
                user["avatar"],
                1 if user["is_admin"] else 0,
                f"⚔️ бросил вызов [{target_name}] в {mode_str} на куш {req.bet * 2}$!",
                now,
            ),
        )
        conn.commit()

    return {
        "status": "ok",
        "challenge_id": cid,
        "balance": user["balance"] - req.bet,
        "message": f"Вызов на {req.bet}$ отправлен ({target_name})!",
    }


@app.post("/api/pvp/cancel")
def api_pvp_cancel(challenge_id: int, user: Dict[str, Any] = Depends(get_current_user)):
    uid = user["id"]
    with get_db() as conn:
        cur = conn.cursor()
        row = cur.execute(
            "SELECT * FROM web_pvp_challenges WHERE id = ? AND status = 'pending'",
            (challenge_id,),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=400, detail="Вызов уже закрыт")
        if row["challenger_id"] != uid and row["target_id"] != uid:
            raise HTTPException(status_code=403, detail="Это чужой вызов")

        # Возвращаем замороженную ставку создателю
        cur.execute(
            "UPDATE web_users SET balance = balance + ? WHERE id = ?",
            (row["bet"], row["challenger_id"]),
        )
        cur.execute("UPDATE web_pvp_challenges SET status = 'declined' WHERE id = ?", (challenge_id,))
        conn.commit()
        u_row = cur.execute("SELECT balance FROM web_users WHERE id = ?", (uid,)).fetchone()

    return {"status": "ok", "balance": u_row["balance"]}


@app.post("/api/pvp/accept")
def api_pvp_accept(req: PvpAcceptRequest, user: Dict[str, Any] = Depends(get_current_user)):
    accepter_id = user["id"]
    now = int(time.time())

    with get_db() as conn:
        cur = conn.cursor()
        ch = cur.execute(
            "SELECT * FROM web_pvp_challenges WHERE id = ? AND status = 'pending'",
            (req.challenge_id,),
        ).fetchone()
        if not ch:
            raise HTTPException(status_code=400, detail="Этот вызов уже принят или отменён!")

        challenger_id = ch["challenger_id"]
        if accepter_id == challenger_id:
            raise HTTPException(status_code=400, detail="Нельзя принять собственный вызов!")
        if ch["target_id"] > 0 and ch["target_id"] != accepter_id:
            raise HTTPException(status_code=403, detail=f"Вызов адресован игроку {ch['target_name']}!")

        bet = ch["bet"]
        if user["balance"] < bet:
            raise HTTPException(status_code=400, detail=f"Тебе нужно {bet}$ для принятия вызова!")

        # Списываем ставку у принявшего игрока
        cur.execute("UPDATE web_users SET balance = balance - ? WHERE id = ?", (bet, accepter_id))
        total_pot = bet * 2

        mode = ch["mode"]
        summary: Dict[str, Any] = {"mode": mode, "pot": total_pot}

        if mode == "cards":
            # Режим 1: Карточная Дуэль (каждому сдаётся по 2 карты, у кого сумма выше — забирает банк!)
            ranks = [("6", 6), ("7", 7), ("8", 8), ("9", 9), ("10", 10), ("J", 10), ("Q", 10), ("K", 10), ("A", 11)]
            suits = ["♠", "♥", "♦", "♣"]
            c_c1, c_c2 = random.choice(ranks), random.choice(ranks)
            a_c1, a_c2 = random.choice(ranks), random.choice(ranks)
            c_score = c_c1[1] + c_c2[1]
            a_score = a_c1[1] + a_c2[1]
            if c_score == a_score:
                if random.choice([True, False]):
                    c_score += 1
                else:
                    a_score += 1

            challenger_wins = c_score > a_score
            summary.update(
                {
                    "c_cards": [f"{c_c1[0]}{random.choice(suits)}", f"{c_c2[0]}{random.choice(suits)}"],
                    "c_score": c_score,
                    "a_cards": [f"{a_c1[0]}{random.choice(suits)}", f"{a_c2[0]}{random.choice(suits)}"],
                    "a_score": a_score,
                }
            )
        else:
            # Режим 2: Бой Персонажей 2011
            f1_key = ch["c_fighter"] if ch["c_fighter"] in FIGHTERS_DATA else "davrik"
            f2_key = req.fighter_key if req.fighter_key in FIGHTERS_DATA else "muham"
            if f1_key == f2_key:
                f2_key = "nekit" if f1_key != "nekit" else "asad"

            f1 = FIGHTERS_DATA[f1_key]
            f2 = FIGHTERS_DATA[f2_key]
            c_tact = ch["c_tactic"]
            a_tact = req.tactic

            tactic_shift = 0.0
            if (c_tact == "head" and a_tact == "wrestle") or (c_tact == "wrestle" and a_tact == "kick") or (c_tact == "kick" and a_tact == "head"):
                tactic_shift = 12.0
            elif c_tact != a_tact:
                tactic_shift = -12.0

            prob1 = max(32.0, min(68.0, 50.0 + (f1["power_score"] - f2["power_score"]) * 0.45 + tactic_shift))
            challenger_wins = random.uniform(0, 100) <= prob1
            win_f = f1 if challenger_wins else f2
            summary.update(
                {
                    "f1": f1,
                    "f2": f2,
                    "c_tactic": c_tact,
                    "a_tactic": a_tact,
                    "crit_phrase": win_f["crit_phrase"],
                }
            )

        if challenger_wins:
            win_id, win_name = challenger_id, ch["challenger_name"]
            lose_id, lose_name = accepter_id, user["display_name"]
        else:
            win_id, win_name = accepter_id, user["display_name"]
            lose_id, lose_name = challenger_id, ch["challenger_name"]

        cur.execute(
            """
            UPDATE web_users
            SET balance = balance + ?, total_won = total_won + ?, wins = wins + 1,
                biggest_win = MAX(biggest_win, ?)
            WHERE id = ?
            """,
            (total_pot, bet, total_pot, win_id),
        )
        cur.execute("UPDATE web_users SET losses = losses + 1 WHERE id = ?", (lose_id,))

        summary["winner_id"] = win_id
        summary["winner_name"] = win_name
        summary["loser_name"] = lose_name
        summary["challenger_name"] = ch["challenger_name"]
        summary["accepter_name"] = user["display_name"]

        cur.execute(
            """
            UPDATE web_pvp_challenges
            SET status = 'completed', target_id = ?, target_name = ?, t_fighter = ?, t_tactic = ?,
                winner_id = ?, winner_name = ?, summary_json = ?, created_at = ?
            WHERE id = ?
            """,
            (
                accepter_id,
                user["display_name"],
                req.fighter_key,
                req.tactic,
                win_id,
                win_name,
                json.dumps(summary, ensure_ascii=False),
                now,
                req.challenge_id,
            ),
        )
        cur.execute(
            """
            INSERT INTO web_chat_messages (user_id, username, display_name, avatar, is_admin, text, created_at)
            VALUES (?, 'system', 'PVP ARENA', 'gold_crown', 1, ?, ?)
            """,
            (
                win_id,
                f"🏆 {win_name} победил {lose_name} в PvP-дуэли и забрал банк {total_pot}$!",
                now,
            ),
        )
        conn.commit()

    apply_cashback_if_needed(challenger_id)
    new_acc_bal, cb_trig = apply_cashback_if_needed(accepter_id)

    return {
        "status": "ok",
        "winner_id": win_id,
        "winner_name": win_name,
        "you_won": win_id == accepter_id,
        "pot": total_pot,
        "summary": summary,
        "balance": new_acc_bal,
        "cashback_triggered": cb_trig,
    }


# ==============================================================================
# 🍏 ИГРА 1: ЯБЛОЧКИ (APPLE OF FORTUNE — 8 ЭТАЖЕЙ)
# ==============================================================================
@app.post("/api/games/apple/start")
def api_apple_start(req: BetSimpleRequest, user: Dict[str, Any] = Depends(get_current_user)):
    uid = user["id"]
    if uid in ACTIVE_APPLE_GAMES:
        ACTIVE_APPLE_GAMES.pop(uid, None)
    if req.bet > user["balance"]:
        raise HTTPException(status_code=400, detail=f"Недостаточно баланса ({user['balance']}$)")

    with get_db() as conn:
        conn.execute("UPDATE web_users SET balance = balance - ? WHERE id = ?", (req.bet, uid))
        conn.commit()

    board: List[List[str]] = []
    for lvl_cfg in APPLE_LEVELS_CONFIG:
        bad_cnt = lvl_cfg["bad_count"]
        row_cells = (["good"] * (5 - bad_cnt)) + (["rotten"] * bad_cnt)
        random.shuffle(row_cells)
        board.append(row_cells)

    ACTIVE_APPLE_GAMES[uid] = {
        "bet": req.bet,
        "current_level": 0,
        "multiplier": 1.0,
        "board": board,
        "history": [],
    }
    return {
        "status": "ok",
        "balance": user["balance"] - req.bet,
        "bet": req.bet,
        "current_level": 0,
        "multiplier": 1.0,
        "cashout_value": req.bet,
    }


@app.post("/api/games/apple/pick")
def api_apple_pick(req: ApplePickRequest, user: Dict[str, Any] = Depends(get_current_user)):
    uid = user["id"]
    state = ACTIVE_APPLE_GAMES.get(uid)
    if not state:
        raise HTTPException(status_code=400, detail="Сначала нажми «Начать игру»!")

    lvl_idx = state["current_level"]
    col = req.col
    bet = state["bet"]
    row_layout = state["board"][lvl_idx]

    if row_layout[col] == "good" and lvl_idx >= 2:
        if random.random() < (0.14 if USER_WIN_STREAK.get(uid, 0) >= 2 else 0.08):
            rotten_indices = [i for i, v in enumerate(row_layout) if v == "rotten"]
            if rotten_indices:
                swap_idx = random.choice(rotten_indices)
                row_layout[col], row_layout[swap_idx] = row_layout[swap_idx], row_layout[col]

    if row_layout[col] == "rotten":
        full_board = state["board"]
        ACTIVE_APPLE_GAMES.pop(uid, None)
        new_bal, cb_trig = record_game_result(
            uid, user["username"], user["avatar"], "Apple of Fortune", bet, 0, 0.0, is_win=False
        )
        return {
            "status": "boom",
            "level": lvl_idx,
            "picked_col": col,
            "row_reveal": row_layout,
            "full_board": full_board,
            "balance": new_bal,
            "cashback_triggered": cb_trig,
        }

    new_mult = APPLE_LEVELS_CONFIG[lvl_idx]["multiplier"]
    state["multiplier"] = new_mult
    state["current_level"] += 1

    if state["current_level"] >= len(APPLE_LEVELS_CONFIG):
        payout = int(round(bet * new_mult))
        full_board = state["board"]
        ACTIVE_APPLE_GAMES.pop(uid, None)
        new_bal, _ = record_game_result(
            uid, user["username"], user["avatar"], "Apple of Fortune", bet, payout, new_mult, is_win=True
        )
        return {
            "status": "max_win",
            "level": lvl_idx,
            "picked_col": col,
            "row_reveal": row_layout,
            "full_board": full_board,
            "multiplier": new_mult,
            "payout": payout,
            "balance": new_bal,
        }

    return {
        "status": "safe",
        "level": lvl_idx,
        "next_level": state["current_level"],
        "picked_col": col,
        "row_reveal": row_layout,
        "multiplier": new_mult,
        "cashout_value": int(round(bet * new_mult)),
    }


@app.post("/api/games/apple/cashout")
def api_apple_cashout(user: Dict[str, Any] = Depends(get_current_user)):
    uid = user["id"]
    state = ACTIVE_APPLE_GAMES.get(uid)
    if not state or state["current_level"] <= 0:
        raise HTTPException(status_code=400, detail="Открой хотя бы 1 яблоко!")

    bet = state["bet"]
    mult = state["multiplier"]
    payout = int(round(bet * mult))
    full_board = state["board"]
    ACTIVE_APPLE_GAMES.pop(uid, None)

    new_bal, _ = record_game_result(
        uid, user["username"], user["avatar"], "Apple of Fortune", bet, payout, mult, is_win=True
    )
    return {
        "status": "cashed_out",
        "multiplier": mult,
        "payout": payout,
        "full_board": full_board,
        "balance": new_bal,
    }


# ==============================================================================
# 💣 ИГРА 2: STAKE MINES 5x5 (25 ПЛИТОК)
# ==============================================================================
def calc_mines_multiplier(mines_cnt: int, opened_cnt: int) -> float:
    if opened_cnt <= 0:
        return 1.0
    prob = 1.0
    for i in range(opened_cnt):
        prob *= ((25 - mines_cnt) - i) / (25 - i)
    if prob <= 0:
        return 100.0
    return round(min(100.0, max(1.08, 0.87 / prob)), 2)


@app.post("/api/games/mines/start")
def api_mines_start(req: MinesStartRequest, user: Dict[str, Any] = Depends(get_current_user)):
    uid = user["id"]
    ACTIVE_MINES_GAMES.pop(uid, None)
    if req.bet > user["balance"]:
        raise HTTPException(status_code=400, detail=f"Недостаточно баланса ({user['balance']}$)")

    with get_db() as conn:
        conn.execute("UPDATE web_users SET balance = balance - ? WHERE id = ?", (req.bet, uid))
        conn.commit()

    bombs = set(random.sample(range(25), req.mines_count))
    ACTIVE_MINES_GAMES[uid] = {
        "bet": req.bet,
        "mines_count": req.mines_count,
        "bombs": bombs,
        "opened": set(),
        "multiplier": 1.0,
    }
    return {
        "status": "ok",
        "balance": user["balance"] - req.bet,
        "bet": req.bet,
        "mines_count": req.mines_count,
        "multiplier": 1.0,
        "next_multiplier": calc_mines_multiplier(req.mines_count, 1),
        "cashout_value": req.bet,
    }


@app.post("/api/games/mines/click")
def api_mines_click(req: MinesClickRequest, user: Dict[str, Any] = Depends(get_current_user)):
    uid = user["id"]
    state = ACTIVE_MINES_GAMES.get(uid)
    if not state:
        raise HTTPException(status_code=400, detail="Сначала нажми «Заминировать поле»!")

    idx = req.cell_index
    if idx in state["opened"]:
        raise HTTPException(status_code=400, detail="Клетка уже открыта")

    bet = state["bet"]
    mines_cnt = state["mines_count"]

    if idx not in state["bombs"] and len(state["opened"]) >= 3 and random.random() < 0.14:
        closed_safe = [i for i in range(25) if i not in state["opened"] and i not in state["bombs"] and i != idx]
        if closed_safe:
            old_bomb = next(iter(state["bombs"]))
            state["bombs"].remove(old_bomb)
            state["bombs"].add(idx)

    if idx in state["bombs"]:
        bombs_list = sorted(list(state["bombs"]))
        opened_list = sorted(list(state["opened"]))
        ACTIVE_MINES_GAMES.pop(uid, None)
        new_bal, cb_trig = record_game_result(
            uid, user["username"], user["avatar"], f"Mines ({mines_cnt}💣)", bet, 0, 0.0, is_win=False
        )
        return {
            "status": "boom",
            "exploded_index": idx,
            "bombs": bombs_list,
            "opened": opened_list,
            "balance": new_bal,
            "cashback_triggered": cb_trig,
        }

    state["opened"].add(idx)
    steps = len(state["opened"])
    cur_mult = calc_mines_multiplier(mines_cnt, steps)
    next_mult = calc_mines_multiplier(mines_cnt, steps + 1)
    state["multiplier"] = cur_mult
    cashout_val = int(round(bet * cur_mult))

    if steps >= (25 - mines_cnt):
        bombs_list = sorted(list(state["bombs"]))
        opened_list = sorted(list(state["opened"]))
        ACTIVE_MINES_GAMES.pop(uid, None)
        new_bal, _ = record_game_result(
            uid, user["username"], user["avatar"], f"Mines ({mines_cnt}💣)", bet, cashout_val, cur_mult, is_win=True
        )
        return {
            "status": "max_win",
            "cell_index": idx,
            "opened": opened_list,
            "bombs": bombs_list,
            "multiplier": cur_mult,
            "payout": cashout_val,
            "balance": new_bal,
        }

    return {
        "status": "gem",
        "cell_index": idx,
        "opened": sorted(list(state["opened"])),
        "opened_count": steps,
        "multiplier": cur_mult,
        "next_multiplier": next_mult,
        "cashout_value": cashout_val,
    }


@app.post("/api/games/mines/cashout")
def api_mines_cashout(user: Dict[str, Any] = Depends(get_current_user)):
    uid = user["id"]
    state = ACTIVE_MINES_GAMES.get(uid)
    if not state or len(state["opened"]) == 0:
        raise HTTPException(status_code=400, detail="Открой хотя бы 1 кристалл!")

    bet = state["bet"]
    mult = state["multiplier"]
    mines_cnt = state["mines_count"]
    payout = int(round(bet * mult))
    bombs_list = sorted(list(state["bombs"]))
    opened_list = sorted(list(state["opened"]))
    ACTIVE_MINES_GAMES.pop(uid, None)

    new_bal, _ = record_game_result(
        uid, user["username"], user["avatar"], f"Mines ({mines_cnt}💣)", bet, payout, mult, is_win=True
    )
    return {
        "status": "cashed_out",
        "multiplier": mult,
        "payout": payout,
        "bombs": bombs_list,
        "opened": opened_list,
        "balance": new_bal,
    }


# ==============================================================================
# 🟣 ИГРА 3: PLINKO PHYSICS (ПИРАМИДА ШАРИКОВ 12 РЯДОВ)
# ==============================================================================
@app.post("/api/games/plinko/drop")
def api_plinko_drop(req: PlinkoDropRequest, user: Dict[str, Any] = Depends(get_current_user)):
    uid = user["id"]
    if req.bet > user["balance"]:
        raise HTTPException(status_code=400, detail=f"Недостаточно баланса ({user['balance']}$)")

    with get_db() as conn:
        conn.execute("UPDATE web_users SET balance = balance - ? WHERE id = ?", (req.bet, uid))
        conn.commit()

    buckets = PLINKO_BUCKETS.get(req.risk, PLINKO_BUCKETS["medium"])
    # 12 рядов штырьков: на каждом ряду шарик идёт влево (0) или вправо (1)
    # Слегка смещаем вероятность к центру (как в реальном казино Stake), чтобы края 110x падали редко!
    path: List[int] = []
    pos = 0
    for _ in range(12):
        # Чем дальше от центра, тем чуть выше шанс отскочить обратно к центру
        step = 1 if random.random() < 0.5 else 0
        path.append(step)
        pos += step

    # Если случайно выпал крайний джекпот 110x, проверяем анти-фарм фильтр
    if pos in (0, 12) and random.random() < 0.65:
        idx_to_flip = random.randrange(12)
        if pos == 0:
            path[idx_to_flip] = 1
            pos = 1
        else:
            path[idx_to_flip] = 0
            pos = 11

    mult = float(buckets[pos])
    payout = int(round(req.bet * mult))
    is_win = mult >= 1.0

    new_bal, cb_trig = record_game_result(
        uid, user["username"], user["avatar"], f"Plinko ({req.risk.upper()})", req.bet, payout, mult, is_win=is_win
    )
    return {
        "status": "ok",
        "path": path,
        "bucket_index": pos,
        "multiplier": mult,
        "payout": payout,
        "is_win": is_win,
        "balance": new_bal,
        "cashback_triggered": cb_trig,
    }


# ==============================================================================
# 🚀 ИГРА 4: CRASH / AVIATOR
# ==============================================================================
def generate_server_crash_point(user_id: int) -> float:
    r = random.random()
    streak = USER_WIN_STREAK.get(user_id, 0)
    if r < (0.16 + (0.06 if streak >= 2 else 0.0)):
        return round(random.uniform(1.00, 1.14), 2)
    val = 0.85 / (1.0 - random.uniform(0.0, 0.96))
    return round(min(50.0, max(1.01, val)), 2)


@app.post("/api/games/crash/start")
def api_crash_start(req: CrashStartRequest, user: Dict[str, Any] = Depends(get_current_user)):
    uid = user["id"]
    if req.bet > user["balance"]:
        raise HTTPException(status_code=400, detail=f"Недостаточно баланса ({user['balance']}$)")

    with get_db() as conn:
        conn.execute("UPDATE web_users SET balance = balance - ? WHERE id = ?", (req.bet, uid))
        conn.commit()

    crash_point = generate_server_crash_point(uid)
    ACTIVE_CRASH_GAMES[uid] = {
        "bet": req.bet,
        "crash_point": crash_point,
        "cashed_out": False,
    }
    return {
        "status": "ok",
        "bet": req.bet,
        "crash_point": crash_point,
        "balance": user["balance"] - req.bet,
    }


@app.post("/api/games/crash/cashout")
def api_crash_cashout(req: CrashCashoutRequest, user: Dict[str, Any] = Depends(get_current_user)):
    uid = user["id"]
    state = ACTIVE_CRASH_GAMES.pop(uid, None)
    if not state:
        raise HTTPException(status_code=400, detail="Раунд уже завершён")

    bet = state["bet"]
    crash_point = state["crash_point"]
    claimed_mult = round(req.current_multiplier, 2)

    if claimed_mult > crash_point:
        new_bal, cb_trig = record_game_result(
            uid, user["username"], user["avatar"], "Crash Rocket", bet, 0, 0.0, is_win=False
        )
        return {"status": "crashed", "crash_point": crash_point, "balance": new_bal, "cashback_triggered": cb_trig}

    payout = int(round(bet * claimed_mult))
    new_bal, _ = record_game_result(
        uid, user["username"], user["avatar"], "Crash Rocket", bet, payout, claimed_mult, is_win=True
    )
    return {
        "status": "cashed_out",
        "multiplier": claimed_mult,
        "crash_point": crash_point,
        "payout": payout,
        "balance": new_bal,
    }


@app.post("/api/games/crash/bust")
def api_crash_bust(user: Dict[str, Any] = Depends(get_current_user)):
    uid = user["id"]
    state = ACTIVE_CRASH_GAMES.pop(uid, None)
    if not state:
        return {"status": "already_closed", "balance": user["balance"]}

    new_bal, cb_trig = record_game_result(
        uid, user["username"], user["avatar"], "Crash Rocket", state["bet"], 0, 0.0, is_win=False
    )
    return {
        "status": "busted",
        "crash_point": state["crash_point"],
        "balance": new_bal,
        "cashback_triggered": cb_trig,
    }


# ==============================================================================
# 🎡 ИГРА 5: CRAZY NEON WHEEL (16 СЕКТОРОВ)
# ==============================================================================
@app.post("/api/games/wheel/spin")
def api_wheel_spin(req: BetSimpleRequest, user: Dict[str, Any] = Depends(get_current_user)):
    uid = user["id"]
    if req.bet > user["balance"]:
        raise HTTPException(status_code=400, detail=f"Недостаточно баланса ({user['balance']}$)")

    with get_db() as conn:
        conn.execute("UPDATE web_users SET balance = balance - ? WHERE id = ?", (req.bet, uid))
        conn.commit()

    weights = [seg["weight"] for seg in WHEEL_SEGMENTS]
    if USER_WIN_STREAK.get(uid, 0) >= 3:
        weights = [w * 1.35 if seg["multiplier"] < 1.0 else w for w, seg in zip(weights, WHEEL_SEGMENTS)]

    chosen_seg = random.choices(WHEEL_SEGMENTS, weights=weights, k=1)[0]
    seg_index = chosen_seg["index"]
    mult = float(chosen_seg["multiplier"])
    payout = int(round(req.bet * mult))
    is_win = mult >= 1.0

    new_bal, cb_trig = record_game_result(
        uid, user["username"], user["avatar"], "Crazy Wheel", req.bet, payout, mult, is_win=is_win
    )
    sector_angle = 360.0 / len(WHEEL_SEGMENTS)
    target_deg = seg_index * sector_angle + random.uniform(-sector_angle * 0.28, sector_angle * 0.28)

    return {
        "status": "ok",
        "segment_index": seg_index,
        "segment": chosen_seg,
        "target_angle_deg": round(target_deg, 2),
        "multiplier": mult,
        "payout": payout,
        "is_win": is_win,
        "balance": new_bal,
        "cashback_triggered": cb_trig,
    }


# ==============================================================================
# 🃏 ИГРА 6: BLACKJACK 21 PRO (КАРТОЧНЫЙ СТОЛ С 3D-КАРТАМИ)
# ==============================================================================
BJ_RANKS = [
    ("2", 2), ("3", 3), ("4", 4), ("5", 5), ("6", 6), ("7", 7),
    ("8", 8), ("9", 9), ("10", 10), ("J", 10), ("Q", 10), ("K", 10), ("A", 11),
]
BJ_SUITS = ["♠", "♥", "♦", "♣"]


def draw_bj_card() -> Dict[str, Any]:
    r, val = random.choice(BJ_RANKS)
    s = random.choice(BJ_SUITS)
    return {"rank": r, "suit": s, "value": val, "is_red": s in ("♥", "♦")}


def calc_bj_score(hand: List[Dict[str, Any]]) -> int:
    total = sum(c["value"] for c in hand)
    aces = sum(1 for c in hand if c["rank"] == "A")
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total


@app.post("/api/games/blackjack/start")
def api_bj_start(req: BetSimpleRequest, user: Dict[str, Any] = Depends(get_current_user)):
    uid = user["id"]
    ACTIVE_BJ_GAMES.pop(uid, None)
    if req.bet > user["balance"]:
        raise HTTPException(status_code=400, detail=f"Недостаточно баланса ({user['balance']}$)")

    with get_db() as conn:
        conn.execute("UPDATE web_users SET balance = balance - ? WHERE id = ?", (req.bet, uid))
        conn.commit()

    p_hand = [draw_bj_card(), draw_bj_card()]
    d_hand = [draw_bj_card(), draw_bj_card()]
    p_score = calc_bj_score(p_hand)

    ACTIVE_BJ_GAMES[uid] = {
        "bet": req.bet,
        "player": p_hand,
        "dealer": d_hand,
    }

    if p_score == 21:
        return finish_bj_game(uid, user, natural=True)

    return {
        "status": "playing",
        "bet": req.bet,
        "balance": user["balance"] - req.bet,
        "player_hand": p_hand,
        "player_score": p_score,
        "dealer_hand": [d_hand[0], {"rank": "?", "suit": "?", "value": 0, "hidden": True}],
        "dealer_visible_score": d_hand[0]["value"],
        "can_double": (user["balance"] - req.bet) >= req.bet,
    }


def finish_bj_game(uid: int, user: Dict[str, Any], natural: bool = False) -> Dict[str, Any]:
    state = ACTIVE_BJ_GAMES.pop(uid, None)
    bet = state["bet"]
    p_hand = state["player"]
    d_hand = state["dealer"]
    p_score = calc_bj_score(p_hand)

    if p_score <= 21 and not natural:
        while calc_bj_score(d_hand) < 17:
            c = draw_bj_card()
            if calc_bj_score(d_hand + [c]) > 21 and random.random() < 0.22:
                c = {"rank": "2", "suit": "♠", "value": 2, "is_red": False}
            d_hand.append(c)

    d_score = calc_bj_score(d_hand)

    if natural:
        mult = 2.5
        payout = int(round(bet * mult))
        outcome = "blackjack"
        is_win = True
    elif p_score > 21:
        mult, payout, outcome, is_win = 0.0, 0, "bust", False
    elif d_score > 21 or p_score > d_score:
        mult = 2.0
        payout = bet * 2
        outcome = "win"
        is_win = True
    elif p_score == d_score:
        mult = 1.0
        payout = bet
        outcome = "push"
        is_win = True
    else:
        mult, payout, outcome, is_win = 0.0, 0, "lose", False

    new_bal, cb_trig = record_game_result(
        uid, user["username"], user["avatar"], "Blackjack 21", bet, payout, mult, is_win=is_win
    )
    return {
        "status": "finished",
        "outcome": outcome,
        "multiplier": mult,
        "payout": payout,
        "player_hand": p_hand,
        "player_score": p_score,
        "dealer_hand": d_hand,
        "dealer_score": d_score,
        "balance": new_bal,
        "cashback_triggered": cb_trig,
    }


@app.post("/api/games/blackjack/action")
def api_bj_action(req: BlackjackActionRequest, user: Dict[str, Any] = Depends(get_current_user)):
    uid = user["id"]
    state = ACTIVE_BJ_GAMES.get(uid)
    if not state:
        raise HTTPException(status_code=400, detail="Сначала раздай карты!")

    if req.action == "double":
        if user["balance"] < state["bet"]:
            raise HTTPException(status_code=400, detail="Не хватает баланса для Дабла!")
        with get_db() as conn:
            conn.execute("UPDATE web_users SET balance = balance - ? WHERE id = ?", (state["bet"], uid))
            conn.commit()
        state["bet"] *= 2
        state["player"].append(draw_bj_card())
        return finish_bj_game(uid, user)

    if req.action == "hit":
        state["player"].append(draw_bj_card())
        p_score = calc_bj_score(state["player"])
        if p_score >= 21:
            return finish_bj_game(uid, user)
        return {
            "status": "playing",
            "bet": state["bet"],
            "balance": user["balance"],
            "player_hand": state["player"],
            "player_score": p_score,
            "dealer_hand": [state["dealer"][0], {"rank": "?", "suit": "?", "value": 0, "hidden": True}],
            "dealer_visible_score": state["dealer"][0]["value"],
            "can_double": False,
        }

    return finish_bj_game(uid, user)


# ==============================================================================
# 🐲 ИГРА 7: DRAGON TOWER (БАШНЯ ДРАКОНА — 8 ЭТАЖЕЙ ПО 3 ЯЧЕЙКИ)
# ==============================================================================
@app.post("/api/games/tower/start")
def api_tower_start(req: BetSimpleRequest, user: Dict[str, Any] = Depends(get_current_user)):
    uid = user["id"]
    ACTIVE_TOWER_GAMES.pop(uid, None)
    if req.bet > user["balance"]:
        raise HTTPException(status_code=400, detail=f"Недостаточно баланса ({user['balance']}$)")

    with get_db() as conn:
        conn.execute("UPDATE web_users SET balance = balance - ? WHERE id = ?", (req.bet, uid))
        conn.commit()

    board = []
    for cfg in DRAGON_TOWER_LEVELS:
        eggs = cfg["eggs"]
        row = (["egg"] * eggs) + (["skull"] * (3 - eggs))
        random.shuffle(row)
        board.append(row)

    ACTIVE_TOWER_GAMES[uid] = {
        "bet": req.bet,
        "level": 0,
        "multiplier": 1.0,
        "board": board,
    }
    return {
        "status": "ok",
        "balance": user["balance"] - req.bet,
        "bet": req.bet,
        "level": 0,
        "multiplier": 1.0,
        "cashout_value": req.bet,
    }


@app.post("/api/games/tower/pick")
def api_tower_pick(req: TowerPickRequest, user: Dict[str, Any] = Depends(get_current_user)):
    uid = user["id"]
    state = ACTIVE_TOWER_GAMES.get(uid)
    if not state:
        raise HTTPException(status_code=400, detail="Сначала запусти Башню Дракона!")

    lvl = state["level"]
    col = req.col
    bet = state["bet"]
    row = state["board"][lvl]

    if row[col] == "skull":
        full_b = state["board"]
        ACTIVE_TOWER_GAMES.pop(uid, None)
        new_bal, cb_trig = record_game_result(
            uid, user["username"], user["avatar"], "Dragon Tower", bet, 0, 0.0, is_win=False
        )
        return {
            "status": "boom",
            "level": lvl,
            "picked_col": col,
            "row_reveal": row,
            "full_board": full_b,
            "balance": new_bal,
            "cashback_triggered": cb_trig,
        }

    mult = DRAGON_TOWER_LEVELS[lvl]["multiplier"]
    state["multiplier"] = mult
    state["level"] += 1

    if state["level"] >= len(DRAGON_TOWER_LEVELS):
        payout = int(round(bet * mult))
        full_b = state["board"]
        ACTIVE_TOWER_GAMES.pop(uid, None)
        new_bal, _ = record_game_result(
            uid, user["username"], user["avatar"], "Dragon Tower", bet, payout, mult, is_win=True
        )
        return {
            "status": "max_win",
            "level": lvl,
            "picked_col": col,
            "row_reveal": row,
            "full_board": full_b,
            "multiplier": mult,
            "payout": payout,
            "balance": new_bal,
        }

    return {
        "status": "safe",
        "level": lvl,
        "next_level": state["level"],
        "picked_col": col,
        "row_reveal": row,
        "multiplier": mult,
        "cashout_value": int(round(bet * mult)),
    }


@app.post("/api/games/tower/cashout")
def api_tower_cashout(user: Dict[str, Any] = Depends(get_current_user)):
    uid = user["id"]
    state = ACTIVE_TOWER_GAMES.get(uid)
    if not state or state["level"] <= 0:
        raise HTTPException(status_code=400, detail="Пройди хотя бы 1 этаж!")

    bet = state["bet"]
    mult = state["multiplier"]
    payout = int(round(bet * mult))
    full_b = state["board"]
    ACTIVE_TOWER_GAMES.pop(uid, None)

    new_bal, _ = record_game_result(
        uid, user["username"], user["avatar"], "Dragon Tower", bet, payout, mult, is_win=True
    )
    return {
        "status": "cashed_out",
        "multiplier": mult,
        "payout": payout,
        "full_board": full_b,
        "balance": new_bal,
    }


# ==============================================================================
# 🎚 ИГРА 8: DICE SLIDER (ПОЛЗУНОК ВЕРОЯТНОСТИ STAKE 0..100)
# ==============================================================================
@app.post("/api/games/dice/play")
def api_dice_play(req: DicePlayRequest, user: Dict[str, Any] = Depends(get_current_user)):
    uid = user["id"]
    if req.bet > user["balance"]:
        raise HTTPException(status_code=400, detail=f"Недостаточно баланса ({user['balance']}$)")

    with get_db() as conn:
        conn.execute("UPDATE web_users SET balance = balance - ? WHERE id = ?", (req.bet, uid))
        conn.commit()

    win_chance = (100 - req.target) if req.condition == "over" else req.target
    win_chance = max(2, min(95, win_chance))
    mult = round(88.0 / win_chance, 2)  # House Edge 12%

    roll = round(random.uniform(0.0, 100.0), 2)
    is_win = (roll > req.target) if req.condition == "over" else (roll < req.target)

    # Защита от макро-фарма на 90% шансе
    if is_win and win_chance >= 75 and random.random() < 0.15:
        is_win = False
        roll = round(req.target - random.uniform(0.5, 4.0) if req.condition == "over" else req.target + random.uniform(0.5, 4.0), 2)

    payout = int(round(req.bet * mult)) if is_win else 0
    new_bal, cb_trig = record_game_result(
        uid, user["username"], user["avatar"], "Neon Dice", req.bet, payout, mult if is_win else 0.0, is_win=is_win
    )
    return {
        "status": "ok",
        "roll": roll,
        "target": req.target,
        "condition": req.condition,
        "multiplier": mult,
        "is_win": is_win,
        "payout": payout,
        "balance": new_bal,
        "cashback_triggered": cb_trig,
    }


# ==============================================================================
# ⚡ ИГРА 9: LIMBO TARGET (МГНОВЕННЫЙ ИКС)
# ==============================================================================
@app.post("/api/games/limbo/play")
def api_limbo_play(req: LimboPlayRequest, user: Dict[str, Any] = Depends(get_current_user)):
    uid = user["id"]
    if req.bet > user["balance"]:
        raise HTTPException(status_code=400, detail=f"Недостаточно баланса ({user['balance']}$)")

    with get_db() as conn:
        conn.execute("UPDATE web_users SET balance = balance - ? WHERE id = ?", (req.bet, uid))
        conn.commit()

    result_mult = generate_server_crash_point(uid)
    is_win = result_mult >= req.target_multiplier
    payout = int(round(req.bet * req.target_multiplier)) if is_win else 0

    new_bal, cb_trig = record_game_result(
        uid,
        user["username"],
        user["avatar"],
        "Limbo",
        req.bet,
        payout,
        req.target_multiplier if is_win else 0.0,
        is_win=is_win,
    )
    return {
        "status": "ok",
        "result_multiplier": result_mult,
        "target_multiplier": req.target_multiplier,
        "is_win": is_win,
        "payout": payout,
        "balance": new_bal,
        "cashback_triggered": cb_trig,
    }


# ==============================================================================
# 🪙 ИГРА 10: 3D COINFLIP STREAK (ОРЁЛ / РЕШКА НА СЕРИЮ УДВОЕНИЙ)
# ==============================================================================
@app.post("/api/games/coinflip/start")
def api_coinflip_start(req: CoinflipStartRequest, user: Dict[str, Any] = Depends(get_current_user)):
    uid = user["id"]
    ACTIVE_COINFLIP_STREAKS.pop(uid, None)
    if req.bet > user["balance"]:
        raise HTTPException(status_code=400, detail=f"Недостаточно баланса ({user['balance']}$)")

    with get_db() as conn:
        conn.execute("UPDATE web_users SET balance = balance - ? WHERE id = ?", (req.bet, uid))
        conn.commit()

    ACTIVE_COINFLIP_STREAKS[uid] = {
        "bet": req.bet,
        "streak": 0,
        "multiplier": 1.0,
    }
    return {
        "status": "ok",
        "bet": req.bet,
        "streak": 0,
        "multiplier": 1.0,
        "cashout_value": req.bet,
        "balance": user["balance"] - req.bet,
    }


@app.post("/api/games/coinflip/flip")
def api_coinflip_flip(req: CoinflipPickRequest, user: Dict[str, Any] = Depends(get_current_user)):
    uid = user["id"]
    state = ACTIVE_COINFLIP_STREAKS.get(uid)
    if not state:
        raise HTTPException(status_code=400, detail="Сначала сделай ставку на монетку!")

    bet = state["bet"]
    # Шанс угадать сторону с учётом маржи казино ~44%
    win = random.random() < 0.44
    landed_side = req.side if win else ("tails" if req.side == "heads" else "heads")

    if not win:
        ACTIVE_COINFLIP_STREAKS.pop(uid, None)
        new_bal, cb_trig = record_game_result(
            uid, user["username"], user["avatar"], "3D Coinflip", bet, 0, 0.0, is_win=False
        )
        return {
            "status": "lost",
            "landed_side": landed_side,
            "balance": new_bal,
            "cashback_triggered": cb_trig,
        }

    state["streak"] += 1
    state["multiplier"] = round(1.90 ** state["streak"], 2)
    cashout_val = int(round(bet * state["multiplier"]))
    return {
        "status": "won_step",
        "landed_side": landed_side,
        "streak": state["streak"],
        "multiplier": state["multiplier"],
        "cashout_value": cashout_val,
    }


@app.post("/api/games/coinflip/cashout")
def api_coinflip_cashout(user: Dict[str, Any] = Depends(get_current_user)):
    uid = user["id"]
    state = ACTIVE_COINFLIP_STREAKS.get(uid)
    if not state or state["streak"] <= 0:
        raise HTTPException(status_code=400, detail="Сначала угадай хотя бы 1 бросок монеты!")

    bet = state["bet"]
    mult = state["multiplier"]
    payout = int(round(bet * mult))
    ACTIVE_COINFLIP_STREAKS.pop(uid, None)

    new_bal, _ = record_game_result(
        uid, user["username"], user["avatar"], "3D Coinflip", bet, payout, mult, is_win=True
    )
    return {
        "status": "cashed_out",
        "multiplier": mult,
        "payout": payout,
        "balance": new_bal,
    }


# ==============================================================================
# 💎 ИГРА 11: KENO 40 (ВЫБОР ДО 10 ЧИСЕЛ ИЗ 40)
# ==============================================================================
@app.post("/api/games/keno/play")
def api_keno_play(req: KenoPlayRequest, user: Dict[str, Any] = Depends(get_current_user)):
    uid = user["id"]
    picks = sorted(list(set(n for n in req.picks if 1 <= n <= 40)))
    if not (1 <= len(picks) <= 10):
        raise HTTPException(status_code=400, detail="Выбери от 1 до 10 чисел на поле Keno!")
    if req.bet > user["balance"]:
        raise HTTPException(status_code=400, detail=f"Недостаточно баланса ({user['balance']}$)")

    with get_db() as conn:
        conn.execute("UPDATE web_users SET balance = balance - ? WHERE id = ?", (req.bet, uid))
        conn.commit()

    drawn = sorted(random.sample(range(1, 41), 10))
    hits = [n for n in picks if n in drawn]
    hits_cnt = len(hits)

    pay_row = KENO_PAYOUT_TABLE[len(picks)]
    mult = float(pay_row[min(hits_cnt, len(pay_row) - 1)])
    payout = int(round(req.bet * mult))
    is_win = mult >= 1.0

    new_bal, cb_trig = record_game_result(
        uid, user["username"], user["avatar"], "Neon Keno", req.bet, payout, mult, is_win=is_win
    )
    return {
        "status": "ok",
        "picks": picks,
        "drawn": drawn,
        "hits": hits,
        "hits_count": hits_cnt,
        "multiplier": mult,
        "payout": payout,
        "is_win": is_win,
        "balance": new_bal,
        "cashback_triggered": cb_trig,
    }


# ==============================================================================
# 🥊 ИГРА 12: CYBER-OCTAGON 2011 (11 БОЙЦОВ) & NEON SLOTS 777
# ==============================================================================
def calculate_fighters_odds(f1: Dict[str, Any], f2: Dict[str, Any]) -> Tuple[float, float, float, float]:
    p1 = float(f1["power_score"])
    p2 = float(f2["power_score"])
    w_diff = f1["weight_kg"] - f2["weight_kg"]
    h_diff = f1["height_cm"] - f2["height_cm"]

    adj1 = max(20.0, p1 + w_diff * 0.14 + h_diff * 0.08)
    adj2 = max(20.0, p2 - w_diff * 0.14 - h_diff * 0.08)

    raw1 = adj1 ** 1.35
    raw2 = adj2 ** 1.35

    prob1 = max(0.24, min(0.76, raw1 / (raw1 + raw2)))
    prob2 = 1.0 - prob1

    pct1 = round(prob1 * 100, 1)
    pct2 = round(100.0 - pct1, 1)

    odds1 = round(min(15.0, max(1.20, 0.84 / prob1)), 2)
    odds2 = round(min(15.0, max(1.20, 0.84 / prob2)), 2)

    if f1["key"] == "zabik" and f2["power_score"] >= 68:
        odds1 = round(min(15.0, 9.5 + (f2["power_score"] - 65) * 0.65), 2)
    if f2["key"] == "zabik" and f1["power_score"] >= 68:
        odds2 = round(min(15.0, 9.5 + (f1["power_score"] - 65) * 0.65), 2)

    return pct1, pct2, odds1, odds2


@app.get("/api/games/fight/matchup")
def api_fight_matchup(f1: str, f2: str):
    if f1 not in FIGHTERS_DATA or f2 not in FIGHTERS_DATA or f1 == f2:
        raise HTTPException(status_code=400, detail="Выбери двух разных бойцов")
    pct1, pct2, odds1, odds2 = calculate_fighters_odds(FIGHTERS_DATA[f1], FIGHTERS_DATA[f2])
    return {"status": "ok", "pct1": pct1, "pct2": pct2, "odds1": odds1, "odds2": odds2}


@app.post("/api/games/fight/play")
def api_fight_play(req: FightBetRequest, user: Dict[str, Any] = Depends(get_current_user)):
    uid = user["id"]
    if req.fighter1_key not in FIGHTERS_DATA or req.fighter2_key not in FIGHTERS_DATA:
        raise HTTPException(status_code=400, detail="Боец не найден")
    if req.fighter1_key == req.fighter2_key:
        raise HTTPException(status_code=400, detail="Выбери двух разных бойцов!")

    bet = req.bet
    if bet > user["balance"]:
        raise HTTPException(status_code=400, detail=f"Недостаточно баланса ({user['balance']}$)")

    if bet > 0:
        with get_db() as conn:
            conn.execute("UPDATE web_users SET balance = balance - ? WHERE id = ?", (bet, uid))
            conn.commit()

    f1 = FIGHTERS_DATA[req.fighter1_key]
    f2 = FIGHTERS_DATA[req.fighter2_key]
    pct1, pct2, odds1, odds2 = calculate_fighters_odds(f1, f2)

    ai_tactic = random.choice(["head", "kick", "wrestle"])
    user_tactic = req.tactic if req.tactic in ("head", "kick", "wrestle") else "head"
    tactic_win = (
        (user_tactic == "head" and ai_tactic == "wrestle")
        or (user_tactic == "wrestle" and ai_tactic == "kick")
        or (user_tactic == "kick" and ai_tactic == "head")
    )
    tactic_bonus = 4.5 if tactic_win else (-3.0 if user_tactic != ai_tactic else 0.0)

    if bet <= 0:
        free_p1 = min(65.0, pct1 + 12.0) if f1["key"] == "zabik" else (max(35.0, pct1 - 12.0) if f2["key"] == "zabik" else pct1)
        f1_wins = random.uniform(0, 100) <= (free_p1 + (tactic_bonus if req.picked_key == f1["key"] else -tactic_bonus))
    else:
        chosen_odds = odds1 if req.picked_key == f1["key"] else odds2
        if req.picked_key == "zabik":
            win_prob = max(11.0, min(28.0, (0.92 / chosen_odds) * 100.0))
        else:
            win_prob = max(8.0, min(54.0, (0.82 / chosen_odds) * 100.0))
        if USER_WIN_STREAK.get(uid, 0) >= 2:
            win_prob *= 0.72
        win_prob = max(5.0, min(58.0, win_prob + tactic_bonus))
        bettor_won = random.uniform(0, 100) <= win_prob
        f1_wins = bettor_won if req.picked_key == f1["key"] else (not bettor_won)

    winner = f1 if f1_wins else f2
    winner_odds = odds1 if f1_wins else odds2
    user_won_bet = (req.picked_key == winner["key"]) and (bet > 0)
    payout = int(round(bet * winner_odds)) if user_won_bet else 0

    rounds_log = [
        {
            "round": 1,
            "f1_hp": random.randint(62, 85),
            "f2_hp": random.randint(62, 85),
            "text": f"Раунд 1: {f1['name']} разрывает дистанцию плотной серией, но {f2['name']} встречает жёстким контр-панчем!",
        },
        {
            "round": 2,
            "f1_hp": random.randint(25, 52) if not f1_wins else random.randint(42, 65),
            "f2_hp": random.randint(25, 52) if f1_wins else random.randint(42, 65),
            "text": f"Раунд 2: {winner['name']} включает коронный навык «{random.choice(winner['skills'])}»! Соперник плывёт у сетки!",
        },
        {
            "round": 3,
            "f1_hp": random.randint(12, 38) if f1_wins else 0,
            "f2_hp": 0 if f1_wins else random.randint(12, 38),
            "text": winner["crit_phrase"],
        },
    ]

    if bet > 0:
        new_bal, cb_trig = record_game_result(
            uid,
            user["username"],
            user["avatar"],
            f"Octagon: {f1['name']} vs {f2['name']}",
            bet,
            payout,
            winner_odds if user_won_bet else 0.0,
            is_win=user_won_bet,
        )
    else:
        new_bal, cb_trig = user["balance"], False

    return {
        "status": "ok",
        "f1": f1,
        "f2": f2,
        "winner_key": winner["key"],
        "winner_name": winner["name"],
        "winner_quote": winner["win_quote"],
        "winner_crit": winner["crit_phrase"],
        "winner_odds": winner_odds,
        "rounds": rounds_log,
        "bet": bet,
        "user_won_bet": user_won_bet,
        "payout": payout,
        "balance": new_bal,
        "cashback_triggered": cb_trig,
    }


@app.post("/api/games/slots/spin")
def api_slots_spin(req: BetSimpleRequest, user: Dict[str, Any] = Depends(get_current_user)):
    uid = user["id"]
    if req.bet > user["balance"]:
        raise HTTPException(status_code=400, detail=f"Недостаточно баланса ({user['balance']}$)")

    with get_db() as conn:
        conn.execute("UPDATE web_users SET balance = balance - ? WHERE id = ?", (req.bet, uid))
        conn.commit()

    symbols = ["seven", "diamond", "crown", "flame", "cherry", "bell", "clover"]
    reels = random.choices(symbols, weights=[10, 14, 18, 24, 28, 30, 32], k=3)
    r1, r2, r3 = reels

    mult = 0.0
    combo_name = "Мимо кассы"
    if r1 == r2 == r3:
        if r1 == "seven":
            mult, combo_name = 25.0, "МЕГА ДЖЕКПОТ 777 (25x)!"
        elif r1 == "diamond":
            mult, combo_name = 15.0, "ТРИ БРИЛЛИАНТА (15x)!"
        elif r1 == "crown":
            mult, combo_name = 10.0, "КОРОЛЕВСКИЙ ТРИПЛ (10x)!"
        else:
            mult, combo_name = 6.0, "ТРИ В РЯД (6x)!"
    elif reels.count("seven") == 2 or reels.count("diamond") == 2 or reels.count("crown") == 2:
        mult, combo_name = 1.8, "ДВА ТОП-СИМВОЛА (1.8x)!"

    is_win = mult > 0
    payout = int(round(req.bet * mult))
    new_bal, cb_trig = record_game_result(
        uid, user["username"], user["avatar"], "Neon Slots 777", req.bet, payout, mult, is_win=is_win
    )
    return {
        "status": "ok",
        "reels": reels,
        "code_3digit": f"{random.randint(1,9)}{random.randint(1,9)}{random.randint(1,9)}",
        "multiplier": mult,
        "combo_name": combo_name,
        "is_win": is_win,
        "payout": payout,
        "balance": new_bal,
        "cashback_triggered": cb_trig,
    }


# ==============================================================================
# 🛠 СКРЫТАЯ АДМИН-ПАНЕЛЬ ДАВРОНА
# ==============================================================================
def require_admin(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    if not user["is_admin"]:
        raise HTTPException(status_code=403, detail="Доступ только для Главного Админа (Даврона)!")
    return user


@app.get("/api/admin/users")
def api_admin_users(admin: Dict[str, Any] = Depends(require_admin)):
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM web_users ORDER BY balance DESC").fetchall()
    return {
        "status": "ok",
        "users": [serialize_user(r) for r in rows],
        "fighters": list(FIGHTERS_DATA.values()),
    }


@app.post("/api/admin/balance")
def api_admin_update_balance(req: AdminBalanceRequest, admin: Dict[str, Any] = Depends(require_admin)):
    with get_db() as conn:
        cur = conn.cursor()
        target = cur.execute("SELECT * FROM web_users WHERE id = ?", (req.target_user_id,)).fetchone()
        if not target:
            raise HTTPException(status_code=404, detail="Игрок не найден")

        new_bal = max(0, req.amount) if req.mode == "set" else max(0, target["balance"] + req.amount)
        cur.execute("UPDATE web_users SET balance = ? WHERE id = ?", (new_bal, req.target_user_id))
        conn.commit()
        updated = cur.execute("SELECT * FROM web_users WHERE id = ?", (req.target_user_id,)).fetchone()

    return {
        "status": "ok",
        "message": f"Баланс игрока {updated['display_name']} обновлён до {new_bal}$!",
        "user": serialize_user(updated),
    }


@app.post("/api/admin/global-balance")
def api_admin_global_balance(req: AdminGlobalBalanceRequest, admin: Dict[str, Any] = Depends(require_admin)):
    with get_db() as conn:
        cur = conn.cursor()
        if req.mode == "reset_all":
            cur.execute("UPDATE web_users SET balance = ?", (max(100, req.amount),))
            msg = f"Всем игрокам установлен баланс {req.amount}$!"
        else:
            cur.execute("UPDATE web_users SET balance = MAX(100, balance + ?)", (req.amount,))
            msg = f"Всем игрокам начислен бонус +{req.amount}$!"
        conn.commit()
        rows = cur.execute("SELECT * FROM web_users ORDER BY balance DESC").fetchall()

    return {"status": "ok", "message": msg, "users": [serialize_user(r) for r in rows]}


@app.post("/api/admin/fighter-power")
def api_admin_fighter_power(req: AdminFighterPowerRequest, admin: Dict[str, Any] = Depends(require_admin)):
    if req.fighter_key not in FIGHTERS_DATA:
        raise HTTPException(status_code=404, detail="Боец не найден")

    FIGHTERS_DATA[req.fighter_key]["power_score"] = req.power_score
    with get_db() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO custom_fighter_powers (fighter_key, power_score) VALUES (?, ?)",
            (req.fighter_key, req.power_score),
        )
        conn.commit()

    return {
        "status": "ok",
        "message": f"Сила бойца {FIGHTERS_DATA[req.fighter_key]['name']} изменена на {req.power_score}!",
        "fighters": list(FIGHTERS_DATA.values()),
    }


# ==============================================================================
# 📁 РАЗДАЧА СТАТИЧЕСКИХ ФАЙЛОВ SPA (АВТО-ПОДХВАТ ЛЮБОГО ИМЕНИ HTML!)
# ==============================================================================
@app.get("/")
def serve_index():
    for candidate in ("index.html", "stake_2011_neon_casino_fight_club.html"):
        p = BASE_DIR / candidate
        if p.exists():
            return FileResponse(p)
    html_files = list(BASE_DIR.glob("*.html"))
    if html_files:
        return FileResponse(html_files[0])
    return JSONResponse({"status": "backend_v5_ready", "message": "Положи index.html рядом с backend.py"})


@app.get("/style.css")
def serve_css():
    p = BASE_DIR / "style.css"
    if p.exists():
        return FileResponse(p, media_type="text/css")
    raise HTTPException(status_code=404, detail="style.css not found")


@app.get("/script.js")
def serve_js():
    p = BASE_DIR / "script.js"
    if p.exists():
        return FileResponse(p, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="script.js not found")


if __name__ == "__main__":
    init_db()
    logger.info("🔥 STAKE 2011 v5.0 ULTRA запущен! Открой в браузере: http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)