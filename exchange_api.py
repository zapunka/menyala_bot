import aiohttp
import os
from dotenv import dotenv_values

from models import ExchangeResponse
import keys_manager


config = {
    **dotenv_values(".env"),
    **os.environ,
}
MAX_TRIES_COUNT = 3
MAIN_CURRENCY = "THB"
EXCHANGE_CURRENCY = "USD"


async def send_request(api_key, curr_from, curr_to) -> ExchangeResponse:
    # url = f"https://api.apilayer.com/currency_data/convert?to={curr_to}&from={curr_from}&amount=1"
    url = f'{config.get("API_URL")}?to={curr_to}&from={curr_from}&amount=1'
    headers = {
        "apikey": api_key,
        "Content-Type": "application/json",
    }

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        async with session.get(url, headers=headers) as resp:
            body = await resp.json()

            return ExchangeResponse(
                body.get('error'),
                body.get('result'),
                resp.status,
                resp.headers
            )


async def exchange(curr_from, curr_to, tries_count=0) -> ExchangeResponse:
    # check if months is passed - update the file and set the first key as current
    await keys_manager.update_current_key()
    # get current key
    key = await keys_manager.get_current_key()

    # sending a request to API
    resp: ExchangeResponse = await send_request(key, curr_from, curr_to)

    if resp.status == 200 or resp.status >= 500:
        return resp

    else:
        while tries_count < MAX_TRIES_COUNT:
            print(f"Can't get response, status = {resp.status}, error = {resp.error}")
            tries_count += 1
            if resp.status == 429:
                await keys_manager.set_current_key(tries_count)
                await exchange(curr_from, curr_to, tries_count)

        return resp


async def convert_to_main_curr(currency: str, exchange_currency=EXCHANGE_CURRENCY, main_currency=MAIN_CURRENCY):
    curr_to_exchange_resp = await exchange(exchange_currency, currency)

    if curr_to_exchange_resp.status == 200:
        curr_to_exchange = float(curr_to_exchange_resp.result)
        curr_to_main_resp = await exchange(exchange_currency, main_currency)

        if curr_to_main_resp.status == 200:
            curr_to_main = float(curr_to_main_resp.result)

            curr_to_main_resp.result = round(curr_to_exchange / curr_to_main, 2)
            return curr_to_main_resp
        else:
            return curr_to_main_resp

    else:
        return curr_to_exchange_resp


# if __name__ == '__main__':
#     import asyncio
#     asyncio.run(exchange("THB", "RUB"))
