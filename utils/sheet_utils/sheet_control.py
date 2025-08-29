import asyncio
import os

import gspread_asyncio
from google.oauth2.service_account import Credentials
from data.config import settings
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload



class GoogleSheetsClient:
    def __init__(self, creds_path: str, sheet_id: str):
        self.creds_path = creds_path
        self.sheet_id = sheet_id
        self.agcm = gspread_asyncio.AsyncioGspreadClientManager(self._get_creds)
        creds = self._get_creds()
        self.drive_service = build('drive', 'v3', credentials=creds)

    def _get_creds(self):
        """Загрузка и настройка credentials"""
        creds = Credentials.from_service_account_file(self.creds_path)
        scoped = creds.with_scopes([
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ])
        return scoped

    async def authorize(self):
        """Авторизация и получение клиента"""
        return await self.agcm.authorize()

    async def get_spreadsheet(self):
        """Получение таблицы по sheet_id"""
        agc = await self.authorize()
        return await agc.open_by_key(self.sheet_id)

    async def get_worksheets(self):
        """Получение всех листов таблицы"""
        ss = await self.get_spreadsheet()
        return await ss.worksheets()

    async def get_worksheet_values_by_id(self, worksheet_id: int):
        """Получение листа по его ID"""
        ss = await self.get_spreadsheet()
        ws = await ss.get_worksheet_by_id(worksheet_id)
        return await ws.get_all_values()

    async def get_worksheet_by_id(self, worksheet_id: int):
        """Получение листа по его ID"""
        ss = await self.get_spreadsheet()
        return await ss.get_worksheet_by_id(worksheet_id)

    async def insert_review_row(
        self,
        worksheet_id: int,
        date: str,
        status: str,
        dish_name: str,
        photo_path: str,
        description: str,
        price: str,
        surname_reviewer: str,
        surname_chef: str,
        final_status: str,
        link_photo: str,
        ref_id: int
    ):
        """
        Вставка строки отзыва в таблицу Google Sheets.
        Порядок колонок:
        date | status | dish_name | photo_path | description |
        surname_reviewer | surname_chef | final_status | ref_id
        """
        ws = await self.get_worksheet_by_id(worksheet_id)
        row_data = [
            date,
            status,
            dish_name,
            photo_path,
            description,
            price,
            surname_reviewer,
            surname_chef,
            final_status,
            link_photo,
            ref_id
        ]
        await ws.append_row(row_data, value_input_option='USER_ENTERED')
