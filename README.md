# atmm

### Efin
Dataset is downloaded from http://paed.hku.hk/efin/download.html on 10th May 2022
```
wget http://147.8.193.83/EFIN/EFIN_0.1.download.csv.tar.gz
```

Efin threshold values:

for swissprot trained scores 0.6 (equal or higher than 0.6 → damaging, lower than 0.6 → neutral
for humdiv trained scores 0.28


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

