from aiogram import types, Router
from aiogram.filters import Command
from data.lexicon import lexicon

router = Router()


@router.message(Command("help"), flags={"chat_action": "typing"})
async def bot_help(message: types.Message):
    await message.answer(lexicon["/help"])
