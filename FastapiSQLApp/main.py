import requests
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from starlette.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from DatabaseConnection import session
from DatabaseModels import Md5sum, All_scores, Common_scores
from PydanticModels import Md5sumSeq, AllScores, CommonScores

app = FastAPI()
db = session

origins = ["*"]
print(db.query(All_scores).filter(All_scores.md5sum == '0003f601d610229eea90fb7f7ff24f05').first())

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



async def md5sum_parameter(md5sum: str, q: int | None = None) -> dict:
    exists = db.query(Md5sum.md5sum).filter_by(md5sum=md5sum).first() is not None

    if not exists:
        raise HTTPException(status_code=400, detail="Md5sum not found")

    parameters = {"md5sum": md5sum}
    if q == 1:
        parameters.update({"q": q})

    return parameters


def get_uniprot_metadata(md5sum):
    requestURL = f"https://www.ebi.ac.uk/proteins/api/proteins?offset=0&size=100&md5={md5sum}"

    r = requests.get(requestURL, headers={"Accept": "application/json"})

    if not r.ok:
        raise HTTPException(status_code=500, detail="Metadata Problem")

    responseBody = r.text
    return responseBody


@app.get("/")
def main():
    return RedirectResponse(url="/docs/")

@app.get("/database/sequence_to_md5sum/{sequence}", response_model=Md5sumSeq, status_code=200,
         summary="Md5sum codes of sequences",
         description="Enter sequence to get Md5sum code of sequence in the database.")
async def sequence_to_md5sum(sequence: str):
    return db.query(Md5sum).filter(Md5sum.sequence == sequence).first()


@app.get("/database/md5sum_to_sequence/{md5sum}", response_model=Md5sumSeq, status_code=200,
         summary="Md5sum codes of sequences", description="Enter Md5sum to get protein sequence in the database.")
async def md5sum_to_sequence(common: dict = Depends(md5sum_parameter)):
    return db.query(Md5sum).filter(Md5sum.md5sum == common.get("md5sum")).first()


@app.get("/database/all_scores/{md5sum}", status_code=200, response_model=AllScores,response_model_exclude_none=True, summary="All available scores for a protein",
         description="This method returns all available tools' scores of a protein", )
async def get_all_scores_for_md5sum(common: dict = Depends(md5sum_parameter)):
    return db.query(All_scores).filter(All_scores.md5sum == common.get("md5sum")).first()

@app.get("/database/all_common_scores/{md5sum}", status_code=200, response_model=CommonScores,summary="All scores for a protein",
         description="This method returns all available tools' scores of a protein", )
async def get_all_common_scores_for_md5sum(common: dict = Depends(md5sum_parameter)):
    return db.query(Common_scores).filter(Common_scores.md5sum == common.get("md5sum")).first()

@app.get("/database/md5sum", status_code=200)
async def get_common_md5sum():
    return db.query(All_scores.md5sum).all()


if __name__ == "__main__":
    uvicorn.run("main:app", host="X.X.X.X", port=8080)
