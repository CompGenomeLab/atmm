import csv
import os
import tempfile
import shutil
import argparse
from FileValidation.CheckJsonFileIntenrigty import CheckScoreJsonFile
from concurrent.futures import ProcessPoolExecutor
import json


class ParseDBSNFP:
    columns = ['aaref', 'aaalt', 'aapos', 'Ensembl_proteinid', 'SIFT_score', 'SIFT4G_score', 'Polyphen2_HDIV_score',
               'Polyphen2_HVAR_score', 'LRT_score', 'MutationTaster_score', 'MutationAssessor_score', 'FATHMM_score',
               'PROVEAN_score', 'VEST4_score', 'MetaSVM_score', 'MetaLR_score', 'MetaRNN_score', 'M-CAP_score',
               'REVEL_score', 'MutPred_score', 'MVP_score', 'MPC_score', 'PrimateAI_score', 'DEOGEN2_score',
               'BayesDel_addAF_score', 'BayesDel_noAF_score', 'ClinPred_score', 'LIST-S2_score', 'CADD_raw',
               'CADD_raw_hg19', 'DANN_score', 'fathmm-MKL_coding_score', 'fathmm-XF_coding_score', 'Eigen-raw_coding',
               'GenoCanyon_score', 'LINSIGHT']

    def __init__(self, workdir: str, dbsnfp_file_path: str):
        self.output = tempfile.mkdtemp(dir=workdir)
        self.workdir = workdir
        self.dbsnfp_file_path = dbsnfp_file_path
        self.tempdir = tempfile.mkdtemp(dir=workdir)

    def process(self):
        max_workers = os.cpu_count()
        print("Processing raw files...")
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            tasks = []
            for index, title in enumerate(self.columns[4:]):
                if title == "MutationTaster_score":
                    continue
                else:
                    task = executor.submit(self.process_raw_file, index, title)
                    tasks.append(task)
            for task in tasks:
                task.result()
        file_paths = [os.path.join(self.tempdir, f) for f in os.listdir(self.tempdir) if f.endswith('.tsv')]

        print("Processing TSV lines...")
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            executor.map(self.process_tsv_lines, file_paths)

        files_to_jsons = [os.path.join(self.tempdir, f) for f in os.listdir(self.tempdir) if f.startswith('processed_')]

        print("Processing JSON files...")
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            executor.map(self.process_json_files, files_to_jsons)

    def process_raw_file(self, index, title):
        with open(self.dbsnfp_file_path, 'r') as dbsnfp:
            tsvreader = csv.reader(dbsnfp, delimiter='\t')
            with open(os.path.join(self.tempdir, f"{title}.tsv"), 'w') as new_file:
                print(f"Raw file processing for {title}")
                for line in tsvreader:
                    if line[0] == '.' or line[1] == '.':
                        continue
                    else:
                        try:
                            new_file.write(f"{line[0]}\t{line[1]}\t{line[2]}\t{line[3]}\t{line[index + 4]}\n")
                        except IndexError:
                            print(f"IndexError: index={index}, title={title}, line_length={len(line)}")
                            continue
            dbsnfp.seek(0)

    def process_tsv_lines(self, file_path):
        new_file_path = os.path.join(self.tempdir, f"processed_{os.path.basename(file_path)}")
        print(f"Processing lines in the {os.path.basename(file_path)}")
        with open(file_path, 'r', newline='') as input_file, open(new_file_path, 'w', newline='') as output_file:
            tsv_reader = csv.reader(input_file, delimiter='\t')
            tsv_writer = csv.writer(output_file, delimiter='\t')
            for line in tsv_reader:
                positions = line[2].split(";")
                proteins = line[3].split(";")
                scores = line[4].split(';')
                for i in range(len(positions)):
                    score = scores[i] if len(scores) > 1 else scores[0]
                    tsv_writer.writerow([line[0], line[1], positions[i], proteins[i], score.strip('\n')])

    def process_json_files(self, file_path):
        data = {}
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f, delimiter='\t')
            print(f"Processing json files for {os.path.basename(file_path)}")
            row: dict
            for row in reader:
                protein_id = row['Ensembl_proteinid']
                aa_pos = row['aapos']
                aa_alt = row['aaalt']
                file = os.path.basename(file_path).split('.')[0].split("processed_")[1]
                tool_score = row[file]

                if protein_id not in data:
                    data[protein_id] = {
                        'scores': {}
                    }

                if aa_pos not in data[protein_id]['scores']:
                    data[protein_id]['scores'][aa_pos] = {}

                if tool_score != '.':
                    try:
                        data[protein_id]['scores'][aa_pos][aa_alt] = float(tool_score)
                    except ValueError:
                        data[protein_id]['scores'][aa_pos][aa_alt] = tool_score

                    data[protein_id]['scores'][aa_pos]['ref'] = row['aaref']
                else:
                    continue

        with open(os.path.join(self.output, file.split('/')[-1].split('.')[0] + '.json'), 'w') as f:
            for key, value in data.items():
                json_value = json.dumps(value)  # Converts the dictionary to a JSON string
                f.write(f"{key}\t{json_value}\n")


def main():
    parser = argparse.ArgumentParser(description='Process DBSNFP data and generate JSON files.')
    parser.add_argument('-w', '--workdir', required=True, help='The working directory to store output JSON files.')
    parser.add_argument('-d', '--dbsnfp', required=True, help='The path to the DBSNFP file.')
    parser.add_argument("-e", "--ensembl-protein-fasta", required=True, help="Ensembl protein FASTA file of dbsnfp")
    parser.add_argument("-o", "--output-directory", required=True, help="Output directory of dbsnfp scores")
    args = parser.parse_args()

    print("Creating temporary working directory...")
    temp_workdir = tempfile.mkdtemp(dir=args.workdir)
    dbsnfp_file_path = args.dbsnfp
    output_directory = args.output_directory

    print("Parsing DBSNFP file...")
    parse_dbsnfp = ParseDBSNFP(temp_workdir, dbsnfp_file_path)
    parse_dbsnfp.process()
    parse_dbsnfp_output = parse_dbsnfp.output
    print("Checking and writing new JSON files...")
    check_score_json = CheckScoreJsonFile(parse_dbsnfp_output, output_directory, args.ensembl_protein_fasta)
    check_score_json.check_each_file_write_new()
    print("Cleaning up temporary working directory...")
    shutil.rmtree(temp_workdir)


if __name__ == "__main__":
    main()
