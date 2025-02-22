import os
from dotenv import load_dotenv

def setings_env():
    env_path = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
    load_dotenv(f"{env_path}/.env")
    print(env_path)