import time
import uuid
import requests
from eth_account import Account
from loguru import logger
from client import Client
from utils.services import get_bearer_token, get_captcha_key
from config import project_uuid, project_client_key, project_app_uuid
from utils.helpers import get_signature, sha256
from eth_account.messages import encode_defunct


class DailyTask:
    def __init__(self, client: Client) -> None:
        self.client = client

    async def daily_check_in(self, mac_key = "iEQmWtT1wQBXTdgaP5XyQRqijyP2CfYdzWy6x2bY", device_id = '65b4e14d-7150-441b-8ff3-f83d630e7287'):
        logger.info("Start to check in")

        account = Account.from_key(self.client.private_key)
        token = await get_bearer_token(self.client)

        random_str, timestamp = str(uuid.uuid4()), int(time.time())
        
        mac_info = {"timestamp": timestamp, "random_str": random_str,
                    "device_id": device_id, "sdk_version": "web_1.0.0",
                    "project_uuid": project_uuid,
                    "project_client_key": project_client_key,
                    "project_app_uuid": project_app_uuid,
                    "mac_key": mac_key}

        params = {
            'timestamp': timestamp,
            'random_str': random_str,
            'device_id': device_id,
            'sdk_version': 'web_1.0.0',
            'project_uuid': project_uuid,
            'project_client_key': project_client_key,
            'project_app_uuid': project_app_uuid,
            'mac': sha256(dict(sorted(mac_info.items())))
        }

        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'authorization': f'Bearer {token}',
            'cache-control': 'no-cache',
            # 'content-type': 'application/json',
            # 'content-length': '0',
            'origin': 'https://pioneer.particle.network',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://pioneer.particle.network/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        }

        # TODO разобраться, почему не работает асинхронный вариант
        # response = await self.client.make_request(
        #     method="POST",
        #     url='https://pioneer-api.particle.network/streaks/streak_tx', 
        #     params=params,
        #     headers=headers
        # )

        session = requests.session()
        response = session.post('https://pioneer-api.particle.network/streaks/streak_tx', params=params,
                        headers=headers).json()            

        if response["message"] == "Already checked-in":
            logger.info(f"Already checked-in for {self.client.account_address}")
            return 

        logger.info(response)

        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'auth-type': 'None',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'origin': 'https://pioneer.particle.network',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://pioneer.particle.network/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        }

        json_data = {'jsonrpc': '2.0', 'chainId': 11155420, 'method': 'universal_createCrossChainUserOperation', 'params': [
            {'name': 'UNIVERSAL', 'version': '1.0.0', 'ownerAddress': response['smartAccount']['ownerAddress']},
            [{'to': response['tx']['to'], 'data': response['tx']['data'], 'chainId': response['tx']['chainId']}]]}

        response = await self.client.make_request(
            method='POST', 
            url='https://universal-api.particle.network/', 
            headers=headers,
            json=json_data
        )

        logger.info(f"Get universal_createCrossChainUserOperation: {response}")

        user_ops = response['result']['userOps']
        headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'origin': 'https://pioneer.particle.network',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://pioneer.particle.network/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        }

        params = {'chainId': '11155420', 'projectUuid': project_uuid, 'projectKey': project_client_key}
        timestamp = int(time.time())
        json_data = {'jsonrpc': '2.0', 'id': 0, 'method': 'particle_aa_createMultiChainUnsignedData',
                    'params': [{'name': 'UNIVERSAL', 'version': '1.0.0', 'ownerAddress': self.client.account_address, }, {
                        'multiChainConfigs': [{'chainId': user_ops[0]['chainId'], 'userOpHash': user_ops[0]['userOpHash'],
                                                'validUntil': timestamp + 600, 'validAfter': timestamp - 600, },
                                            {'chainId': user_ops[1]['chainId'], 'userOpHash': user_ops[1]['userOpHash'],
                                                'validUntil': timestamp + 600, 'validAfter': timestamp - 600}]}]}
        
        time.sleep(3)
        response = await self.client.make_request(
            method="POST", 
            url='https://rpc.particle.network/evm-chain', 
            params=params, 
            headers=headers,
            json=json_data
        )

        logger.info(f"Get merkleRoot: {response['result']['merkleRoot']}")

        merkle_root = response['result']['merkleRoot']
        evm_signature = account.sign_message(encode_defunct(hexstr=merkle_root)).signature.hex()
        signature1, signature2 = get_signature(response['result'], user_ops[0]['userOp']['signature'], evm_signature)
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'auth-type': 'None',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'origin': 'https://pioneer.particle.network',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://pioneer.particle.network/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        }

        captcha_key = await get_captcha_key(self.client)

        json_data = {
            'jsonrpc': '2.0', 
            'chainId': 11155420, 
            'method': 'universal_sendCrossChainUserOperation',
            'cfTurnstileResponse': captcha_key,
            'params': [[{
                'sender': user_ops[0]['userOp']['sender'], 'nonce': user_ops[0]['userOp']['nonce'],
                'initCode': user_ops[0]['userOp']['initCode'], 'callData': user_ops[0]['userOp']['callData'],
                'paymasterAndData': user_ops[0]['userOp']['paymasterAndData'], 'signature': signature1,
                'preVerificationGas': user_ops[0]['userOp']['preVerificationGas'],
                'verificationGasLimit': user_ops[0]['userOp']['verificationGasLimit'],
                'callGasLimit': user_ops[0]['userOp']['callGasLimit'],
                'maxFeePerGas': user_ops[0]['userOp']['maxFeePerGas'],
                'maxPriorityFeePerGas': user_ops[0]['userOp']['maxPriorityFeePerGas'],
                'chainId': user_ops[0]['chainId']},
                {'sender': user_ops[1]['userOp']['sender'], 'nonce': user_ops[1]['userOp']['nonce'],
                'initCode': user_ops[1]['userOp']['initCode'], 'callData': user_ops[1]['userOp']['callData'],
                'callGasLimit': user_ops[1]['userOp']['callGasLimit'],
                'verificationGasLimit': user_ops[1]['userOp']['verificationGasLimit'],
                'preVerificationGas': user_ops[1]['userOp']['preVerificationGas'],
                'maxFeePerGas': user_ops[1]['userOp']['maxFeePerGas'],
                'maxPriorityFeePerGas': user_ops[1]['userOp']['maxPriorityFeePerGas'],
                'paymasterAndData': user_ops[1]['userOp']['paymasterAndData'], 'chainId': user_ops[1]['chainId'],
                'signature': signature2}]]}

        response = await self.client.make_request(
            method="POST", 
            url='https://universal-api.particle.network/', 
            headers=headers, 
            json=json_data
        )

        logger.success(f"Successful check in: {response}")

        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'authorization': f'Bearer {token}',
            'origin': 'https://pioneer.particle.network',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://pioneer.particle.network/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        }

        random_str, timestamp = str(uuid.uuid4()), int(time.time())
        mac_info = {"timestamp": timestamp, "random_str": random_str,
                    "device_id": device_id, "sdk_version": "web_1.0.0",
                    "project_uuid": project_uuid,
                    "project_client_key": project_client_key,
                    "project_app_uuid": project_app_uuid,
                    "mac_key": mac_key
                }

        params = {
            'timestamp': timestamp,
            'random_str': random_str,
            'device_id': device_id,
            'sdk_version': 'web_1.0.0',
            'project_uuid': project_uuid,
            'project_client_key': project_client_key,
            'project_app_uuid': project_app_uuid,
            'mac': sha256(dict(sorted(mac_info.items())))
        }

        response = await self.client.make_request(
            method="POST", 
            url='https://pioneer-api.particle.network/users/check_tx_point', 
            params=params,
            headers=headers
        )

        logger.info(f"Get check point: {response}")

        random_str, timestamp = str(uuid.uuid4()), int(time.time())
        mac_info = {"timestamp": timestamp, "random_str": random_str,
                    "device_id": device_id, "sdk_version": "web_1.0.0",
                    "project_uuid": project_uuid,
                    "project_client_key": project_client_key,
                    "project_app_uuid": project_app_uuid,
                    "mac_key": mac_key}
        params = {
            'timestamp': timestamp,
            'random_str': random_str,
            'device_id': device_id,
            'sdk_version': 'web_1.0.0',
            'project_uuid': project_uuid,
            'project_client_key': project_client_key,
            'project_app_uuid': project_app_uuid,
            'mac': sha256(dict(sorted(mac_info.items())))
        }
        response = await self.client.make_request(
            method="POST", 
            url='https://pioneer-api.particle.network/streaks/check_streak', 
            params=params,
            headers=headers
        )

        logger.info(f"Get streak: {response}")

        random_str, timestamp = str(uuid.uuid4()), int(time.time())
        mac_info = {"timestamp": timestamp, "random_str": random_str,
                    "device_id": device_id, "sdk_version": "web_1.0.0",
                    "project_uuid": project_uuid,
                    "project_client_key": project_client_key,
                    "project_app_uuid": project_app_uuid,
                    "mac_key": mac_key}
        params = {
            'timestamp': timestamp,
            'random_str': random_str,
            'device_id': device_id,
            'sdk_version': 'web_1.0.0',
            'project_uuid': project_uuid,
            'project_client_key': project_client_key,
            'project_app_uuid': project_app_uuid,
            'mac': sha256(dict(sorted(mac_info.items())))
        }

        response = await self.client.make_request(
            method="GET", 
            url='https://pioneer-api.particle.network/streaks/daily_point', 
            params=params,
            headers=headers
        )

        logger.info(f"Get daily point: {response}")
