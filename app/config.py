import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

WEBSHARE_USERNAME = os.getenv("WEBSHARE_USERNAME")
WEBSHARE_PASSWORD = os.getenv("WEBSHARE_PASSWORD")
