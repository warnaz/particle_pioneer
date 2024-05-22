import random
import ssl
import asyncio
import aiohttp
from loguru import logger
from aiohttp import ClientSession
from aiohttp_socks import ProxyConnector
from web3 import Web3
from config import sepolia_optimism_rpc 


class Client:
    def __init__(self, proxy: str, private_key: str, address: str) -> None:
        self.private_key = private_key
        self.account_address = address
        self.proxy_init = proxy
        self.w3 = Web3(Web3.HTTPProvider(sepolia_optimism_rpc))

        self.session = ClientSession(connector=ProxyConnector.from_url(f'http://{proxy}', ssl=ssl.create_default_context(), verify_ssl=True))
        self.session.headers.update({
            'User-Agent': self.get_user_agent()
        })

    @staticmethod
    def get_user_agent():
        random_version = f"{random.uniform(520, 540):.2f}"
        return (f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/{random_version}'
                f' (KHTML, like Gecko) Chrome/121.0.0.0 Safari/{random_version} Edg/121.0.0.0')

    async def make_request(self, method:str = 'GET', url:str = None, headers:dict = None, params: dict = None,
                           data:str = None, json:dict = None, module_name:str = 'Request'):

        errors = None

        total_time = 0
        timeout = 360
        while True:
            try:
                async with self.session.request(
                        method=method, url=url, headers=headers, data=data, params=params, json=json
                ) as response:
                    if response.status in [200, 201]:
                        data = await response.json()
                        if isinstance(data, dict):
                            errors = data.get('errors')
                        elif isinstance(data, list) and isinstance(data[0], dict):
                            errors = data[0].get('errors')

                        if not errors:
                            return data
                        elif 'have been marked as inactive' in f"{errors}":
                            raise Exception(
                                f"Bad request to {self.__class__.__name__}({module_name}) API: {errors[0]['message']}")
                        else:
                            raise Exception(
                                f"Bad request to {self.__class__.__name__}({module_name}) API: {errors[0]['message']}")

                    raise Exception(
                        f"Bad request to {self.__class__.__name__}({module_name}) API: {await response.text()}")
            except aiohttp.client_exceptions.ServerDisconnectedError as error:
                total_time += 15
                await asyncio.sleep(15)
                if total_time > timeout:
                    raise Exception(error)
                continue
            except Exception as error:
                raise Exception(error)
