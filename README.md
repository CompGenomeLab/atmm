# atmm

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

The query sequences downloaded from https://ftp.uniprot.org/pub/databases/uniprot/uniref/uniref100/ (uniref100). Each protein saved separately to the input folder.

The database has been downloaded from https://www.uniprot.org/help/downloads (swissprot and trembl) || August 2022. 
Swissprot and Swissprot/Trembl are used for calculations as a database parameter.

```
for file in INPUT_FOLDER_PATH; do ./bin/sift4g -q $file -d DATABASE_PATH --outfmt light --out OUTPUT_FOLDER_PATH; done

```

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
./run_pph4.sh -d /var/tmp/scratch -s ref_proteome.fasta subs.input > run_pph4.log 2>&1 &
```


#### Polyphen-2 threshold values:
<p>0.0 to 0.15 -- Variants with scores in this range are predicted to be benign. </p>
<p>0.15 to 1.0 -- Variants with scores in this range are possibly damaging.</p>
<p>0.85 to 1.0 -- Variants with scores in this range are more confidently predicted to be damaging.</p>


<p></p>
<p></p>


### References
<p>Zeng, S., Yang, J., Chung, B.HY. et al. EFIN: predicting the functional impact of nonsynonymous single nucleotide polymorphisms in human genome. BMC Genomics 15, 455 (2014). https://doi.org/10.1186/1471-2164-15-455</p>
<p>Malhis N, Jacobson M, Jones SJM, Gsponer J. LIST-S2: taxonomy based sorting of deleterious missense mutations across species. Nucleic Acids Res. 2020 Jul 2;48(W1):W154-W161. doi: 10.1093/nar/gkaa288. PMID: 32352516; PMCID: PMC7319545.</p>
<p>Ng PC, Henikoff S. Predicting deleterious amino acid substitutions. Genome Res. 2001 May;11(5):863-74. doi: 10.1101/gr.176601. PMID: 11337480; PMCID: PMC311071.</p>
<p>Adzhubei IA, Schmidt S, Peshkin L, Ramensky VE, Gerasimova A, Bork P, Kondrashov AS, Sunyaev SR. Nat Methods 7(4):248-249 (2010).</p>
