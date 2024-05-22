import hashlib
import json
from eth_abi import encode
from eth_account import Account
from config import project_uuid, project_client_key, project_app_uuid


def get_headers():
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
      
    return headers


def get_mac_info(timestamp, random_str, device_id, mac_key):
    return {"timestamp": timestamp, "random_str": random_str,
                    "device_id": device_id, "sdk_version": "web_1.0.0",
                    "project_uuid": project_uuid,
                    "project_client_key": project_client_key,
                    "project_app_uuid": project_app_uuid,
                    "mac_key": mac_key}


def get_params(timestamp, random_str, device_id, mac_key):
    return {
            'timestamp': timestamp,
            'random_str': random_str,
            'device_id': device_id,
            'sdk_version': 'web_1.0.0',
            'project_uuid': project_uuid,
            'project_client_key': project_client_key,
            'project_app_uuid': project_app_uuid,
            'mac': sha256(dict(sorted(get_mac_info(timestamp, random_str, device_id, mac_key).items())))
        }


def sha256(data):
    hash_object = hashlib.sha256()
    hash_object.update(json.dumps(data).replace(' ', '').encode())
    hex_dig = hash_object.hexdigest()
    return hex_dig


def get_signature(merkle_root_result, signature, evm_signature):
    encode_data = ''
    valid_until = merkle_root_result['data'][0]['validUntil']
    valid_after = merkle_root_result['data'][0]['validAfter']
    encode_data += signature[0:130]
    encode_data += '0000000000000000000000000000000000000000000000000000000000000160'
    encode_data += encode(('uint256',), (valid_until,)).hex()
    encode_data += encode(('uint256',), (valid_after,)).hex()
    encode_data += merkle_root_result['merkleRoot'][2:]
    encode_data += '00000000000000000000000000000000000000000000000000000000000000a0'
    encode_data += '00000000000000000000000000000000000000000000000000000000000000e0'
    encode_data += '0000000000000000000000000000000000000000000000000000000000000001'
    result_signature1 = encode_data + merkle_root_result['data'][0]['merkleProof'][0][2:]
    result_signature1 += '0000000000000000000000000000000000000000000000000000000000000041' + evm_signature[2:]
    result_signature1 += '00000000000000000000000000000000000000000000000000000000000000'
    result_signature2 = encode_data + merkle_root_result['data'][1]['merkleProof'][0][2:]
    result_signature2 += '0000000000000000000000000000000000000000000000000000000000000041' + evm_signature[2:]
    result_signature2 += '00000000000000000000000000000000000000000000000000000000000000'
    return result_signature1, result_signature2


def get_address_by_key(key):
    account = Account.from_key(key)
    return account.address


def get_keys_proxies():
    keys = []
    with open('data/keys.txt', 'r') as f:
        keys = [line.strip() for line in f.readlines()]

    proxies = []
    with open('data/proxies.txt', 'r') as f:
        proxies = [line.strip() for line in f.readlines()]
    
    return keys, proxies



def get_send_operation_json(capcha_key, user_ops, signature1, signature2):
        return {
            'jsonrpc': '2.0', 
            'chainId': 11155420, 
            'method': 'universal_sendCrossChainUserOperation',
            'cfTurnstileResponse': capcha_key,
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
