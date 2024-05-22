from client import Client
import time
import uuid

from eth_account.messages import encode_defunct
from faker import Faker
from loguru import logger
from web3 import Web3
from utils.helpers import sha256, get_headers
from config import (
    project_uuid, 
    project_client_key, 
    project_app_uuid, 
)


class BearerToken:
    def __init__(self, client: Client) -> None:
        self.client = client

    async def get_bearer_token(self):
        logger.info("Get bearer token")

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Auth-Type': 'Basic',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'https://pioneer.particle.network',
            'Referer': 'https://pioneer.particle.network/',
            'authorization': 'Basic OUMzUnRxQmNCcUJuQk5vYjo3RGJubng3QlBxOENBOFBI',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        }
        random_str, timestamp, device_id = str(uuid.uuid4()), int(time.time()), str(uuid.uuid4())
        params = {'timestamp': timestamp, 'random_str': random_str, 'device_id': device_id, 'sdk_version': 'web_1.0.0',
                'project_uuid': project_uuid, 'project_client_key': project_client_key,
                'project_app_uuid': project_app_uuid}
        
        sign_str = f"""Welcome to Particle Pioneer!\n\nWallet address:\n{self.client.account_address}\n\nNonce:\n{device_id}"""

        signature = self.client.w3.eth.account.sign_message(encode_defunct(text=sign_str), self.client.private_key).signature.hex()
        mac_info = {"timestamp": timestamp, "random_str": random_str, "device_id": device_id,
                    "sdk_version": "web_1.0.0",
                    "project_uuid": project_uuid, "project_client_key": project_client_key,
                    "mac_key": "5706dd1db5aabc45c649ecc01fdac97100de8e8655715d810d0fb2080e6cea24",
                    "project_app_uuid": project_app_uuid, "loginMethod": "evm_wallet", "loginSource": "metamask",
                    "loginInfo": {"address": self.client.account_address.lower(), "signature": signature}}

        mac = sha256(dict(sorted(mac_info.items())))
        params.update({'mac': mac})
        json_data = {'loginMethod': 'evm_wallet', 'loginSource': 'metamask',
                    'loginInfo': {'address': self.client.account_address.lower(), 'signature': signature}}

        response = await self.client.make_request(
            method = 'POST', 
            url='https://pioneer-api.particle.network/users',
            params=params, 
            headers=headers,
            json=json_data
        )
    
        token = response['token']
        aaAddress = response['aaAddress']
        logger.success(f"Bearer Token: {token}")

        return token, aaAddress
 