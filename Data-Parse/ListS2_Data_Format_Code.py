import hashlib
import json

LISTS2_PATH = "LIST-s2.tsv"


def file_reader(file_name):
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


#CREATING SEQUENCE_MD5SUM FILE FOR PRIMARY KEY TABLE
indicator = ''
protein_dict = {}
id_md5 = {}

with open('seq_md5sum.tsv', mode='w') as sm:
    sm.write('md5sum\tsequence\n')

    for row in file_reader(LISTS2_PATH):
        x = row.split('\t')
        print(x)
        if x[0] == 'UniParc':
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

#MERGING MD5SUM AND SCORES
with open('List-s2.tsv', mode='w') as l:
    l.write('md5sum\trefAA\tPosition\taltAA\tScore\tPrediction\n')
    for row in file_reader(LISTS2_PATH):
        x = row.split('\t')
        if x[0] == 'protein':
            continue
        try:
            l.write(f'{id_md5[x[0]]}\t{x[2]}\t{x[1]}\t{x[3]}\t{x[4]}\n')
        except KeyError:
            continue

#MODIFYING SCORES TO JSON FORMAT
PATH = "List-s2.tsv"

json_data = {}
protein_md5sum = ''
x = ''

with open('LIST-S2_FORMATTED.tsv', mode='w') as f:
    f.write('md5sum\tscores\n')
    for row in file_reader(PATH):
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
