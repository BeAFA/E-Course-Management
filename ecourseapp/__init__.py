import json
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from google import genai

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:root@localhost/ecoursedb?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["SECRET_KEY"] = '8f3a4c1e7d9b2a6f8e4c3d1a9b7e5f6c8d0a1b2c3d4e5f60718293a4b5c6d7'

AI_API_KEY = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ecourseapp\\credentials", "ai_api_key.json")
with open(AI_API_KEY, "r", encoding="utf-8") as f:
    AI_CONFIG = json.load(f)
GEMINI_API_KEY = AI_CONFIG['GEMINI_API_KEY']
GEMINI_MODEL = AI_CONFIG["GEMINI_MODEL"]

if not GEMINI_API_KEY:
    raise RuntimeError("Chưa thiết lập GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_INSTRUCTION = "Bạn là một trợ lý AI thân thiện, trả lời ngắn gọn, rõ ràng bằng tiếng Việt."

db = SQLAlchemy(app)
login = LoginManager(app)
