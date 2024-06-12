from client import Client
from src.send_to import UniversalAccount
from src.daily_task import DailyTask
from utils.get_bearer_token import BearerToken


async def get_client(proxy, private_key, address):
    return Client(proxy, private_key, address)


async def send_to(proxy, private_key, address):
    universal_account = UniversalAccount(Client(proxy=proxy, private_key=private_key, address=address))
    
    _, aaAddress = await BearerToken(universal_account.client).get_bearer_token()
    universal_account.client.aaAddress = aaAddress

    await universal_account.send_from_universal_acccount()

# async def send_to(client: Client):
#     universal_account = UniversalAccount(client)
#     await universal_account.send_from_universal_acccount()


async def check_in(proxy, private_key, address):
    daily_task = DailyTask(Client(proxy=proxy, private_key=private_key, address=address))
    await daily_task.daily_check_in()
