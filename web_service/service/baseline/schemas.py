from typing import List, Dict
from pydantic import BaseModel


class ObjectSubject(BaseModel):
    objects: List[str]
    subjects: List[str]


class PredictProba(BaseModel):
    value: Dict[str, float]


class Timestamp(BaseModel):
    id: int
    timestamp: int
