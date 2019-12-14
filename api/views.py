import json
import math
from datetime import datetime
from decimal import Decimal

import dateutil
import pandas as pd
from pydantic.error_wrappers import ValidationError as pydanticValidationError
from starlette.requests import Request
from starlette.responses import Response

from api.models import CallData, CallDataInResponse, InvoiceData
from api.queries import ADD_CALLS_RECORD, GET_INVOICE_RECORD_BY_ID, LISTING, GET_FINANCIAL_REPORTS_SUM, \
    GET_FINANCIAL_REPORTS_REMAINING
from api.utils import invoice_generation
from api.utils.cost_calculation_py import calculate_cost
from . import app

ERROR_400 = Response(content='{"message": "Incorrect input"}', status_code=400,
                     headers={"Content-type": "application/json"})
ERROR_404 = Response(content='{"message": "No in DB"}', status_code=404,
                     headers={"Content-type": "application/json"})
MAX_PREFIX_SIZE = 9


def get_call_stats_from_csv(dataframe, time, calling):
    rows = pd.DataFrame()
    calling = str(calling)
    for i in range(MAX_PREFIX_SIZE, 0, -1):
        rows = dataframe.loc[dataframe.prefix == int(calling[:i])]
        if not rows.empty:
            rows = rows.loc[(rows.startDate <= time)].sort_values('startDate').tail(1)
            break

    if rows.empty:
        return {}

    return {
        "prefix": f"{rows.prefix.values[0]}",
        "price": f"{rows.price.values[0]}",
        "from": rows.startDate.values[0],
        "initial": f"{rows.initial.values[0]}",
        "increment": f"{rows.increment.values[0]}"
    }


@app.post("/reset", status_code=201)
async def reset():
    """
    Delete all prior records of calls and invoices made and bring system to initial state.
    :return:
        - 201 Body: none.  # System state was cleared and the server is ready.
    """

    async with app.postgres.acquire() as con:
        await con.execute("DELETE FROM calls")
        await con.execute("DELETE FROM invoice")
    return {}


@app.get("/switch/price")
async def switch_price(number: str, time: str = ""):
    """
    :param number: *required. Telephone number to call, for which the call price should be returned. Example: 38121123456
    :param time: not required. Example: 2019-04-03T12:34:56.00Z
    :return:
        - 200  Price of a call, per second
            - Headers
                - Content-type: application/json
            - Body
                {
                    "prefix": "381 21",
                    "price": "1.2",
                    "from": "2019-01-01T00:00:00.00Z",
                    "initial": "10",
                    "increment": "5"
                }
        - 400  Call number is invalid format
            - Headers
                - Content-type: application/json
            - Body
                {
                    "message": "Call number is invalid format"
                }
        - 404  Price for the number cannot be calculated
            - Headers
                - Content-type: application/json
            - Body
                {
                    "message": "Price for the number cannot be calculated"
                }
    """
    if not number or not number.isdigit() or len(number) > 15:
        return ERROR_400

    time = time if time else datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-4] + 'Z'
    result = get_call_stats_from_csv(
        dataframe=app.df,
        time=time,
        calling=number
    )
    if not result:
        return ERROR_404
    return result


@app.post("/switch/call")
async def switch_call(data: dict):
    """Register details of a call that was made and calcualte the cost of the call.
        - Request data:
            {
                "calling": "381211234567",
                "called": "38164111222333",
                "start": "2019-05-23T21:03:33.30Z",
                "duration": "450"
            }

    :param data:
    :return:
        - 200  Call accepted
            - Headers
                - Content-type: application/json
            - Body
                {
                    "calling": "381211234567",
                    "called": "38164111222333",
                    "start": "2019-05-23T21:03:33.30Z",
                    "duration": "350",
                    "rounded": "355",
                    "price": "0.4",
                    "cost": "2.367"
                }
        - 400  Incorrect input
            - Headers
                - Content-type: application/json
            - Body
                {
                    "message": "Incorrect input"
                }
        - 400  Incorrect input
            - Headers
                - Content-type: application/json
            - Body
                {
                    "message": "Error occurred"
                }
    """
    try:
        call_object = CallData(**data)

        call_stats = get_call_stats_from_csv(
            calling=call_object.called,
            time=call_object.start.isoformat() + 'Z',
            dataframe=app.df
        )
        if not call_stats:
            return ERROR_400

        cost = calculate_cost(
            initial=int(call_stats["initial"]),
            duration=int(call_object.duration),
            increment=int(call_stats["increment"]),
            rate=float(call_stats["price"])
        )
        rounded = math.ceil((int(call_stats["initial"]) + int(call_object.duration)) / \
        int(call_stats["increment"])) * int(call_stats["increment"])
        call_object.price = call_stats["price"]
        call_object.cost = cost
        call_object.rounded = rounded

        async with app.postgres.acquire() as con:
            await con.execute(
                ADD_CALLS_RECORD,
                int(call_object.calling),
                int(call_object.called),
                call_object.start.replace(tzinfo=None),
                call_object.duration,
                call_object.rounded,
                float(call_object.price),
                float(call_object.cost)
            )
            # call_object.id = str(row.inserted_id)
            # response = {key: str(v) for key, v in call_object.dict().items()}
            response = CallDataInResponse(call_data=call_object.dict()).call_data
    except pydanticValidationError:
        response = Response(
            content='{"message": "Incorrect input"}',
            status_code=400,
            headers={
                "Content-type": "application/json"
            }
        )
    except Exception as e:
        raise e
        # response = Response(
        #     content='{"message": "Error occurred"}',
        #     status_code=400,
        #     headers={
        #         "Content-type": "application/json"
        #     }
        # )
    return response


