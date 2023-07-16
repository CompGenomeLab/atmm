from typing import Optional
import argparse

import requests
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from starlette.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

from DatabaseConnection import session, DatabaseConnector, _read_json_credentials
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


async def get_md5sum_parameter(md5sum: str, q: Optional[int] = None) -> dict:
    """
    Get parameters based on the provided md5sum.

    Args:
        md5sum (str): MD5 hash of the sequence.
        q (int, optional): An optional parameter that may be used in queries.

    Returns:
        dict: A dictionary containing the provided md5sum and optionally 'q'.
    """
    exists = db.query(Md5sum.md5sum).filter_by(md5sum=md5sum).first() is not None

    if not exists:
        raise HTTPException(status_code=400, detail="Md5sum not found")

    parameters = {"md5sum": md5sum}
    if q == 1:
        parameters.update({"q": q})

    return parameters


async def get_uniprotid_parameter(uniprotid: str, q: Optional[int] = None) -> dict:
    """
    Get parameters based on the provided Uniprot ID.

    Args:
        uniprotid (str): Uniprot ID of the sequence.
        q (int, optional): An optional parameter that may be used in queries.

    Returns:
        dict: A dictionary containing the md5sum associated with the Uniprot ID and optionally 'q'.
    """
    md5sum = db.query(IdTable.md5sum).filter_by(entry=uniprotid).first()
    md5sum_exist = md5sum is not None
    if not md5sum_exist:
        raise HTTPException(status_code=400, detail="Entry not found in database")
    parameters = {"md5sum": md5sum[0]}
    if q == 1:
        parameters.update({"q": q})

    return parameters


async def get_geneid_parameter(geneid: str, q: Optional[int] = None) -> dict:
    """
    Get parameters based on the provided gene ID.

    Args:
        geneid (str): Gene ID of the sequence.
        q (int, optional): An optional parameter that may be used in queries.

    Returns:
        dict: A dictionary containing the md5sum associated with the gene ID and optionally 'q'.
    """
    md5sum = db.query(IdTable.md5sum).filter_by(gene_name=geneid).first()
    md5sum_exist = md5sum is not None
    if not md5sum_exist:
        raise HTTPException(status_code=400, detail="geneid not found in database")
    parameters = {"md5sum": md5sum[0]}
    if q == 1:
        parameters.update({"q": q})

    return parameters


def get_uniprot_metadata(md5sum):
    """
    Fetch Uniprot metadata for the provided md5sum.

    Args:
        md5sum (str): MD5 hash of the sequence.

    Returns:
        str: Uniprot metadata in JSON format.
    """
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
async def md5sum_to_sequence(common: dict = Depends(get_md5sum_parameter)):
    return db.query(Md5sum).filter(Md5sum.md5sum == common.get("md5sum")).first()


@app.get("/database/all_scores/md5sum/{md5sum}", status_code=200, response_model=AllScores,
         response_model_exclude_none=True,
         summary="Get All Scores for a Protein by MD5 Sum",
         description="Retrieve all available scores from various tools for a protein, using the MD5 sum as an "
                     "identifier.", )
async def get_all_scores_using_md5sum(common: dict = Depends(get_md5sum_parameter)):
    return db.query(AllScoresTable).filter(AllScoresTable.md5sum == common.get("md5sum")).first()


@app.get("/database/all_common_scores/md5sum/{md5sum}", status_code=200, response_model=CommonScores,
         summary="Get Common Scores for a Protein by MD5 Sum",
         description="Retrieve common scores from various tools for a protein, using the MD5 sum as an identifier.", )
async def get_common_scores_using_md5sum(common: dict = Depends(get_md5sum_parameter)):
    return db.query(CommonScoresTable).filter(CommonScoresTable.md5sum == common.get("md5sum")).first()


@app.get("/database/dbsnfp_all_scores/md5sum/{md5sum}", status_code=200, response_model=DbsnfpAllScores,
         response_model_exclude_none=True,
         summary="Get All dbSNP Scores for a Protein by MD5 Sum",
         description="Retrieve all dbSNP scores for a protein, using the MD5 sum as an identifier.")
async def get_dbsnfp_all_scores_using_md5sum(common: dict = Depends(get_md5sum_parameter)):
    return db.query(DbsnfpAllScoresTable).filter(DbsnfpAllScoresTable.md5sum == common.get("md5sum")).first()


@app.get("/database/dbsnfp_common_scores/md5sum/{md5sum}", status_code=200, response_model=DbsnfpCommonScores,
         response_model_exclude_none=True,
         summary="Get Common dbSNP Scores for a Protein by MD5 Sum",
         description="Retrieve common dbSNP scores for a protein, using the MD5 sum as an identifier.")
