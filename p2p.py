import requests


def get_p2p_rate():
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Length": "123",
        "content-type": "application/json",
        "Host": "p2p.binance.com",
        "Origin": "https://p2p.binance.com",
        "Pragma": "no-cache",
        "TE": "Trailers",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"
    }

    data = {
        "asset": "USDT",
        "countries": [],
        "fiat": "THB",
        "page": 1,
        "payTypes": ["TinkoffNew"],
        "proMerchantAds": False,
        "publisherType": None,
        "rows": 10,
        "tradeType": "SELL"
    }

    url = 'https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search'
    # r = requests.post('https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search', headers=headers, json=data)
    # print(r.text)
    r = requests.post(url, headers=headers, json=data)
    print(r.text)

    # async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
    #     async with session.post(url, headers=headers, data=data) as resp:
    #         body = await resp.json()
    #         print(f'body = {body}')


if __name__ == '__main__':
    get_p2p_rate()
