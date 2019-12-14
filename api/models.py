from typing import Optional
from datetime import datetime, timezone

from pydantic import BaseConfig, BaseModel


class RWModel(BaseModel):
    class Config(BaseConfig):
        allow_population_by_alias = True
        json_encoders = {
            datetime: lambda dt: dt.replace(tzinfo=timezone.utc)
            .isoformat()
            .replace("+00:00", "Z")
        }


class CallData(BaseModel):
    """
    Example input data
    {
      "calling": "381211234567",
      "called": "38164111222333",
      "start": "2019-05-23T21:03:33.30Z",
      "duration": "450"
    }
    Example response:
    {
      "calling": "381211234567",
      "called": "38164111222333",
      "start": "2019-05-23T21:03:33.30Z",
      "duration": "350",
      "rounded": "355",
      "price": "0.4",
      "cost": "2.367"
    }
    """
    # id: Optional[str] = None
    calling: str
    called: str
    start: datetime
    duration: int
    # FIXME should be calculated!
    rounded: int = 1
    price: float = 1
    cost: float = 1


class InvoiceData(BaseModel):
    """
    Example input data
        - Request data:
    {
      "start": "2019-05-01T00:00:00.00Z",
      "end": "2019-05-31T23:59:59.99Z",
      "callback": "http://judge-thread.hack9.levi9.com/report/invoice/g1y67aeega12384"
    }
    """
    # id: Optional[str] = None
    start: datetime
    end: datetime
    callback: str


class CallDataInResponse(RWModel):
    call_data: CallData
