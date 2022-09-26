from xml.etree.ElementTree import iterparse
import hashlib
import argparse
import os


def csv_reader(file_name):
    for row in open(file_name, "r"):
        yield row.split('\n')[0]


def hash_seq(s):
    result = hashlib.md5(s.encode())
    return result.hexdigest()


parser = argparse.ArgumentParser(description='Creates md5sum-sequence table for input and separate fasta files to sift_input folder for sift4g')
parser.add_argument('--path', '-p', type=str, help='xml file path ex: /home/username/uniref100.xml', required=True)
parser.add_argument('--outputpath', '-op', type=str, help='path where the new file and folder will be created, ex: /home/username/', required=True)
args = parser.parse_args()

if not args.outputpath.endswith('/'):
    path = args.outputpath + '/'
else:
    path = args.outputpath


# GET ALL THE DATA
with open(f'{path}uniref100.tsv', mode='w') as f:
    for event, elem in iterparse(open(args.path, 'rb')):
        if 'type' in elem.attrib.keys() and elem.attrib['type'] == 'UniProtKB accession':
            f.write(f'{elem.attrib["value"]}|')
        if 'type' in elem.attrib.keys() and elem.attrib['type'] == 'NCBI taxonomy':
            f.write(f'\t{elem.attrib["value"]}\t')
        if elem.tag == '{http://uniprot.org/uniref}sequence':
            sequence = elem.text.replace("\n", "").replace("  ", "")
            f.write(f'{sequence}\t')
        if elem.tag == '{http://uniprot.org/uniref}entry':
            f.write(f'{elem.attrib["updated"]}\n')
        elem.clear()

# MD5SUM-SEQUENCE TABLE CREATED
# INPUT FASTA FILES CREATED FOR SIFT4G
with open(f'{path}md5sum_seq_uniref100.tsv', mode='w') as f:
    f.write('md5sum\tsequence\n')
    for row in csv_reader(f'{path}uniref100.tsv'):
        x = row.split('\t')
        if x[1] == '9606':
            ids = [i for i in x[0].split('|') if i != '']
            if ids:
                if ids[0]:
                    with open(f'{path}sift_input/{ids[0]}.fasta', mode='w') as z:
                        z.write('>' + ids[0] + '\n' + x[2] + '\n')
                        f.write(f'{hash_seq(x[2])}\t{x[2]}\n')

			
file_path = f'{path}uniref100.tsv'
if os.path.isfile(file_path):
    os.remove(file_path)
