import csv
import os
import tempfile
import shutil

class ParseDBSNFP:
    columns = ['aaref', 'aaalt', 'aapos', 'Ensembl_proteinid', 'SIFT_score', 'SIFT4G_score', 'Polyphen2_HDIV_score',
               'Polyphen2_HVAR_score', 'LRT_score', 'MutationTaster_score', 'MutationAssessor_score', 'FATHMM_score',
               'PROVEAN_score', 'VEST4_score', 'MetaSVM_score', 'MetaLR_score', 'MetaRNN_score', 'M-CAP_score',
               'REVEL_score', 'MutPred_score', 'MVP_score', 'MPC_score', 'PrimateAI_score', 'DEOGEN2_score',
               'BayesDel_addAF_score', 'BayesDel_noAF_score', 'ClinPred_score', 'LIST-S2_score', 'CADD_raw',
               'CADD_raw_hg19', 'DANN_score', 'fathmm-MKL_coding_score', 'fathmm-XF_coding_score', 'Eigen-raw_coding',
               'GenoCanyon_score', 'LINSIGHT']

    def __init__(self, workdir: str, dbsnfp_file_path: str):

        self.workdir = workdir
        self.dbsnfp_file_path = dbsnfp_file_path
        self.tempdir = tempfile.mkdtemp(dir=workdir)

    def process(self):
        for index, title in enumerate(self.columns[4:]):
            if title == "MutationTaster_score":
                continue
            else:
                self.process_raw_file(index, title)
        file_paths = [os.path.join(self.tempdir, f) for f in os.listdir(self.tempdir) if f.endswith('.tsv')]
        for tsv_file in file_paths:
            self.process_tsv_lines(tsv_file)
        files_to_jsons = [os.path.join(self.tempdir, f) for f in os.listdir(self.tempdir) if f.startswith('processed_')]
        for to_json_file in files_to_jsons:
            self.process_json_files(to_json_file)
        shutil.rmtree(self.tempdir)
    def process_raw_file(self, index, title):
        with open(self.dbsnfp_file_path, 'r') as dbsnfp:
            tsvreader = csv.reader(dbsnfp, delimiter='\t')
            with open(os.path.join(self.tempdir, f"{title}.tsv"), 'w') as new_file:
                for line in tsvreader:
                    if line[0] == '.' or line[1] == '.':
                        continue
                    else:
                        new_file.write(f"{line[0]}\t{line[1]}\t{line[2]}\t{line[3]}\t{line[index + 4]}\n")
            dbsnfp.seek(0)

    def process_tsv_lines(self, file_path):
        new_file_path = os.path.join(self.tempdir, f"processed_{os.path.basename(file_path)}")
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
            print(file_path)
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

        with open(os.path.join(self.workdir, file.split('/')[-1].split('.')[0] + '.json'), 'w') as f:
            for key in data.keys():
                f.write(f"{key}\t{data[key]}\n")
