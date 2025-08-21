import asyncio

import gspread_asyncio
from google.oauth2.service_account import Credentials
from data.config import settings


def get_creds():
    creds = Credentials.from_service_account_file("../quality-control-469712-5f601fa34788.json")
    scoped = creds.with_scopes([
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ])
    return scoped


async def example(agcm):
    agc = await agcm.authorize()
    ss = await agc.open_by_key(settings.SHEET_ID)
    print("All done!")
    result = await ss.worksheets()
    return result


async def main():
    agcm = gspread_asyncio.AsyncioGspreadClientManager(get_creds)
    result = await example(agcm)
    for sheet in result:
        print(f'"{sheet.title}": {sheet.id},')

if __name__ == "__main__":
    asyncio.run(main())
