from client import Client
from src.send_to import UniversalAccount
from src.daily_task import DailyTask


async def send_to(client: Client):
    universal_account = UniversalAccount(client)
    await universal_account.send_from_universal_acccount()


async def check_in(client: Client):
    daily_task = DailyTask(client)
    await daily_task.daily_check_in()
