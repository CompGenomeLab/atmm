import json
import os
import hashlib
import argparse


def hash_seq(s):
    result = hashlib.md5(s.encode())
    return result.hexdigest()


parser = argparse.ArgumentParser(description='Format sift4g output files, this code gives sift4g result file that is tsv format and md5sum-sequence file for the primary key table')
parser.add_argument('--outputpath', '-op', type=str, help='path to output files of sift4g algorithm. ex: /home/username/sift4g/output/ (it should finish with backslash)', required=True)
parser.add_argument('--path', '-p', type=str, help='path where the new files will be created. ex: /home/username/sift4g/ (it should finish with backslash)', required=True)
parser.add_argument('--inputpath', '-ip', type=str, help='path of the folder in which input files are present at. They can be created with ./Current_uniref100_Parse.py ex: /home/username/sift4g/input/ (it should finish with backslash)', required=True)
parser.add_argument('--databasetype', '-db', type=str, help='database that is used for the algorithm. swissprot or swissprot_trembl', required=True)
args = parser.parse_args()


aa_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'X', 'Y',
           'Z', '*', '-']

dir_path = args.outputpath
files = []

for path in os.listdir(dir_path):
    if os.path.isfile(os.path.join(dir_path, path)):
        files.append(path)


with open(f'{args.path}sift4gDATA_{args.databasetype}.tsv', mode='w') as k, open(f'{args.path}seq_md5sum_sift4g_{args.databasetype}.tsv', mode='w') as seqmd:
    k.write('md5sum\tscore\n')
    seqmd.write('md5sum\tsequence\n')
    for f in files:
        with open(dir_path + f) as m:
            score = m.read().splitlines()
        with open(f'{args.inputpath}{f[:-14]}fasta') as s:
            fasta_file = s.read().splitlines()
        sequence = ''
        for el in fasta_file:
            if not el.startswith('>'):
                sequence += el

        json_data = {}
        m = 1
        for i in score:
            if not i.startswith('  A') and i.startswith(' '):
                if '-nan' not in i:
                    sc_list = i.replace('  ', ' ')[1:].split(' ')
                    aa = sequence[m - 1]
                    json_data[m] = {"ref": aa}
                    for j in aa_list:
                        if j not in ['B', 'X', 'Z', '*', '-']:
                            json_data[m][j] = float(sc_list[aa_list.index(j)])

                else:
                    aa = 20
                    json_data[m] = {"ref": aa_list[aa]}
                    for j in aa_list:
                        if j not in ['B', 'X', 'Z', '*', '-']:
                            json_data[m][j] = 'NaN'

                m += 1

        k.write(f'{hash_seq(sequence)}\t{json.dumps(json_data)}\n')
        seqmd.write(f'{hash_seq(sequence)}\t{sequence}\n')
        
