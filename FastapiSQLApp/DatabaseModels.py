from sqlalchemy import Column, String, JSON, Text, ForeignKey, DATETIME

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

Base = declarative_base()



class Md5sum(Base):
    __tablename__ = 'seq_md5sum'
    md5sum = Column(String(255), primary_key=True)
    sequence = Column(Text, nullable=False, unique=True)


class Sift(Base):
    __tablename__ = 'sift4g_swissprot'
    md5sum = Column(String(255), ForeignKey("seq_md5sum.md5sum"), primary_key=True)
    scores = Column(JSON, nullable=False)




class Provean(Base):
    __tablename__ = 'provean'
    md5sum = Column(String(255), ForeignKey("seq_md5sum.md5sum"), primary_key=True)
    scores = Column(JSON, nullable=False)


class Lists2(Base):
    __tablename__ = 'lists2'
    md5sum = Column(String(255), ForeignKey("seq_md5sum.md5sum"), primary_key=True)
    scores = Column(JSON, nullable=False)


class Efin(Base):
    __tablename__ = 'efin_humdiv'
    md5sum = Column(String(255), ForeignKey("seq_md5sum.md5sum"), primary_key=True)
    scores = Column(JSON, nullable=False)

class Polyphen(Base):
    __tablename__ = 'Polyphen_humvar'
    md5sum = Column(String(255), ForeignKey("seq_md5sum.md5sum"), primary_key=True)
    scores = Column(JSON, nullable=False)   

class UniprotMetaData(Base):
    __tablename__ = 'uniprot_data'
    uniprotkb_id = Column(String, primary_key=True)
    seq = Column(Text, nullable=False)
    md5sum = Column(String(255), ForeignKey("seq_md5sum.md5sum"), unique=True, )
    updated = Column(DATETIME)
