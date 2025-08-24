import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_NAME = "QualityControl test"
    DB_NAME = "control.db"
    PROJECT_DESCRIPTION = "Quality control of food and drinks"

    BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
    EMAIL_CONTROLLER = str(os.getenv("EMAIL_CONTROLLER"))
    SHEET_ID = str(os.getenv("SHEET_ID"))

    admins = [
        os.getenv("ADMIN_ID"),
    ]

    worksheet_ids = {
        "Joli": "0",
        "Juan": "1148098353",
        "Bist": "1554182714",
        "Hitch": "700143884",
        "Italiani Сити Молл": "1125789583",
        "Italiani Невский": "820734054",
        "Театр": "1262577310",
        "Italy Большой": "98944021",
        "Italy Вилен": "226068587",
        "Italy Моск": "1997943886",
        "Italy Морская": "1996220372",
        "Goose Goose": "2095471730",
        "Salone Спб": "141746961",
        "Oasis": "2127537775",
        "Atelier": "135383404",
        "Salone Мск": "1536820575",
    }

    roles = {
        "gen_manager": "Управляющий",
        "manager": "Менеджер",
        "chef": "Шеф-повар",
        "su_chef": "Су-шеф",
    }

    # PROJECT_PATH = "/Users/mac/Desktop/my_projects/quality_control/controlBot/"
    PROJECT_PATH = "/home/controlBot/"
    DB_PATH = PROJECT_PATH + DB_NAME
    PHOTO_DIR = "data/photo"
    SERVER_IP = "localhost"
    SERVER_PORT = 8000
    SERVER_LINK = f"http://{SERVER_IP}:{SERVER_PORT}"
    PHOTO_PATH = PROJECT_PATH + "/" + PHOTO_DIR + "/"
    GOOGLE_DRIVE_FOLDER_ID = "1v7he5jjYeT-sXtbySeMvLA2R_ls-wRzW"
    DROPBOX_TOKEN = os.getenv("DROPBOX_TOKEN")
    DB_KEY = os.getenv("DB_KEY")
    DB_SECRET = os.getenv("DB_SECRET")

settings = Settings()
