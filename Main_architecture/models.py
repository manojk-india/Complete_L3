from pydantic import BaseModel
from typing import Literal


# pydantic classes 
class queries(BaseModel):
    query: list[str]

class info(BaseModel):
    boards: list[str]
    name: list[str]
    time_period: bool

class going_down_or_not(BaseModel):
    value: bool
    reason: str

class where_should_we_go(BaseModel):
     level: Literal["L1 level", "L2 level"]
     reason: str