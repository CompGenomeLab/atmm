import json
import os

import hashlib


class CheckScoreJsonFile:

    def __init__(self, input_dir, output_dir, ensembl_protein_fasta):
        self.input_dir = input_dir
        self.files_to_check = [os.path.join(self.input_dir, f) for f in os.listdir(self.input_dir)]
        self.output_dir = output_dir
        self.ensembl_protein_fasta = ensembl_protein_fasta
        self.fasta_dict = self.get_protein_seq_for_ensembl_protein_id(self.ensembl_protein_fasta)

    def check_each_file_write_new(self):
        for file in self.files_to_check:
            file_name = "cheched_" + file.split("/")[-1]
            md5sum_file = "md5sum_" + file.split("/")[-1]
            with open(os.path.join(self.input_dir, file), "r") as input_file, open(
                    os.path.join(self.output_dir, file_name),
                    "w") as out_file, open(
                os.path.join(self.output_dir, md5sum_file), "w") as output_md5sum_file:
                for line in input_file:
                    ensembl_protein_id, score = line.split("\t")
                    score = score.replace("'", "\"")
                    score_json = json.loads(score)
                    if ensembl_protein_id not in self.fasta_dict:
                        continue
                    protein_entry = ProteinScore(ensembl_protein_id, self.fasta_dict[ensembl_protein_id], score_json)
                    if protein_entry.protein_len_in_score_json != len(self.fasta_dict[ensembl_protein_id]):
                        continue
                    if protein_entry.valid:
                        out_file.write(f"{protein_entry.md5sum}\t{protein_entry.score_json}\n")
                        output_md5sum_file.write(
                            f"{protein_entry.md5sum}\t{protein_entry.ensembl_protein_id}\t{protein_entry.sequence}\n")

    def get_protein_seq_for_ensembl_protein_id(self, ensembl_protein_id):
        with open(ensembl_protein_id, 'r') as file:
            content = file.read()

        fasta_dict = {}
        for entry in content.split('>')[1:]:
            lines = entry.strip().split('\n')
            header = lines[0].split(".")[0]
            sequence = ''.join(lines[1:])
            fasta_dict[header] = sequence

        return fasta_dict


class ProteinScore:

    def __init__(self, ensembl_protein_id, sequence, score_json):

        self.ensembl_protein_id = ensembl_protein_id
        self.sequence = sequence
        self.score_json = score_json
        self.md5sum = self.seq_to_md5()
        self.valid = self.check_scores
        self.protein_len_in_score_json = len(self.score_json["scores"].keys())

    def seq_to_md5(self):
        sequence_bytes = self.sequence.encode("utf-8")
        md5sum = hashlib.md5(sequence_bytes).hexdigest()
        return md5sum

    @property
    def check_scores(self):
        all_empty = all(not bool(self.score_json['scores'][key]) for key in self.score_json['scores'])
        if all_empty:
            return True

        for _, sub_dict in self.score_json.items():
            for val in sub_dict.values():
                if not (isinstance(val, (int, float)) or val == ''):
                    return True
        return False
