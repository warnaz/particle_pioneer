from client import Client
from utils.get_capcha_key import TwoCaptcha
from utils.get_bearer_token import BearerToken


async def get_bearer_token(client: Client):
    bearer_token = BearerToken(client)
    return await bearer_token.get_bearer_token()


async def get_captcha_key(client: Client):
    two_captcha = TwoCaptcha(client)
    task_id = await two_captcha.create_task_for_captcha()
    return await two_captcha.get_captcha_key(task_id=task_id)
