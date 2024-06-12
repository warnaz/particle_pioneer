import os
import random
import asyncio
import sys
from loguru import logger
from functions import send_to, check_in
from client import Client
from utils.helpers import get_address_by_key, get_data_for_module
from utils.get_bearer_token import BearerToken
from config import DELAY_BETWEEN_ACCOUNTS, DELAY_BETWEEN_SEND_TRANSACTION, TWO_CAPTCHA_API_KEY
from questionary import Choice, select
from termcolor import cprint


logger.add("data/logs/logging.log", rotation="500 MB")  


async def run(module, proxy, key, address, client: Client = None):
    logger.info("RUN")
    await module(proxy, key, address)


async def run_module_multiple_times(module, proxy, key, address):
    delay = random.randint(*DELAY_BETWEEN_ACCOUNTS)
    logger.info(f"Delay between accounts: {delay} seconds")
    await asyncio.sleep(delay)

    # client = Client(proxy=proxy, private_key=key, address=address)

    if module == send_to:
        count_loop = 100
        # _, aaAddress = await BearerToken(client).get_bearer_token()
        # client.aaAddress = aaAddress
    else:
        count_loop = 1

    for _ in range(count_loop):  
        # await run(module, client)
        await run(module, proxy, key, address)

        delay = random.randint(*DELAY_BETWEEN_SEND_TRANSACTION)
        logger.info(f"Delay between transactions: {delay} seconds")
        await asyncio.sleep(delay)


async def run_modules(module):
    tasks = []
    keys, proxies, device_ids, mac_keys = get_data_for_module()

    if len(keys) != len(proxies):
        logger.error("Количество ключей и проксей должно быть одинаковое!")
        return
    elif len(keys) == 0:
        logger.error("Количество ключей и проксей должно быть больше нуля!")
        return

    for key, proxy in zip(keys, proxies):
        logger.info(key)
        address = get_address_by_key(key)
        task = asyncio.create_task(run_module_multiple_times(module=module, proxy=proxy, key=key, address=address))
        tasks.append(task)
    await asyncio.gather(*tasks)


# @logger.catch
def main():
    try:
        while True:
            answer = select(
                'Выберите действие',
                choices=[
                    Choice("✅ DAILY CHECK-IN", 'check_in'),
                    Choice("🚀 ВЫПОЛНИТЬ 100 ТРАНЗАКЦИЙ", 'send_to'),
                    Choice('❌ Exit', "exit")

                ]
            ).ask()

            if answer == 'check_in':
                asyncio.run(run_modules(module=check_in))
            elif answer == 'send_to':
                asyncio.run(run_modules(module=send_to))
            elif answer == 'exit':
                sys.exit()

    except KeyboardInterrupt:
        cprint(f'\nЧтобы выйти нажмите <ctrl + C>', color='light_yellow')
        sys.exit()


if __name__ == '__main__':
    main()
    logger.info("All wallets completed their tasks!")
