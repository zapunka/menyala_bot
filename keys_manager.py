import aiofiles
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import os
from dotenv import dotenv_values


config = {
    **dotenv_values(".env"),
    **os.environ,
}
API_KEYS = config.get('API_KEYS').split(',')


async def get_current_key():
    async with aiofiles.open('current_key.txt', 'w+') as f:
        key = await f.readline()

    if not key:
        key = API_KEYS[0]
        await set_current_key(0)

    return key


async def is_period_passed():
    async with aiofiles.open('last_update_date.txt', 'w+') as f:
        last_date = await f.readline()
        if last_date:
            last_date = datetime.strptime(last_date, '%Y-%m-%d')
        else:
            last_date = date.today()
            await f.write(last_date.strftime('%Y-%m-%d'))

    return date.today() > last_date + relativedelta(months=1)


async def update_current_key():
    is_passed = await is_period_passed()

    if is_passed:
        async with aiofiles.open('current_key.txt', 'w+') as f:
            await f.write(API_KEYS[0])

        async with aiofiles.open('last_update_date.txt', 'w+') as f:
            await f.write(date.today().strftime('%Y-%m-%d'))


async def set_current_key(key_number):
    async with aiofiles.open('current_key.txt', 'w+') as f:
        await f.write(API_KEYS[key_number])


if __name__ == '__main__':
    import asyncio
    asyncio.run(is_period_passed())
