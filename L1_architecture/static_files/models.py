# Here is where we declare our models 
from typing import Literal,Optional
from pydantic import BaseModel

class info(BaseModel):
    board_name: str
    person_name: Optional[str]
    sprint_name: Optional[str]


class Evaluated_metrics(BaseModel):
    classification: str
    strengths: list[str]
    improvement_areas: list[str]
    revised_version: str