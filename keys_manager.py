from datetime import date
from dateutil.relativedelta import relativedelta
import os
from dotenv import dotenv_values


config = {
    **dotenv_values(".env"),
    **os.environ,
}
API_KEYS = config.get('API_KEYS').split(',')


async def get_current_key():
    async with open('current_key.txt', 'rw+') as f:
        key = f.readline()
        print(f'key = {key}')


async def is_period_passed():
    async with open('last_update_date.txt', 'rw+') as f:
        last_date = f.readline()
        if not last_date:
            last_date = date.today()
            f.write(last_date)

    return date.today() > last_date + relativedelta(months=1)


async def update_current_key():
    pass


if __name__ == '__main__':
    print(API_KEYS[0])
