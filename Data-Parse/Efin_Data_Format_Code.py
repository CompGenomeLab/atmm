import hashlib
import json
import argparse


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


parser = argparse.ArgumentParser(description='Format Efin csv file, output gives 3 files namely: seq_md5sum.tsv, EfinSWISSPROT.tsv, EfinHUMDIV.tsv')
parser.add_argument('--path', '-p', type=str, help='the csv file path. ex: /home/username/efin.csv', required=True)
parser.add_argument('--outputpath', '-op', type=str, help='path where the new files will be created. ex: /home/username/', required=True)
args = parser.parse_args()

if not args.outputpath.endswith('/'):
    path = args.outputpath + '/'
else:
    path = args.outputpath


indicator = ''
protein_dict = {}
id_md5 = {}

with open(f'{path}seq_md5sum_efin.tsv', mode='w') as sm:
    sm.write('md5sum\tsequence\n')
    for row in csv_reader(args.path):
        x = row.split(',')
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


json_data = {}
protein_md5sum = ''
x = ''

with open(f'{path}EfinSWISSPROT.tsv', mode='w') as f:
    f.write('md5sum\tscores\n')
    for row in csv_reader(args.path):
        vals = row.split(',')
        if vals[1] == 'NA' or vals[2] == 'NA':
            continue
        if vals[0] == 'protein':
            continue
        if vals[0] not in id_md5.keys():
            continue
        if protein_md5sum != '' and protein_md5sum != id_md5[vals[0]]:
            f.write(f'{protein_md5sum}\t{json.dumps(json_data)}\n')
            json_data = {}
        if x == f'{id_md5[vals[0]]},{vals[1]}':
            json_data[vals[1]][vals[3]] = float(vals[4])
        elif x == '' or x != f'{id_md5[vals[0]]},{vals[1]}':
            json_data[vals[1]] = {"ref": vals[2]}
            json_data[vals[1]][vals[3]] = float(vals[4])
        x = f'{id_md5[vals[0]]},{vals[1]}'
        protein_md5sum = id_md5[vals[0]]
    f.write(f'{protein_md5sum}\t{json.dumps(json_data)}\n')


json_data = {}
protein_md5sum = ''
x = ''

with open(f'{path}EfinHUMDIV.tsv', mode='w') as f:
    f.write('md5sum\tscores\n')
    for row in csv_reader(args.path):
        vals = row.split(',')
        if vals[1] == 'NA' or vals[2] == 'NA':
            continue
        if vals[0] == 'protein':
            continue
        if vals[0] not in id_md5.keys():
            continue
        if protein_md5sum != '' and protein_md5sum != id_md5[vals[0]]:
            f.write(f'{protein_md5sum}\t{json.dumps(json_data)}\n')
            json_data = {}
        if x == f'{id_md5[vals[0]]},{vals[1]}':
            json_data[vals[1]][vals[3]] = float(vals[6])
        elif x == '' or x != f'{id_md5[vals[0]]},{vals[1]}':
            json_data[vals[1]] = {"ref": vals[2]}
            json_data[vals[1]][vals[3]] = float(vals[6])
        x = f'{id_md5[vals[0]]},{vals[1]}'
        protein_md5sum = id_md5[vals[0]]
    f.write(f'{protein_md5sum}\t{json.dumps(json_data)}\n')
