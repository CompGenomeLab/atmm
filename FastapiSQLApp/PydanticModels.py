from pydantic import BaseModel
from typing import List, Optional

#This script uses pydantic to validate the data coming from PostgreSQL database.


class ScoreTables(BaseModel):
    md5sum: str
    scores: dict
    uniprot_metadata: Optional[list]

    class Config:
        orm_mode = True


class Md5sumSeq(BaseModel):
    md5sum: str
    sequence: str

    class Config:
        orm_mode = True


class AllScores(BaseModel):
    md5sum: str
    Sift: Optional[dict]
    Provean: Optional[dict]
    Lists2: Optional[dict]
    Efin: Optional[dict]
    Polyphen: Optional[dict]
        
    class Config:
        orm_mode = True
