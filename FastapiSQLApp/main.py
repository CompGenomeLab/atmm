import json

import pandas as pd
import requests
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from starlette.responses import RedirectResponse

from DatabaseConnection import session
from DatabaseModels import Sift, Efin, Provean, Lists2, Md5sum, Polyphen
from PydanticModels import ScoreTables, Md5sumSeq, AllScores

app = FastAPI()
db = session


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


@app.get("/database/sift/{md5sum}", response_model=ScoreTables, status_code=200, summary="Sift scores of a protein",
         description="Enter Md5sum of a protein sequence to get the sift scores of all possible sift aminoacid "
                     "variants pathogenicity scores from Sift Database.")
async def get_sift_item(common: dict = Depends(md5sum_parameter)):
    if common.get("q") == 1:
        a = db.query(Sift).filter(Sift.md5sum == common.get("md5sum")).first().__dict__
        a.update({"uniprot_metadata": json.loads(get_uniprot_metadata(common.get("md5sum")))})
        return a
    return db.query(Sift).filter(Sift.md5sum == common.get("md5sum")).first()


@app.get("/database/efin/{md5sum}", response_model=ScoreTables, status_code=200, summary="Efin scores of a protein",
         description="Enter Md5sum of a protein sequence to get the Efin scores of all possible Efin aminoacid "
                     "variants pathogenicity scores from Sift Database.")
async def get_efin_item(common: dict = Depends(md5sum_parameter)):
    if common.get("q") == 1:
        a = db.query(Efin).filter(Efin.md5sum == common.get("md5sum")).first().__dict__
        a.update({"uniprot_metadata": json.loads(get_uniprot_metadata(common.get("md5sum")))})
        return a
    return db.query(Efin).filter(Efin.md5sum == common.get("md5sum")).first()


@app.get("/database/provean/{md5sum}", response_model=ScoreTables, status_code=200, summary="Provean scores of a protein",
         description="Enter Md5sum of a protein sequence to get the Provean scores of all possible Provean aminoacid "
                     "variants pathogenicity scores from Sift Database.")
async def get_provean_item(common: dict = Depends(md5sum_parameter)):
    if common.get("q") == 1:
        a = db.query(Provean).filter(Provean.md5sum == common.get("md5sum")).first().__dict__
        a.update({"uniprot_metadata": json.loads(get_uniprot_metadata(common.get("md5sum")))})
        return a
    return db.query(Provean).filter(Provean.md5sum == common.get("md5sum")).first()


@app.get("/database/lists2/{md5sum}", response_model=ScoreTables, status_code=200,
         summary="Lists2 scores of a protein",
         description="Enter Md5sum of a protein sequence to get the Lists2 scores of all possible Lists2 aminoacid "
                     "variants pathogenicity scores from Sift Database.")
async def get_lists2_item(common: dict = Depends(md5sum_parameter)):
    if common.get("q") == 1:
        a = db.query(Lists2).filter(Lists2.md5sum == common.get("md5sum")).first().__dict__
        a.update({"uniprot_metadata": json.loads(get_uniprot_metadata(common.get("md5sum")))})
        return a
    return db.query(Lists2).filter(Lists2.md5sum == common.get("md5sum")).first()

@app.get("/database/polyphen/{md5sum}", response_model=ScoreTables, status_code=200,
         summary="Polyphen scores of a protein",
         description="Enter Md5sum of a protein sequence to get the Polyphen scores of all possible Polyphen aminoacid "
                     "variants pathogenicity scores from Polyphen Database.")
async def get_Polyphen_item(common: dict = Depends(md5sum_parameter)):
    if common.get("q") == 1:
        a = db.query(Polyphen).filter(Polyphen.md5sum == common.get("md5sum")).first().__dict__
        a.update({"uniprot_metadata": json.loads(get_uniprot_metadata(common.get("md5sum")))})
        return a
    return db.query(Polyphen).filter(Polyphen.md5sum == common.get("md5sum")).first()

@app.get("/database/sequence_to_md5sum/{sequence}", response_model=Md5sumSeq, status_code=200,
         summary="Md5sum codes of sequences",
         description="Enter sequence to get Md5sum code of sequence in the database.")
async def sequence_to_md5sum(sequence: str):
    return db.query(Md5sum).filter(Md5sum.sequence == sequence).first()


@app.get("/database/md5sum_to_sequence/{md5sum}", response_model=Md5sumSeq, status_code=200,
         summary="Md5sum codes of sequences", description="Enter Md5sum to get protein sequence in the database.")
async def md5sum_to_sequence(common: dict = Depends(md5sum_parameter)):
    return db.query(Md5sum).filter(Md5sum.md5sum == common.get("md5sum")).first()


@app.get("/database/all_scores/{md5sum}", status_code=200, response_model=AllScores, summary="All scores for a protein",
         description="")
async def get_all_scores_for_md5sum(common: dict = Depends(md5sum_parameter)):
    all_scores = {"md5sum": (common.get("md5sum"))}
    dataset_dict = {"Provean": Provean, "Lists2": Lists2, "Sift": Sift, "Efin": Efin, "Polyphen": Polyphen}
    for dataset in dataset_dict.keys():
        key = dataset_dict.get(dataset)
        score = db.query(key).filter(key.md5sum == common.get("md5sum")).first().__dict__
        all_scores[dataset] = score
    return all_scores


@app.get("/database/md5sum", status_code=200)
async def get_common_md5sum():
    md5sum_list = []
    dataset_dict = {"Provean": Provean, "Lists2": Lists2, "Sift": Sift, "Efin": Efin, "Polyphen": Polyphen}
    for dataset in dataset_dict.keys():
        key = dataset_dict.get(dataset)
        md5sums = db.query(key.md5sum).all()
        md5sum_list += list(md5sums)
    md5sum_series = pd.DataFrame(data={"md5sum": [i['md5sum'] for i in md5sum_list]})
    md5sum_count = pd.DataFrame(data=md5sum_series["md5sum"].value_counts()).reset_index()
    md5sum_count.columns = ["md5sum", "count"]
    return md5sum_count.loc[md5sum_count["count"] == 5]["md5sum"].to_list()


if __name__ == "__main__":
    uvicorn.run("main:app", host="10.3.2.13", port=8080)
