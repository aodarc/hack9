import math

import asyncpg
from fastapi import FastAPI

from api import settings
from api.queries import CREATE_CALLS_TABLE, CREATE_INVOICE_TABLE
from api.settings import POSTGRES_URL


def calculate_cost(initial: int, duration: int, increment: int, rate: float) -> float:
    """Calculate call price
    :param initial: initial for prefix
    :param duration: call duration
    :param increment: increment value for prefix
    :param rate: calling rate for prefix !! per minute
    :return: price
    """
    # The cost of the call is calculated as the price per minute divided by 60 and effective seconds.
    # Effective number of seconds is calculated as:
    #   initial seconds plus actual seconds, rounded to the upper bound of increment.

    # If we had a call that lasted 53s and the price entry applicable has initial=20s and increment=10s,
    # the effective duration of the call would be: 20s + 53s = 73s,
    # which will be rounded up to 80s (the first number greater or equal to 73, divisible by 10).

    # All financial numerical values are rounded to 2 fractional digits.
    return round((math.ceil((initial + duration) / increment) * increment) * (rate / 60.), 2)


async def setup_postgres(app: FastAPI) -> None:
    app.postgres = await asyncpg.create_pool(dsn=POSTGRES_URL)

    # pre-init db scripts
    async with app.postgres.acquire() as con:
        await con.execute(CREATE_CALLS_TABLE)
        await con.execute(CREATE_INVOICE_TABLE)
