import os
from dotenv import load_dotenv


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(BASE_DIR, ".env")

load_dotenv(dotenv_path)

FUTUUR_PUBLIC_KEY = os.environ.get("FUTUUR_PUBLIC_KEY")
FUTUUR_PRIVATE_KEY = os.environ.get("FUTUUR_PRIVATE_KEY")
