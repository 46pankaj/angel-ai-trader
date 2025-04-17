from cryptography.fernet import Fernet
import os

class Config:
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")  # From env vars
    DATA_DIR = "/var/data/trading"
    MAX_DAILY_LOSS = -500  # ₹5,00 daily loss limit
