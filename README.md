# atmm

The database is consists of two main tables.
- Md5sum (unique, primary key) - Sequence
- Md5sum - Scores in Json format (for each tool)


## DATA COLLECTION

### Efin
Dataset is downloaded from http://paed.hku.hk/efin/download.html on 10th May 2022
```
wget http://147.8.193.83/EFIN/EFIN_0.1.download.csv.tar.gz
tar -zxvf EFIN_0.1.download.csv.tar.gz
```
Then, since two table are required for the database, the data was modified with ./Data-Parse/Efin_Data_Format_Code.py

#### Efin threshold values:

<p>for swissprot trained scores 0.6 (equal or higher than 0.6 → neutral, lower than 0.6 → damaging</p>
<p>for humdiv trained scores 0.28 (equal or higher than 0.28 → damaging, lower than 0.28 → neutral</p>


### List-S2

Dataset is downloaded from https://borealisdata.ca/dataset.xhtml?persistentId=doi:10.5683/SP2/PM9TAB on 10th May 2022

```
wget https://borealisdata.ca/api/access/datafile/100619 
wget https://borealisdata.ca/api/access/datafile/100621
wget https://borealisdata.ca/api/access/datafile/100620
wget https://borealisdata.ca/api/access/datafile/100616
mv LIST-S2_Human_UniParc_2019_10_part1 LIST-S2_Human_UniParc_2019_10.tsv.gz
cat LIST-S2_Human_UniParc_2019_10_part2 >> LIST-S2_Human_UniParc_2019_10.tsv.gz
cat LIST-S2_Human_UniParc_2019_10_part3 >> LIST-S2_Human_UniParc_2019_10.tsv.gz
cat LIST-S2_Human_UniParc_2019_10_part4 >> LIST-S2_Human_UniParc_2019_10.tsv.gz
```
Then, since two table are required for the database, the data was modified with ./Data-Parse/ListS2_Data_Format_Code.py

#### List-s2 threshold values:
<p>Generic threshold: 0.85</p>
<p>Equal to 0.85 or higher: deleterious</p>
<p>lower than 0.85: benign</p>


### SIFT4g

The source code was downloaded from https://github.com/rvaser/sift4g on 13th August 2022. It is installed as written on github page.

The query sequences downloaded from https://ftp.uniprot.org/pub/databases/uniprot/uniref/uniref100/uniref100.xml.gz (last modified:2022-08-03). Each protein's fasta file was saved separately to the input folder and MD5sum-sequence file was created with ./Data-Parse/Current_uniref100_Parse.py

The database has been downloaded from https://www.uniprot.org/help/downloads (swissprot and trembl) || August 2022. 
Swissprot and Swissprot/Trembl are used for calculations as a database parameter.

```
for file in INPUT_FOLDER_PATH; do ./bin/sift4g -q $file -d DATABASE_PATH --outfmt light --out OUTPUT_FOLDER_PATH; done

```
The code was executed with these parameters:

gap opening penalty: 10

gap extention penalty: 1

similarity matrix: BLOSUM_62

evalue threshold: 0.0001

alignment algorithm: Smith-Waterman local alignment

median-threshold: 2.75

kmer-length: 5 (length of kmers used for database search)

Since prediction files are separately for protein's fasta folder, each of them merged into a tsv file with ./Data-Parse/Sift4G_Data_Merge.py


#### Sift-4g threshold values:
<p>If the score is equal or lower than 0.05 -> damaging </p>
<p>If the score is greater than 0.05 -> tolerated </p>



### Polyphen-2

The source code was downloaded from http://genetics.bwh.harvard.edu/pph2/dokuwiki/downloads on 7th September 2022. 

```
wget http://genetics.bwh.harvard.edu/pph2/dokuwiki/_media/polyphen-2.2.3r407.tar.gz
tar -zxvf polyphen-2.2.3r407.tar.gz

```
The other databases were installed according to the INSTALL file inside the tarball.

The reference proteome that was downloaded from https://www.uniprot.org/proteomes/UP000005640 was used as query.

Since query fasta file size is too big, polyphen's parallel execution script (run_pph4.sh) that is written in its READ ME file was used.
```
#!/bin/bash
M=4 # number of program instances to run
for (( N=1; N<=$M; N++ )); do
$PPH/bin/run_pph.pl -r $N/$M "$@" 1>pph$N.features 2>pph$N.log &
done
wait
rm -f pph.features pph.log
for (( N=1; N<=$M; N++ )); do
cat pph$N.features >>pph.features
cat pph$N.log >>pph.log
rm -f pph$N.features pph$N.log
done
```
-d dumpdir (directory for auxiliary output files)
-s fasta file
subs.input -> input file for all theoric amino acids changes

```
#CREATING INPUT SUBSTITUTION FILE
aa_list = ['A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'Y']

with open('ref_proteome.fasta') as n:
    q = n.read().splitlines()

with open('subs.input', mode='w') as b:
    for el in q:
        if el.startswith('>'):
            p_id = el.split('|')[1]
            m = 0
        else:
            for j in range(len(el)):
                for k in aa_list:
                    b.write(p_id + '\t' + f'{m + 1}' + '\t' + el[j] + '\t' + k + '\n')
                m += 1

```


```
./run_pph4.sh -d /var/tmp/scratch -s ref_proteome.fasta subs.input > run_pph4.log 2>&1 &
```


#### Polyphen-2 threshold values:
<p>0.0 to 0.15 -- Variants with scores in this range are predicted to be benign. </p>
<p>0.15 to 1.0 -- Variants with scores in this range are possibly damaging.</p>
<p>0.85 to 1.0 -- Variants with scores in this range are more confidently predicted to be damaging.</p>


<p></p>
<p></p>

## BUILDING THE DATABASE 

<p>PostgreSQL (psql) was used to create the database.</p>

<p>First you must log in to the psql command-line.</p>

```
CREATE DATABASE protein_variants_db;
\connect protein_variants_db;
#md5sum - sequence dump
CREATE TABLE seq_md5sum (
	md5sum VARCHAR(128) UNIQUE NOT NULL,
	sequence TEXT NOT NULL,
	PRIMARY KEY(md5sum)
);
CREATE TABLE temp (
	md5sum VARCHAR(128) NOT NULL,
	sequence TEXT NOT NULL);
COPY temp FROM 'MD5SUM-SEQUENCE FILE PATH' USING DELIMITERS E'\t' WITH NULL AS '\null' CSV HEADER;

insert into seq_md5sum SELECT distinct * FROM temp ON CONFLICT (md5sum) DO nothing;

drop table "temp";

#dataset dump

CREATE TABLE {DATASET NAME} (md5sum VARCHAR(128) NOT NULL,
                            scores JSONb not null,
                            FOREIGN KEY (md5sum)
                              REFERENCES seq_md5sum (md5sum));
                              
CREATE TABLE templ (
                                md5sum VARCHAR(128) NOT NULL,
                                scores JSONb not null;
                                
COPY templ FROM SCORE_PATH USING DELIMITERS E'\t' WITH NULL AS '\null' CSV header QUOTE E'\b' ESCAPE '\';    
insert into {DATASET NAME} select distinct * from templ on conflict (md5sum) do nothing;

drop table templ;

```
Also ./SQL-script/Script.py can add tables to the database after it has been created with CREATE DATABASE command.
```
python3 ./SQL-script/Script.py -h
```

## FAST-API 


## Sample database setup

Inside the ./test_files there are sample files obtained from Efin and List-s2. The sample database can be built according to README file using them. 


## References
<p>Adzhubei IA, Schmidt S, Peshkin L, Ramensky VE, Gerasimova A, Bork P, Kondrashov AS, Sunyaev SR. Nat Methods 7(4):248-249 (2010).</p>
<p>Malhis N, Jacobson M, Jones SJM, Gsponer J. LIST-S2: taxonomy based sorting of deleterious missense mutations across species. Nucleic Acids Res. 2020 Jul 2;48(W1):W154-W161. doi: 10.1093/nar/gkaa288. PMID: 32352516; PMCID: PMC7319545.</p>
<p>Ng PC, Henikoff S. Predicting deleterious amino acid substitutions. Genome Res. 2001 May;11(5):863-74. doi: 10.1101/gr.176601. PMID: 11337480; PMCID: PMC311071.</p>
<p>Zeng, S., Yang, J., Chung, B.HY. et al. EFIN: predicting the functional impact of nonsynonymous single nucleotide polymorphisms in human genome. BMC Genomics 15, 455 (2014). https://doi.org/10.1186/1471-2164-15-455</p>
