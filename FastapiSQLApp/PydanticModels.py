from typing import Optional
import json
from typing import no_type_check, Type, Any

from pydantic import BaseModel, ValidationError, StrBytes, Protocol

class BaseModelNoException(BaseModel):
    def __init__(__pydantic_self__, **data: Any) -> None:
        try:
            super(BaseModelNoException, __pydantic_self__).__init__(**data)
        except ValidationError as pve:
            print(f'This is a warning. __init__ failed to validate:\n {json.dumps(data, indent=4)}\n')
            print(f'This is the original exception:\n{pve.json()}')

    @no_type_check
    def __setattr__(self, name, value):
        try:
            return super(BaseModelNoException, self).__setattr__
        except ValidationError as pve:
            print(f'This is a warning. __setattr__ failed to validate:\n {json.dumps({name: value}, indent=4)}')
            print(f'This is the original exception:\n{pve.json()}')
            return None

    @classmethod
    def parse_obj(cls: Type['Model'], obj: Any) -> 'Model':
        try:
            return super(BaseModelNoException, cls).parse_obj(obj)
        except ValidationError as pve:
            print(f'This is a warning. parse_obj failed to validate:\n {json.dumps(obj, indent=4)}')
            print(f'This is the original exception:\n{pve.json()}')
            return None

    @classmethod
    def parse_raw(cls: Type['Model'], b: StrBytes, *, content_type: str = None, encoding: str = 'utf8',
                  proto: Protocol = None, allow_pickle: bool = False, ) -> 'Model':
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
    pph_humdiv: Optional[dict]
    pph_humvar: Optional[dict]
    sift4g_sp_trembl: Optional[dict]
    sift4g_swissprot: Optional[dict]
    lists2: Optional[dict]
    efin_humdiv: Optional[dict]
    efin_swissprot: Optional[dict]
    provean: Optional[dict]
    uniprot_metadata: Optional[list]
    class Config:
        orm_mode = True

class CommonScores(BaseModelNoException):

    md5sum: str
    pph_humdiv: dict
    pph_humvar: dict
    sift4g_sp_trembl: dict
    sift4g_swissprot: dict
    lists2: dict
    efin_humdiv: dict
    efin_swissprot: dict
    provean: dict
    uniprot_metadata: Optional[list]
    class Config:
        orm_mode = True
