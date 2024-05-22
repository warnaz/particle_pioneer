import hashlib
import json
from eth_abi import encode
from eth_account import Account


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
