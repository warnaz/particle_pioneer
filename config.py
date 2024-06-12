import os
from dotenv import load_dotenv


load_dotenv()

project_uuid = '91bf10e7-5806-460d-95af-bef2a3122e12'
project_client_key = 'cOqbmrQ1YfOuBMo0KKDtd15bG1ENRoxuUa7nNO76'
project_app_uuid = '79df412e-7e9d-4a19-8484-a2c8f3d65a2e'

project_uuid_for_send = '772f7499-1d2e-40f4-8e2c-7b6dd47db9de'
project_key_for_send = 'ctWeIc2UBA6sYTKJknT9cu9LBikF00fbk1vmQjsV'

MAC_KEY = 'iEQmWtT1wQBXTdgaP5XyQRqijyP2CfYdzWy6x2bY'
DEVICE_ID = '5ee1686a-697f-4cde-a816-8937fb5ebbc7'


DELAY_BETWEEN_ACCOUNTS = (10, 50)
DELAY_BETWEEN_SEND_TRANSACTION = (10, 50)

TWO_CAPTCHA_API_KEY = os.getenv("TWO_API")

sepolia_optimism_rpc = 'https://optimism-sepolia.blockpi.network/v1/rpc/public'
