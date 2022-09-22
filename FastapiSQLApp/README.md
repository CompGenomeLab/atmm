# Main.py
This project uses four main python libraries. These are fastapi, sqlalchemy, pydantic, and uvicorn. The main file is main.py where the restapi is made. The fastapi library is used to build the api for this project. Uvicorn is also used for the ASGI. The main file is consist of all methods which is used in the restAPI. In this app, we specified all methods a specific pathway. These methods generally requires a md5sum hash code of interested proteins. It returns the scores of all theoric amino acid changes in one protein depending the selection of table. These tables also take one more parameter called "q" which is used to indicate whether the user is interested in getting the metadata of the protein sequence from the uniprot database. 

```

@app.get("/database/sift/{md5sum}", response_model=ScoreTables, status_code=200, summary="Sift scores of a protein",
         description="Enter Md5sum of a protein sequence to get the sift scores of all possible sift aminoacid "
                     "variants pathogenicity scores from Sift Database.")
async def get_sift_item(common: dict = Depends(md5sum_parameter)):
    if common.get("q") == 1:
        a = db.query(Sift).filter(Sift.md5sum == common.get("md5sum")).first().__dict__
        a.update({"uniprot_metadata": json.loads(get_uniprot_metadata(common.get("md5sum")))})
        return a
    return db.query(Sift).filter(Sift.md5sum == common.get("md5sum")).first()
```



# PydanticModels.py

All the data coming from the database are validated by the pydantic models in the PydanticModels.py. It uses BaseModel to inherit the types. 

```

class ScoreTables(BaseModel):
    md5sum: str
    scores: dict
    uniprot_metadata: Optional[list]

    class Config:
        orm_mode = True
```

# DatabaseModels.py
```
class Md5sum(Base):
    __tablename__ = 'seq_md5sum'
    md5sum = Column(String(255), primary_key=True)
    sequence = Column(Text, nullable=False, unique=True)
```

# DatabaseConnection.py
This is an example of a json credentials file, all information are required. Both need their self file. 
```
{"ssh_credentials":{
        "ipaddress": "xxx",
        "SSH port": 22,
        "User_name": "xxx",
        "password": "xxx"
    }}
 {"database_credentials":{
        "port": 5432,
        "database_name": "xxx",
        "database_user": "xxx",
        "database_password": "xxx"
    }}
    ```
