from sqlalchemy import Column, String, JSON, Text, ForeignKey, DateTime, Integer
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Md5sum(Base):
    __tablename__ = 'seq_md5sum'
    md5sum = Column(String(255), primary_key=True)
    sequence = Column(Text, nullable=False, unique=True)


class UniprotMetaData(Base):
    __tablename__ = 'uniprot_data'
    uniprotkb_id = Column(String, primary_key=True)
    seq = Column(Text, nullable=False)
    md5sum = Column(String(255), ForeignKey("seq_md5sum.md5sum"), unique=True)
    updated = Column(DateTime)


class All_scores(Base):
    __tablename__ = 'all_tool_scores'
    md5sum = Column(String(255), ForeignKey("seq_md5sum.md5sum"), primary_key=True)
    pph_humdiv = Column(JSON, nullable=True)
    pph_humvar = Column(JSON, nullable=True)
    sift4g_sp_trembl = Column(JSON, nullable=True)
    sift4g_swissprot = Column(JSON, nullable=True)
    lists2 = Column(JSON, nullable=True)
    efin_humdiv = Column(JSON, nullable=True)
    efin_swissprot = Column(JSON, nullable=True)
    provean = Column(JSON, nullable=True)
    phact = Column(JSON, nullable=True)
    phactboost = Column(JSON, nullable=True)
    md5sum_relationship = relationship("Md5sum", backref="all_tool_scores")


class Common_scores(Base):
    __tablename__ = 'common_scores'
    md5sum = Column(String(255), ForeignKey("seq_md5sum.md5sum"), primary_key=True)

    pph_humdiv = Column(JSON)
    pph_humvar = Column(JSON)
    sift4g_sp_trembl = Column(JSON)
    sift4g_swissprot = Column(JSON)
    lists2 = Column(JSON)
    efin_humdiv = Column(JSON)
    efin_swissprot = Column(JSON)
    provean = Column(JSON)
    phact = Column(JSON)
    phactboost = Column(JSON)
    md5sum_relationship = relationship("Md5sum", backref="common_scores")




class IdTable(Base):
    __tablename__ = 'id_table'
    entry = Column(String, primary_key=True)
    gene_name = Column(String)
    entry_version = Column(Integer)
    gene_name_synonym = Column(String, nullable=True)
    md5sum = Column(String(255), ForeignKey("seq_md5sum.md5sum"))
    md5sum_relationship = relationship("Md5sum", backref="id_table")
