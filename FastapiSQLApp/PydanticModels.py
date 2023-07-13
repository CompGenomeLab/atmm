import json

from pydantic.error_wrappers import ValidationError
from pydantic.main import BaseModel
from pydantic.parse import Protocol
from pydantic.types import StrBytes
from typing import Any, Optional, Type, Dict, List


class BaseModelNoException(BaseModel):
    def __init__(__pydantic_self__, **data: Any) -> None:
        try:
            super(BaseModelNoException, __pydantic_self__).__init__(**data)
        except ValidationError as pve:
            print(f'This is a warning. __init__ failed to validate:\n {json.dumps(data, indent=4)}\n')
            print(f'This is the original exception:\n{pve.json()}')

    def __setattr__(self, name, value):
        try:
            super(BaseModelNoException, self).__setattr__(name, value)
        except ValidationError as pve:
            print(f'This is a warning. __setattr__ failed to validate:\n {json.dumps({name: value}, indent=4)}')
            print(f'This is the original exception:\n{pve.json()}')
        else:
            return None

    @classmethod
    def parse_obj(cls: Type['BaseModelNoException'], obj: Any) -> Any:
        try:
            return super(BaseModelNoException, cls).parse_obj(obj)
        except ValidationError as pve:
            print(f'This is a warning. parse_obj failed to validate:\n {json.dumps(obj, indent=4)}')
            print(f'This is the original exception:\n{pve.json()}')
            return None

    @classmethod
    def parse_raw(cls: Type['BaseModelNoException'], b: StrBytes, *, content_type: str = None, encoding: str = 'utf8',
                  proto: Protocol = None, allow_pickle: bool = False, ) -> Any:
        try:
            return super(BaseModelNoException, cls).parse_raw(b=b, content_type=content_type, encoding=encoding,
                                                              proto=proto, allow_pickle=allow_pickle)
        except ValidationError as pve:
            print(f'This is a warning. parse_raw failed to validate:\n {b}')
            print(f'This is the original exception:\n{pve.json()}')
            return None


class Md5sumSeq(BaseModelNoException):
    md5sum: str
    sequence: str

    class Config:
        orm_mode = True


class AllScores(BaseModelNoException):
    md5sum: str
    pph_humdiv: Optional[Dict]
    pph_humvar: Optional[Dict]
    sift4g_sp_trembl: Optional[Dict]
    sift4g_swissprot: Optional[Dict]
    lists2: Optional[Dict]
    efin_humdiv: Optional[Dict]
    efin_swissprot: Optional[Dict]
    provean: Optional[Dict]
    uniprot_metadata: Optional[List]
    phact: Optional[Dict]
    phactboost: Optional[Dict]

    class Config:
        orm_mode = True


class DbsnfpAllScores(BaseModel):
    md5sum: str
    sift: Optional[Dict]
    sift4g: Optional[Dict]
    polyphen2_hdiv: Optional[Dict]
    polyphen2_hvar: Optional[Dict]
    lrt: Optional[Dict]
    mutationassessor: Optional[Dict]
    fathmm: Optional[Dict]
    dbsnfp_provean: Optional[Dict]
    vest4: Optional[Dict]
    metasvm: Optional[Dict]
    metalr: Optional[Dict]
    metarnn: Optional[Dict]
    m_cap: Optional[Dict]
    revel: Optional[Dict]
    mutpred: Optional[Dict]
    mvp: Optional[Dict]
    mpc: Optional[Dict]
    primateai: Optional[Dict]
    deogen2: Optional[Dict]
    bayesdel_addaf_score: Optional[Dict]
    bayesdel_noaf_score: Optional[Dict]
    clinpred: Optional[Dict]
    lists2: Optional[Dict]
    cadd: Optional[Dict]
    cadd_hg19: Optional[Dict]
    dann: Optional[Dict]
    fathmm_mkl_coding: Optional[Dict]
    fathmm_xf_coding: Optional[Dict]
    eigen_raw_coding: Optional[Dict]
    genocanyon: Optional[Dict]
    linsight: Optional[Dict]

    class Config:
        orm_mode = True


class CommonScores(BaseModelNoException):
    md5sum: str
    pph_humdiv: Dict
    pph_humvar: Dict
    sift4g_sp_trembl: Dict
    sift4g_swissprot: Dict
    lists2: Dict
    efin_humdiv: Dict
    efin_swissprot: Dict
    provean: Dict
    phact: Dict
    phactboost: Dict
    uniprot_metadata: Optional[list]

    class Config:
        orm_mode = True


class DbsnfpCommonScores(BaseModel):
    md5sum: str
    sift: Optional[Dict]
    sift4g: Optional[Dict]
    polyphen2_hdiv: Optional[Dict]
    polyphen2_hvar: Optional[Dict]
    lrt: Optional[Dict]
    mutationassessor: Optional[Dict]
    fathmm: Optional[Dict]
    dbsnfp_provean: Optional[Dict]
    vest4: Optional[Dict]
    metasvm: Optional[Dict]
    metalr: Optional[Dict]
    metarnn: Optional[Dict]
    m_cap: Optional[Dict]
    revel: Optional[Dict]
    mutpred: Optional[Dict]
    mvp: Optional[Dict]
    mpc: Optional[Dict]
    primateai: Optional[Dict]
    deogen2: Optional[Dict]
    bayesdel_addaf_score: Optional[Dict]
    bayesdel_noaf_score: Optional[Dict]
    clinpred: Optional[Dict]
    lists2: Optional[Dict]
    cadd: Optional[Dict]
    cadd_hg19: Optional[Dict]
    dann: Optional[Dict]
    fathmm_mkl_coding: Optional[Dict]
    fathmm_xf_coding: Optional[Dict]
    eigen_raw_coding: Optional[Dict]
    genocanyon: Optional[Dict]
    linsight: Optional[Dict]
    uniprot_metadata: Optional[List[Dict]]

    class Config:
        orm_mode = True