@app.get("/listing/{calling}")
async def listing(calling: str, request: Request):
    """Listing of calls made by the given telephone number.
    :param calling: *required. Calling number. Example 38121123456
    :param request:
        from: *required. Start of the listing period. Example: 2019-04-03T12:34:56.00Z
        to: *required. End of the listing period. Example: 2019-04-03T12:34:56.00Z
    :return:
        - 200  Listing generated, even if empty.
            - Headers
                - Content-type: application/json
            - Body
                {
                    "calling": "381211234567",
                    "calls": [
                    {
                        "calling": "381211234567",
                        "called": "38164111222333",
                        "start": "2019-05-23T21:03:33.30Z",
                        "duration": "350",
                        "rounded": "355",
                        "price": "0.4",
                        "cost": "2.367"
                    }
                  ]
                }
    """
    from_str = request.query_params.get('from')
    to_str = request.query_params.get('to')

    response_body = {
        'calling': calling,
        'calls': []
    }
    try:
        datetime_from = dateutil.parser.parse(from_str).replace(tzinfo=None)
        datetime_to = dateutil.parser.parse(to_str).replace(tzinfo=None)

        async with app.postgres.acquire() as con:
            records = await con.fetch(
                LISTING,
                int(calling),
                datetime_from,
                datetime_to
            )

        for record in records:
            record = dict(record)
            record['start'] = record['start'].isoformat() + 'Z'
            response_body['calls'].append(record)

        json_body = json.dumps(response_body)
        response = Response(
            content=json_body,
            status_code=200,
            headers={
                "Content-type": "application/json"
            }
        )
    except Exception:
        json_body = json.dumps(response_body)
        response = Response(
            content=json_body,
            status_code=200,
            headers={
                "Content-type": "application/json"
            }
        )
    return response


@app.post("/financial/invoice", status_code=202)
async def financial_invoice(invoice: InvoiceData):
    """
    :description:
        Initiate invoice generation for all calls initiated within the given period.
        For each calling number and given period, one invoice needs to be generated.
        Each invoice has a unique ID. When invoices generation is finished, given callback URL should be called.
        It will signal the client (judge) that the invoice generation is done.
    :param id: *required. Invoice ID. Example: INV_2019-03-02_38121123456
    :request body
        {
            "start": "2019-05-01T00:00:00.00Z",
            "end": "2019-05-31T23:59:59.99Z",
            "callback": "http://judge-thread.hack9.levi9.com/report/invoice/g1y67aeega12384"
        }
    :return:
        - 200 Invoice creation is underway
            - Headers
                - Content-type: application/json
        - 400 Bad parameters
            - Headers
                - Content-type: application/json
            - Body
                {
                    "message": "string"
                }
    :callbacks:
        - POST {$request.body#/callback} Invoice report to submit to control server.
            - request body
                {
                    "master_id": "INV_2019-05-01",
                    "invoices": [
                        {
                            "id": "INV_2019-05-01_38121123456",
                            "calling": "381211234567",
                            "start": "2019-01-01T00:00:00.00Z",
                            "end": "2019-01-31T23:59:59.99Z",
                            "sum": "1341.33",
                            "count": "2319"
                        }
                    ]
                }
            - return
                - 204 Invoice report accepted
                    - Headers
                        - Content-type: application/json
    """
    async with app.postgres.acquire() as con:
        await invoice_generation.submit_new_invoice_request(invoice.start, invoice.end,
                                                            invoice.callback, con)
    return {'message': 'Invoice creation is underway.'}


@app.get("/financial/invoice/{invoice_id}")
async def financial_invoice_id(invoice_id: str):
    """
    :description:
        Get the invoice with the given ID
    :return:
        - 200 Invoice with the given ID
            - Headers
                - Content-type: application/json
            - Body
                {
                    "id": "INV_2019-05-01_38121123456",
                    "calling": "381211234567",
                    "start": "2019-01-01T00:00:00.00Z",
                    "end": "2019-01-31T23:59:59.99Z",
                    "sum": "1341.33",
                    "count": "2319"
                }
        - 404 No such invoice ID
            - Headers
                - Content-type: application/json
            - Body
                {
                    "message": "string"
                }
    """

    if not invoice_id.isdigit():
        return ERROR_404

    async with app.postgres.acquire() as con:
        invoice = await con.fetch(
            GET_INVOICE_RECORD_BY_ID,
            int(invoice_id)
        )
        if invoice:
            response = dict(invoice[0])
        else:
            response = ERROR_404
    return response


@app.post("/financial/report/{calling}")
@app.get("/financial/report/{calling}")
async def financial_report(calling: str):
    """
    :description:
        Get all previous invoices and current, uninvoiced calls of the given number
    :param calling: *required. Calling number. Example 38121123456
    :return:
        - 200 Invoice with the given ID
            - Headers
                - Content-type: application/json
            - Body
                {
                    "calling": "381211234567",
                    "invoices": [
                        {
                            "id": "INV_2019-04-01_38121123456",
                            "sum": "231.22"
                        }
                    ],
                    "remaining": "34.23"
                }
        - 404 Unknown report
            - Headers
                - Content-type: application/json
            - Body
                {
                    "message": "string"
                }
    """
    async with app.postgres.acquire() as con:
        invoices = await con.fetch(
            GET_FINANCIAL_REPORTS_SUM,
            int(calling)
        )

    if not invoices:
        # TODO check this error
        return ERROR_404

    async with app.postgres.acquire() as con:
        remaining = await con.fetchrow(
            GET_FINANCIAL_REPORTS_REMAINING,
            int(calling)
        )
    return {
        "calling": str(calling),
        "invoices": list(map(lambda x: {'id': str(x['id']), 'sum': str(x['sum'])}, invoices)),
        "remaining": str(remaining.get('sum'))
    }
