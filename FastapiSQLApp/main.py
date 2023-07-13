from typing import Optional

import requests
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Query
from starlette.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

from DatabaseConnection import session
from DatabaseModels import Md5sum, AllScoresTable, CommonScoresTable, IdTable, DbsnfpAllScoresTable, \
    DbsnfpCommonScoresTable
from PydanticModels import Md5sumSeq, AllScores, CommonScores, DbsnfpAllScores, DbsnfpCommonScores

app = FastAPI()
db = session
app.add_middleware(HTTPSRedirectMiddleware)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def md5sum_parameter(md5sum: str, q: Optional[int] = None) -> dict:
    exists = db.query(Md5sum.md5sum).filter_by(md5sum=md5sum).first() is not None

    if not exists:
        raise HTTPException(status_code=400, detail="Md5sum not found")

    parameters = {"md5sum": md5sum}
    if q == 1:
        parameters.update({"q": q})

    return parameters


async def uniprotid_parameter(uniprotid: str, q: Optional[int] = None) -> dict:
    md5sum = db.query(IdTable.md5sum).filter_by(entry=uniprotid).first()
    md5sum_exist = md5sum is not None
    if not md5sum_exist:
        raise HTTPException(status_code=400, detail="Entry not found in database")
    parameters = {"md5sum": md5sum[0]}
    if q == 1:
        parameters.update({"q": q})

    return parameters


async def geneid_parameter(geneid: str, q: Optional[int] = None) -> dict:
    md5sum = db.query(IdTable.md5sum).filter_by(gene_name=geneid).first()
    md5sum_exist = md5sum is not None
    if not md5sum_exist:
        raise HTTPException(status_code=400, detail="geneid not found in database")
    parameters = {"md5sum": md5sum[0]}
    if q == 1:
        parameters.update({"q": q})

    return parameters


def get_uniprot_metadata(md5sum):
    requesturl = f"https://www.ebi.ac.uk/proteins/api/proteins?offset=0&size=100&md5={md5sum}"

    r = requests.get(requesturl, headers={"Accept": "application/json"})

    if not r.ok:
        raise HTTPException(status_code=500, detail="Metadata Problem")

    responsebody = r.text
    return responsebody


@app.get("/")
def main():
    return RedirectResponse(url="/docs/")


@app.get("/database/sequence_to_md5sum/{sequence}", response_model=Md5sumSeq, status_code=200,
         summary="Md5sum codes of sequences",
         description="Enter sequence to get Md5sum code of sequence in the database.")
async def sequence_to_md5sum(sequence: str):
    # Add your validation here
    return db.query(Md5sum).filter(Md5sum.sequence == sequence).first()


@app.get("/database/md5sum_to_sequence/{md5sum}", response_model=Md5sumSeq, status_code=200,
         summary="Md5sum codes of sequences", description="Enter Md5sum to get protein sequence in the database.")
async def md5sum_to_sequence(common: dict = Depends(md5sum_parameter)):
    return db.query(Md5sum).filter(Md5sum.md5sum == common.get("md5sum")).first()


@app.get("/database/all_scores/md5sum/{md5sum}", status_code=200, response_model=AllScores,
         response_model_exclude_none=True, summary="All available scores for a protein",
         description="This method returns all available tools' scores of a protein", )
async def get_AllScores_for_md5sum(common: dict = Depends(md5sum_parameter)):
    return db.query(AllScoresTable).filter(AllScoresTable.md5sum == common.get("md5sum")).first()


@app.get("/database/all_common_scores/md5sum/{md5sum}", status_code=200, response_model=CommonScores,
         summary="All scores for a protein",
         description="This method returns all available tools' scores of a protein", )
async def get_all_CommonScores_for_md5sum(common: dict = Depends(md5sum_parameter)):
    return db.query(CommonScoresTable).filter(CommonScoresTable.md5sum == common.get("md5sum")).first()


@app.get("/database/dbsnfp_all_scores/md5sum/{md5sum}", status_code=200, response_model=DbsnfpAllScores,
         response_model_exclude_none=True, summary="", description="")
async def get_dbsnfp_AllScores_for_md5sum(common: dict = Depends(md5sum_parameter)):
    return db.query(DbsnfpAllScoresTable).filter(DbsnfpAllScoresTable.md5sum == common.get("md5sum")).first()


@app.get("/database/dbsnfp_common_scores/md5sum/{md5sum}", status_code=200, response_model=DbsnfpCommonScores,
         response_model_exclude_none=True, summary="", description="")
async def get_dbsnfp_CommonScores_for_md5sum(common: dict = Depends(md5sum_parameter)):
    return db.query(DbsnfpCommonScoresTable).filter(DbsnfpCommonScoresTable.md5sum == common.get("md5sum")).first()


@app.get("/database/all_scores/uniprotid/{uniprotid}", status_code=200, response_model=AllScores,
         response_model_exclude_none=True, summary="All available scores for a protein",
         description="This method returns all available tools' scores of a protein", )
async def get_AllScores_for_uniprotid(common: dict = Depends(uniprotid_parameter)):
    return db.query(AllScoresTable).filter(AllScoresTable.md5sum == common.get("md5sum")).first()


@app.get("/database/all_common_scores/uniprotid/{uniprotid}", status_code=200, response_model=CommonScores)
async def get_all_CommonScores_for_uniprotid(common: dict = Depends(uniprotid_parameter)):
    return db.query(CommonScoresTable).filter(CommonScoresTable.md5sum == common.get("md5sum")).first()


@app.get("/database/all_scores/geneid/{geneid}", status_code=200, response_model=AllScores,
         response_model_exclude_none=True, summary="All available scores for a protein",
         description="This method returns all available tools' scores of a protein", )
async def get_AllScores_for_geneid(common: dict = Depends(geneid_parameter)):
    return db.query(AllScoresTable).filter(AllScoresTable.md5sum == common.get("md5sum")).first()


@app.get("/database/all_common_scores/geneid/{geneid}", status_code=200, response_model=CommonScores)
async def get_all_CommonScores_for_geneid(common: dict = Depends(geneid_parameter)):
    return db.query(CommonScoresTable).filter(CommonScoresTable.md5sum == common.get("md5sum")).first()


@app.get("/database/get_geneid/{geneid}", response_model=list, status_code=200)
async def get_geneid(geneid: str):
    search = "{}%".format(geneid)
    geneids = [i.gene_name for i in db.query(IdTable.gene_name).filter(IdTable.gene_name.like(search)).all()]
    if len(geneids) > 10:
        return []
    else:
        return geneids


@app.get("/database/get_uniprotid/{uniprotid}", response_model=list, status_code=200)
async def get_uniprotid(uniprotid: str):
    search = "{}%".format(uniprotid)
    uniprotids = [i.entry for i in db.query(IdTable.entry).filter(IdTable.entry.like(search)).all()]
    if len(uniprotids) > 10:
        return []
    else:
        return uniprotids


@app.get("/database/md5sum", status_code=200)
async def get_common_md5sum():
    return db.query(AllScores.md5sum).all()


if __name__ == "__main__":
    uvicorn.run("main:app",
                host="10.3.2.13",
                port=8080,
                ssl_keyfile="/home2/mehmet/domain_key.pem",
                ssl_certfile="/home2/mehmet/domain.pem")
