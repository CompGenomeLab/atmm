import re
import hashlib
import json
import argparse


parser = argparse.ArgumentParser(description='Formats the output file of run_weka.sh algorithm of polyphen.')
parser.add_argument('--pphoutput', '-pph', type=str, help='the output of run_weka.sh algorithm', required=True)
parser.add_argument('--type', '-t', type=str, help='type of the analysis: please type hd for humdiv, hv for hum var', required=True)
parser.add_argument('--output', '-o', type=str, help='path where the new files will be created. ex: /home/username/', required=True)
parser.add_argument('--proteinfasta', '-rp', type=str, help='the reference proteome fasta file', required=True)
args = parser.parse_args()


def hash_seq(s):
    result = hashlib.md5(s.encode())
    return result.hexdigest()


def csv_reader(file_name):
    for row in open(file_name, "r"):
        yield row.split('\n')[0]


if not args.output.endswith('/'):
    path = args.output + '/'
else:
    path = args.output


with open(args.proteinfasta) as kk:
    fasta = kk.read().splitlines()


id_md5 = {}
for j in range(len(fasta)):
    if fasta[j].startswith('>'):
        id_md5[fasta[j][1:]] = hash_seq(fasta[j + 1])


ids = []
json_data = {}
protein_md5sum = ''
x = ''

with open(f'{path}Polyphen{args.type}.tsv', mode='w') as pph:
    pph.write('md5sum\tsequence\n')
    for row in csv_reader(args.pphoutput):
        content = re.sub("\s\s+", " ", row).split()
        if content[0].startswith('#'):
            continue
        if 'deleterious' in content:
            score = float(content[content.index('deleterious') + 1])
        elif 'neutral' in content:
            score = float(content[content.index('neutral') + 1])
        else:
            score = 'NaN'
        if protein_md5sum != '' and protein_md5sum != id_md5[content[0]]:
            pph.write(f'{protein_md5sum}\t{json.dumps(json_data)}\n')
            json_data = {}
        if x == f'{id_md5[content[0]]},{content[1]}':
            json_data[content[1]][content[3]] = score
        elif x == '' or x != f'{id_md5[content[0]]},{content[1]}':
            json_data[content[1]] = {"ref": content[2]}
            json_data[content[1]][content[3]] = score
        x = f'{id_md5[content[0]]},{content[1]}'
        protein_md5sum = id_md5[content[0]]
    pph.write(f'{protein_md5sum}\t{json.dumps(json_data)}\n')
