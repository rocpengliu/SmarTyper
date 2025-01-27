from Bio import Align
from Bio.Seq import Seq

def do_pairwise_alignment(target:str, query:str)->tuple:
        aligner=Align.PairwiseAligner()
        aligner.match_score = 1
        aligner.mismatch_score = -1
        aligner.open_gap_score = -5
        aligner.extend_gap_score = -1
        alignments=aligner.align(target, query)
        alignment=alignments[0]
        return(calculate_mismatches_indels(alignment))
def calculate_mismatches_indels(alignment)->tuple:
        aligned_target, aligned_query = alignment
        indels_pos=set()
        mismatches_pos=set()
        snp_str=""
        for i, (base1, base2) in enumerate(zip(str(aligned_target), str(aligned_query))):
            if base1 != base2:
                if base1 == '-' or base2 == '-':
                    indels_pos.add(i)
                else:
                    mismatches_pos.add(i)
                    snp_str += f"{i}({base2}|{base1})"
        if len(indels_pos) == 0:
            return sorted(indels_pos), sorted(mismatches_pos), snp_str
        else:
            return sorted(indels_pos), [], ""