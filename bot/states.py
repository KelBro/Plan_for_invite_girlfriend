from aiogram.fsm.state import State, StatesGroup


class CodeStates(StatesGroup):
    waiting_for_code = State()
