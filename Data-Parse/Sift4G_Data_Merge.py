import json
import os
import hashlib


def hash_seq(s):
    result = hashlib.md5(s.encode())
    return result.hexdigest()


aa_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'X', 'Y',
           'Z', '*', '-']

dir_path = r'/path/to/output/files/'
files = []

for path in os.listdir(dir_path):
    # check if current path is a file
    if os.path.isfile(os.path.join(dir_path, path)):
        files.append(path)

with open('/sift4gDATA_SP_TREMBL.tsv', mode='w') as k:
    k.write('md5sum\tscore\n')
    for f in files:
        with open(dir_path + f) as m:
            score = m.read().splitlines()
        with open(f'./sift4g/input/{f[:-14]}fasta') as s:
            fasta_file = s.read().splitlines()
        for el in fasta_file:
            if not el.startswith('>'):
                sequence = el

        json_data = {}
        m = 1
        for i in score:
            if not i.startswith('  A') and i.startswith(' '):
                if '-nan' not in i:
                    sc_list = i.replace('  ', ' ')[1:].split(' ')
                    aa = sequence[m-1]
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
