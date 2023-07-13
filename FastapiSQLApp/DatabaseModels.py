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


class AllScoresTable(Base):
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


class CommonScoresTable(Base):
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


class DbsnfpAllScoresTable(Base):
    __tablename__ = 'dbsnfp_all_scores'
    md5sum = Column(String(255), ForeignKey("seq_md5sum.md5sum"), primary_key=True)
    sift = Column(JSON, nullable=True)
    sift4g = Column(JSON, nullable=True)
    polyphen2_hdiv = Column(JSON, nullable=True)
    polyphen2_hvar = Column(JSON, nullable=True)
    lrt = Column(JSON, nullable=True)
    mutationassessor = Column(JSON, nullable=True)
    fathmm = Column(JSON, nullable=True)
    dbsnfp_provean = Column(JSON, nullable=True)
    vest4 = Column(JSON, nullable=True)
    metasvm = Column(JSON, nullable=True)
    metalr = Column(JSON, nullable=True)
    metarnn = Column(JSON, nullable=True)
    m_cap = Column(JSON, nullable=True)
    revel = Column(JSON, nullable=True)
    mutpred = Column(JSON, nullable=True)
    mvp = Column(JSON, nullable=True)
    mpc = Column(JSON, nullable=True)
    primateai = Column(JSON, nullable=True)
    deogen2 = Column(JSON, nullable=True)
    bayesdel_addaf_score = Column(JSON, nullable=True)
    bayesdel_noaf_score = Column(JSON, nullable=True)
    clinpred = Column(JSON, nullable=True)
    lists2 = Column(JSON, nullable=True)
    cadd = Column(JSON, nullable=True)
    cadd_hg19 = Column(JSON, nullable=True)
    dann = Column(JSON, nullable=True)
    fathmm_mkl_coding = Column(JSON, nullable=True)
    fathmm_xf_coding = Column(JSON, nullable=True)
    eigen_raw_coding = Column(JSON, nullable=True)
    genocanyon = Column(JSON, nullable=True)
    linsight = Column(JSON, nullable=True)
    md5sum_relationship = relationship("Md5sum", backref="dbsnfp_all_scores")


class DbsnfpCommonScoresTable(Base):
    __tablename__ = 'dbsnfp_common_scores'
    md5sum = Column(String(255), ForeignKey("seq_md5sum.md5sum"), primary_key=True)
    sift = Column(JSON)
    sift4g = Column(JSON)
    polyphen2_hdiv = Column(JSON)
    polyphen2_hvar = Column(JSON)
    lrt = Column(JSON)
    mutationassessor = Column(JSON)
    fathmm = Column(JSON)
    dbsnfp_provean = Column(JSON)
    vest4 = Column(JSON)
    metasvm = Column(JSON)
    metalr = Column(JSON)
    metarnn = Column(JSON)
    m_cap = Column(JSON)
    revel = Column(JSON)
    mutpred = Column(JSON)
    mvp = Column(JSON)
    mpc = Column(JSON)
    primateai = Column(JSON)
    deogen2 = Column(JSON)
    bayesdel_addaf_score = Column(JSON)
    bayesdel_noaf_score = Column(JSON)
    clinpred = Column(JSON)
    lists2 = Column(JSON)
    cadd = Column(JSON)
    cadd_hg19 = Column(JSON)
    dann = Column(JSON)
    fathmm_mkl_coding = Column(JSON)
    fathmm_xf_coding = Column(JSON)
    eigen_raw_coding = Column(JSON)
    genocanyon = Column(JSON)
    linsight = Column(JSON)
    md5sum_relationship = relationship("Md5sum", backref="dbsnfp_common_scores")


class IdTable(Base):
    __tablename__ = 'id_table'
    entry = Column(String, primary_key=True)
    gene_name = Column(String)
    entry_version = Column(Integer)
    gene_name_synonym = Column(String, nullable=True)
    md5sum = Column(String(255), ForeignKey("seq_md5sum.md5sum"))
    md5sum_relationship = relationship("Md5sum", backref="id_table")
