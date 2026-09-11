from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
import os

load_dotenv() 

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:root@localhost/ecoursedb?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

app.config["SECRET_KEY"] = '8f3a4c1e7d9b2a6f8e4c3d1a9b7e5f6c8d0a1b2c3d4e5f60718293a4b5c6d7'

db = SQLAlchemy(app)
login = LoginManager(app)


VNPAY_CONFIG = {
    "vnp_TmnCode": os.environ.get("VNPAY_TMN_CODE"),
    "vnp_HashSecret": os.environ.get("VNPAY_HASH_SECRET"),
    "vnp_Url": os.environ.get("VNPAY_URL"),
    "vnp_ReturnUrl": os.environ.get("VNPAY_RETURN_URL")
}

