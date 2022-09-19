from xml.etree.ElementTree import iterparse
import hashlib


def csv_reader(file_name):
    for row in open(file_name, "r"):
        yield row.split('\n')[0]
        
def hash_seq(s):
    result = hashlib.md5(s.encode())
    return result.hexdigest()

#GET ALL THE DATA
with open('uniref100_curr.tsv', mode='w') as f:
    for event, elem in iterparse(open("uniref100.xml", 'rb')):
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
  
  
#MD5SUM-SEQUENCE TABLE CREATED
#INPUT FASTA FILES CREATED FOR SIFT4G
with open('md5sum_seq_uniref100.tsv', mode='w') as f:
    f.write('md5sum\tsequence\n')
		for row in csv_reader('uniref100_curr.tsv'):
        x = row.split('\t')
        if x[1] == '9606':
						ids = [i for i in x[0].split('|') if i != '']
						if ids:
                if ids[0]:
                    with open(f'/sift4g/input/{ids[0]}.fasta', mode='w') as z:
                        z.write('>' + ids[0] + '\n' + x[2] + '\n')
										f.write(f'{hash_seq(x[2])}\t{x[2]}\n')
                    

                    
                    
                    
