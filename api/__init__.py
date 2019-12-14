from fastapi import FastAPI

from api.utils import cost_calculation_py as python_calculation_utils
from api.utils import setup_funcs
from api.utils.setup_funcs import setup_postgres, setup_data_frame

app = FastAPI()


@app.on_event('startup')
async def startup():
    await setup_postgres(app)
    setup_data_frame(app)


@app.on_event('shutdown')
async def down():
    await app.postgres.close()

from .views import *
