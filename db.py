import aiosqlite
import asyncio
from peewee import *


sqlite_db = SqliteDatabase('menyala_bot.db')

class Order(Model):
    id


class DBClient:
    @staticmethod
    async def create_order():
        db = await aiosqlite.connect(database='menyala_bot.db')

        await db.execute("INSERT INTO some_table ...")
        await db.commit()

        await db.close()

    @staticmethod
    async def get_orders():
        db = await aiosqlite.connect('menyala_bot.db')
        cursor = await db.execute('SELECT * FROM order')
        row = await cursor.fetchone()
        rows = await cursor.fetchall()
        await cursor.close()
        await db.close()


if __name__ == '__main__':
    db_client = DBClient()
    asyncio.run(db_client.get_orders())
