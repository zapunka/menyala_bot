import aiohttp
import os
from dotenv import dotenv_values

from models import ExchangeResponse


config = {
    **dotenv_values(".env"),
    **os.environ,
}
MAX_TRIES_COUNT = 3


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
            print(body)
            return ExchangeResponse(
                body.get('error'),
                body.get('result'),
                resp.status,
                resp.headers
            )


async def exchange(curr_from, curr_to, tries_count=0) -> ExchangeResponse:
    key =

    if not key:
        key = API_KEYS[0]
        async with open('current_key.txt', 'w') as f:
            f.write(key)

    resp: ExchangeResponse = await send_request(key, curr_from, curr_to)

    if resp.status == 200 or resp.status >= 500:
        return resp

    else:
        while tries_count < MAX_TRIES_COUNT:
            print(f"Can't get response, status = {resp.status}, error = {resp.error}")
            tries_count += 1
            if resp.status == 429:
                key = API_KEYS[tries_count]
                async with open('current_key.txt', 'w') as f:
                    f.write(key)
                    await exchange(curr_from, curr_to, tries_count)

        return resp


# if __name__ == '__main__':
#     import asyncio
#     asyncio.run(exchange())
