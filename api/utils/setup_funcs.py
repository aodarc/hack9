import asyncpg
import pandas as pd
import os
from fastapi import FastAPI

from api.queries import CREATE_CALLS_TABLE, CREATE_INVOICE_TABLE
from api.settings import POSTGRES_URL


def setup_data_frame(app: FastAPI) -> None:
    app.df = pd.read_csv(os.path.join(os.getcwd(), "api/utils/callingCodes.csv")).sort_values('prefix')


async def setup_postgres(app: FastAPI) -> None:
    app.postgres = await asyncpg.create_pool(dsn=POSTGRES_URL)

    # pre-init db scripts
    async with app.postgres.acquire() as con:
        await con.execute(CREATE_CALLS_TABLE)
        await con.execute(CREATE_INVOICE_TABLE)
