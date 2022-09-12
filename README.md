# atmm

### Efin
Dataset is downloaded from http://paed.hku.hk/efin/download.html on 10th May 2022
```
wget http://147.8.193.83/EFIN/EFIN_0.1.download.csv.tar.gz
```

Efin threshold values:

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

<p>Generic threshold: 0.85</p>
<p>Equal to 0.85 or higher: deleterious</p>
<p>lower than 0.85: benign</p>


### SIFT4g

The source code is downloaded from https://github.com/rvaser/sift4g on 13th August 2022. It is installed as written on github page.

The database has been downloaded from https://www.uniprot.org/help/downloads (swissprot and trembl) || August 2022. 
Swissprot and Swissprot/Trembl are used for calculations as a database parameter.







### References
<p>Zeng, S., Yang, J., Chung, B.HY. et al. EFIN: predicting the functional impact of nonsynonymous single nucleotide polymorphisms in human genome. BMC Genomics 15, 455 (2014). https://doi.org/10.1186/1471-2164-15-455</p>
<p>Malhis N, Jacobson M, Jones SJM, Gsponer J. LIST-S2: taxonomy based sorting of deleterious missense mutations across species. Nucleic Acids Res. 2020 Jul 2;48(W1):W154-W161. doi: 10.1093/nar/gkaa288. PMID: 32352516; PMCID: PMC7319545.</p>
<p>Ng PC, Henikoff S. Predicting deleterious amino acid substitutions. Genome Res. 2001 May;11(5):863-74. doi: 10.1101/gr.176601. PMID: 11337480; PMCID: PMC311071.</p>
