from dotenv import load_dotenv # type: ignore
import os

load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DB_ID= os.getenv("NOTION_DATABASE_ID")

