import asyncio
from client import Client
from config import TWO_CAPTCHA_API_KEY 
from loguru import logger


class TwoCaptcha:
    def __init__(self, client: Client) -> None:
        self.client = client

    async def create_task_for_captcha(self):
        url = 'https://api.2captcha.com/createTask'

        proxy_tuple = self.client.proxy_init.split('@')

        proxy_login, proxy_password = proxy_tuple[0].split(':')
        proxy_address, proxy_port = proxy_tuple[1].split(':')

        logger.info(f'Getting captcha key from 2Captcha')
                
        cloudflare_url = 'https://pioneer.particle.network/en/point' 
        cloudflare_sitekey = '0x4AAAAAAAaHm6FnzyhhmePw'

        payload = {
            "clientKey": TWO_CAPTCHA_API_KEY,
            "task": {
                "type": "TurnstileTask",
                "websiteURL": cloudflare_url,
                "websiteKey": cloudflare_sitekey,
                "userAgent": self.client.session.headers['User-Agent'],
                "proxyType": "http",
                "proxyAddress": proxy_address,
                "proxyPort": proxy_port,
                "proxyLogin": proxy_login,
                "proxyPassword": proxy_password
            }
        }

        response = await self.client.make_request(method="POST", url=url, json=payload)
        logger.info(response )

        if response.get('errorId', None):
            raise Exception('Bad request to 2Captcha(Create Task)')
        return response.get('taskId', None)

    async def get_captcha_key(self, task_id):
        url = 'https://api.2captcha.com/getTaskResult'

        payload = {
            "clientKey": TWO_CAPTCHA_API_KEY,
            "taskId": task_id
        }

        total_time = 0
        timeout = 360
        while True:
            response = await self.client.make_request(method="POST", url=url, json=payload)

            if response.get('status', None) == 'ready':
                return response['solution']['token']

            total_time += 5
            await asyncio.sleep(5)

            if total_time > timeout:
                raise Exception('Can`t get captcha solve in 360 second')