async def get_dbsnfp_common_scores_using_md5sum(common: dict = Depends(get_md5sum_parameter)):
    return db.query(DbsnfpCommonScoresTable).filter(DbsnfpCommonScoresTable.md5sum == common.get("md5sum")).first()


@app.get("/database/all_scores/uniprotid/{uniprotid}", status_code=200, response_model=AllScores,
         response_model_exclude_none=True,
         summary="Get All Scores for a Protein by UniProt ID",
         description="Retrieve all available scores from various tools for a protein, using the UniProt ID as an "
                     "identifier.", )
async def get_all_scores_using_uniprotid(common: dict = Depends(get_uniprotid_parameter)):
    return db.query(AllScoresTable).filter(AllScoresTable.md5sum == common.get("md5sum")).first()


@app.get("/database/all_common_scores/uniprotid/{uniprotid}", status_code=200, response_model=CommonScores,
         summary="Get Common Scores for a Protein by UniProt ID",
         description="Retrieve common scores from various tools for a protein, using the UniProt ID as an identifier.")
async def get_common_scores_using_uniprotid(common: dict = Depends(get_uniprotid_parameter)):
    return db.query(CommonScoresTable).filter(CommonScoresTable.md5sum == common.get("md5sum")).first()


@app.get("/database/all_scores/geneid/{geneid}", status_code=200, response_model=AllScores,
         response_model_exclude_none=True,
         summary="Get All Scores for a Protein by Gene ID",
         description="Retrieve all available scores from various tools for a protein, using the Gene ID as an "
                     "identifier.")
async def get_all_scores_using_geneid(common: dict = Depends(get_geneid_parameter)):
    return db.query(AllScoresTable).filter(AllScoresTable.md5sum == common.get("md5sum")).first()


@app.get("/database/all_common_scores/geneid/{geneid}", status_code=200, response_model=CommonScores,
         summary="Get Common Scores for a Protein by Gene ID",
         description="Retrieve common scores from various tools for a protein, using the Gene ID as an identifier.")
async def get_common_scores_using_geneid(common: dict = Depends(get_geneid_parameter)):
    return db.query(CommonScoresTable).filter(CommonScoresTable.md5sum == common.get("md5sum")).first()


@app.get("/database/get_geneid/{geneid}", response_model=list, status_code=200)
async def get_geneid(geneid: str):
    """
    Get gene ID information from the database based on the provided query.

    Args:
        geneid (str): The beginning of the gene ID to search in the database.

    Returns:
        list: A list of gene IDs matching the search query. Empty if more than 10 results found.
    """
    search = "{}%".format(geneid)
    geneids = [i.gene_name for i in db.query(IdTable.gene_name).filter(IdTable.gene_name.like(search)).all()]
    if len(geneids) > 10:
        return []
    else:
        return geneids


@app.get("/database/get_uniprotid/{uniprotid}", response_model=list, status_code=200)
async def get_uniprotid(uniprotid: str):
    """
    Get Uniprot ID information from the database based on the provided query.

    Args:
        uniprotid (str): The beginning of the Uniprot ID to search in the database.

    Returns:
        list: A list of Uniprot IDs matching the search query. Empty if more than 10 results found.
    """
    search = "{}%".format(uniprotid)
    uniprotids = [i.entry for i in db.query(IdTable.entry).filter(IdTable.entry.like(search)).all()]
    if len(uniprotids) > 10:
        return []
    else:
        return uniprotids


@app.get("/database/md5sum", status_code=200)
async def get_common_md5sum():
    """
    Get the md5sum from the AllScores table.

    Returns:
        list: A list of md5sums from the AllScores table.
    """
    return db.query(AllScores.md5sum).all()


def parse_arguments():
    parser = argparse.ArgumentParser(description="Start the API server")
    parser.add_argument('--host', '-H', type=str, required=True)
    parser.add_argument('--port', '-p', type=int, required=True)
    parser.add_argument('--ssl-keyfile', '-sk', type=str, required=False)
    parser.add_argument('--ssl-certfile', '-sc', type=str, required=False)
    parser.add_argument('--dbpath', '-dp', type=str, required=True)
    return parser.parse_args()


def run_uvicorn_server(host, port, ssl_keyfile, ssl_certfile, db_credentials):
    db_connector = DatabaseConnector(_read_json_credentials(db_credentials))
    db_connector.connect()

    uvicorn.run("main:app",
                host=host,
                port=port,
                ssl_keyfile=ssl_keyfile,
                ssl_certfile=ssl_certfile)


args = parse_arguments()

run_uvicorn_server(
    host=args.host,
    port=args.port,
    ssl_keyfile=args.ssl_keyfile,
    ssl_certfile=args.ssl_certfile,
    db_credentials=args.dbpath
)
