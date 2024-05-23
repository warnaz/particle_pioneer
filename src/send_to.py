import random
import time
import uuid

from loguru import logger
from client import Client
from utils.decorators import helper
from utils.services import get_captcha_key
from utils.helpers import get_headers, get_send_operation_json, get_signature
from utils.format_number import random_value
from config import project_uuid_for_send, project_key_for_send
from eth_account.messages import encode_defunct


class UniversalAccount:
    def __init__(self, client: Client) -> None:
        self.client = client

    @helper
    async def send_from_universal_acccount(self):
        logger.info(f"Start to send from universal account for : {self.client.account_address} - {self.client.aaAddress}")

        create_cross_chain_url = 'https://universal-api.particle.network/'
        url = 'https://rpc.particle.network/evm-chain?chainId=11155420&projectUuid=91bf10e7-5806-460d-95af-bef2a3122e12&projectKey=cOqbmrQ1YfOuBMo0KKDtd15bG1ENRoxuUa7nNO76&method=particle_suggestedGasFee'

        json_data = {
            "id": str(uuid.uuid4()),
            "jsonrpc": "2.0", 
            "method": "particle_suggestedGasFees",
            "params": []
        }

        headers = get_headers()
        headers['auth_type'] = 'Basic'
        headers['authorization'] = "Basic OTFiZjEwZTctNTgwNi00NjBkLTk1YWYtYmVmMmEzMTIyZTEyOmNPcWJtclExWWZPdUJNbzBLS0R0ZDE1YkcxRU5Sb3h1VWE3bk5PNzY="
        headers["origin"] = 'https://wallet.particle.network'
        headers['accept'] = 'application/json'

        headers.pop('referer', None)

        result = await self.client.make_request(
            method='POST',
            url=url, 
            headers=headers, 
            json=json_data
        )

        logger.info(f"Get gas fee: {result['result']['high']['maxPriorityFeePerGas']}")

        value = random_value()

        json_data = {"jsonrpc": "2.0","chainId": 11155420,"method": "universal_createCrossChainUserOperation","params": [
        { "name": "UNIVERSAL", "version": "1.0.0", "ownerAddress": self.client.account_address},
        [
            {
                "from": self.client.aaAddress,
                "to": self.client.account_address,
                "value": value,
                "type": "0x2",
                "gasLimit": "0x5208",
                "action": "normal",
                "data": "0x",
                "gasLevel": "high",
                "maxFeePerGas": result['result']['high']['maxFeePerGas'],
                "maxPriorityFeePerGas": result['result']['high']['maxPriorityFeePerGas']}]]
            }
        headers = get_headers()

        response = await self.client.make_request(
            method='POST', url=create_cross_chain_url, headers=headers, json=json_data)

        logger.debug(response)
        logger.info("Get user op hash: " + response['result']['userOps'][0]['userOpHash'])

        user_ops = response['result']['userOps']
        timestamp = int(time.time())
        
        params = {'chainId': '11155420', 'projectUuid': project_uuid_for_send, 'projectKey': project_key_for_send}
        json_data = {'jsonrpc': '2.0', 'id': 0, 'method': 'particle_aa_createMultiChainUnsignedData',
                    'params': [{'name': 'UNIVERSAL', 'version': '1.0.0', 'ownerAddress': self.client.account_address }, {
                        'multiChainConfigs': [{'chainId': user_ops[0]['chainId'], 'userOpHash': user_ops[0]['userOpHash'],
                                                'validUntil': timestamp + 600, 'validAfter': timestamp - 600, },
                                            {'chainId': user_ops[1]['chainId'], 'userOpHash': user_ops[1]['userOpHash'],
                                                'validUntil': timestamp + 600, 'validAfter': timestamp - 600}]}]}

        time.sleep(3)
        response = await self.client.make_request(
            method='POST', url='https://rpc.particle.network/evm-chain', params=params, headers=headers,
                                json=json_data)
        
        logger.info("Get merkle root: " + response['result']['merkleRoot'])

        merkle_root = response['result']['merkleRoot']
        merkle = encode_defunct(hexstr=merkle_root)
        evm_signature_hex = self.client.w3.eth.account.sign_message(merkle, self.client.private_key)
        _evm_signature = evm_signature_hex.signature
        evm_signature = _evm_signature.hex()

        signature1, signature2 = get_signature(response['result'], user_ops[0]['userOp']['signature'], evm_signature)
        
        capcha_key = await get_captcha_key(client=self.client)

        logger.info("Get captcha key")

        headers = get_headers()

        json_data = get_send_operation_json(capcha_key=capcha_key, user_ops=user_ops, signature1=signature1, signature2=signature2)

        response = await self.client.make_request(
            method='POST', url='https://universal-api.particle.network/', headers=headers, json=json_data)
        
        if response.get('error', None):
            message = response['error']['message'] + response['error']['extraData']
            logger.error(f"Error: {message}")
        else:
            logger.success(f"Success: {response}")
