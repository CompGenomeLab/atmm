import json
import os
import argparse
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
            file_name = "checked_" + file.split("/")[-1]
            with open(os.path.join(self.input_dir, file), "r") as input_file, open(
                    os.path.join(self.output_dir, file_name),"w") as out_file:
                for line in input_file:
                    ensembl_protein_id, score = line.split("\t")
                    score = score.replace("'", "\"")
                    score_json = json.loads(score)
                    if ensembl_protein_id not in self.fasta_dict:
                        continue
                    protein_entry = ProteinScore(ensembl_protein_id, self.fasta_dict[ensembl_protein_id], score_json)
                    if protein_entry.valid:
                        out_file.write(f"{protein_entry.sequence}\t{json.dumps(protein_entry.score_json)}\n")
            os.remove(os.path.join(self.input_dir, file))

    @staticmethod
    def get_protein_seq_for_ensembl_protein_id(ensembl_protein_id):
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
        all_empty = all(not bool(scores) for scores in self.score_json['scores'].values())
        return not all_empty


def main():
    parser = argparse.ArgumentParser(description="Check Score JSON Files")
    parser.add_argument("-i", "--input-dir", required=True, help="Input directory containing JSON files")
    parser.add_argument("-o", "--output-dir", required=True, help="Output directory to save checked files")
    parser.add_argument("-e", "--ensembl-protein-fasta", required=True, help="Ensembl protein FASTA file")

    args = parser.parse_args()

    check_score_json = CheckScoreJsonFile(args.input_dir, args.output_dir, args.ensembl_protein_fasta)
    check_score_json.check_each_file_write_new()


if __name__ == "__main__":
    main()
