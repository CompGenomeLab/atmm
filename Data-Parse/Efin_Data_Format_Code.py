
import hashlib
import json


def csv_reader(file_name):
    for row in open(file_name, "r"):
        yield row.split('\n')[0]


def hash_seq(s):
    result = hashlib.md5(s.encode())
    return result.hexdigest()


def get_sequence(dic) -> str:
    ct = 1
    seq = ''
    for pos, aa in dic.items():
        if int(pos) == ct:
            seq += aa
            ct += 1
            continue
        while int(pos) != ct:
            seq += 'X'
            ct += 1
        seq += aa
        ct = int(pos) + 1
    return seq


EFIN_PATH = "EFIN.csv"


#CREATING SEQUENCE_MD5SUM FILE FOR PRIMARY KEY TABLE
indicator = ''
protein_dict = {}
id_md5 = {}

with open('seq_md5sum.tsv', mode='w') as sm:
    sm.write('md5sum\tsequence\n')

    for row in csv_reader(EFIN_PATH):
        x = row.split(',')
        print(x)
        if x[1] == 'NA' or x[2] == 'NA':
            continue
        if x[0] == 'protein':
            continue
        if indicator != x[0] and indicator != '':
            sequence = get_sequence(protein_dict)
            md5sum = hash_seq(sequence)
            if len(sequence) >= 30:
                id_md5[indicator] = md5sum
                sm.write(f'{md5sum}\t{sequence}\n')
            protein_dict = {}
        indicator = x[0]
        protein_dict[x[1]] = x[2]
    sequence = get_sequence(protein_dict)
    md5sum = hash_seq(sequence)

    if len(sequence) >= 30:
        id_md5[indicator] = md5sum
        sm.write(f'{md5sum}\t{sequence}\n')

#DIVIDING DATA TO SWISSPROT AND HUMDIV
with open('Efin_Swissprot.tsv', mode='w') as sw, open('Efin_Humdiv.tsv', mode='w') as hd:
    hd.write('md5sum\trefAA\tPosition\taltAA\tScore\tPrediction\n')
    sw.write('md5sum\trefAA\tPosition\taltAA\tScore\tPrediction\n')
    for row in csv_reader(EFIN_PATH):
        x = row.split(',')
        if x[1] == 'NA' or x[2] == 'NA':
            continue
        if x[0] == 'protein':
            continue
        try:
            sw.write(f'{id_md5[x[0]]}\t{x[2]}\t{x[1]}\t{x[3]}\t{x[4]}\t{x[5]}\n')
            hd.write(f'{id_md5[x[0]]}\t{x[2]}\t{x[1]}\t{x[3]}\t{x[6]}\t{x[7]}\n')
        except KeyError:
            continue


#MODIFYING SCORES TO JSON FORMAT
PATH_SWISSPROT = "Efin_Swissprot.tsv"
PATH_HUMDIV = "Efin_Humdiv.tsv"


json_data = {}
protein_md5sum = ''
x = ''

with open('EfinSWISSPROT.tsv', mode='w') as f:
    f.write('md5sum\tscores\n')
    for row in csv_reader(PATH_SWISSPROT):
        if row.startswith('md5sum'):
            continue
        vals = row.split('\t')
        if protein_md5sum != '' and protein_md5sum != vals[0]:
            f.write(f'{protein_md5sum}\t{json.dumps(json_data)}\n')
            json_data = {}
        if x == f'{vals[0]},{vals[2]}':
            json_data[vals[2]][vals[3]] = float(vals[4])
        elif x == '' or x != f'{vals[0]},{vals[2]}':
            json_data[vals[2]] = {"ref": vals[1]}
            json_data[vals[2]][vals[3]] = float(vals[4])
        x = f'{vals[0]},{vals[2]}'
        protein_md5sum = vals[0]
    f.write(f'{protein_md5sum}\t{json.dumps(json_data)}\n')

with open('EfinHUMDIV.tsv', mode='w') as f:
    f.write('md5sum\tscores\n')
    for row in csv_reader(PATH_HUMDIV):
        if row.startswith('md5sum'):
            continue
        vals = row.split('\t')
        if protein_md5sum != '' and protein_md5sum != vals[0]:
            f.write(f'{protein_md5sum}\t{json.dumps(json_data)}\n')
            json_data = {}
        if x == f'{vals[0]},{vals[2]}':
            json_data[vals[2]][vals[3]] = float(vals[4])
        elif x == '' or x != f'{vals[0]},{vals[2]}':
            json_data[vals[2]] = {"ref": vals[1]}
            json_data[vals[2]][vals[3]] = float(vals[4])
        x = f'{vals[0]},{vals[2]}'
        protein_md5sum = vals[0]
    f.write(f'{protein_md5sum}\t{json.dumps(json_data)}\n')
