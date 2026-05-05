import os
from io import StringIO
from Bio import Align
from Bio import Phylo
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio import SeqIO, AlignIO
from Bio.Phylo.TreeConstruction import DistanceTreeConstructor, DistanceCalculator
import subprocess
from scripts.class_modules.microtype_class import ComboMicroType, MicroType
from typing import Dict
import matplotlib.pyplot as plt

def do_pairwise_alignment(target:str, query:str, triml = 0, withtriml = False)->tuple:
        if len(target) == 0 or len(query) == 0:
            return [], [], ""
        aligner=Align.PairwiseAligner()
        aligner.match_score = 1
        aligner.mismatch_score = -1
        aligner.open_gap_score = -5
        aligner.extend_gap_score = -1
        alignments=aligner.align(target, query)
        alignment=alignments[0]
        return(calculate_mismatches_indels(alignment, triml, withtriml))

def calculate_mismatches_indels(alignment,  triml = 0, withtriml = False)->tuple:
        aligned_target, aligned_query = alignment
        indels_pos=set()
        mismatches_pos=set()
        snp_str=""
        snp_str_withtriml = ""
        for i, (base1, base2) in enumerate(zip(str(aligned_target), str(aligned_query))):
            if base1 != base2:
                if base1 == '-' or base2 == '-':
                    indels_pos.add(i)
                else:
                    mismatches_pos.add(i)
                    if withtriml:
                        snp_str_withtriml += f"{i+triml}({base2}|{base1})"
                    else:
                        snp_str += f"{i}({base2}|{base1})"
        if len(indels_pos) == 0:
            return sorted(indels_pos), sorted(mismatches_pos), (snp_str_withtriml if withtriml else snp_str)
        else:
            return sorted(indels_pos), [], ""

def remove_inner_labels(tree):
    for clade in tree.find_clades():
        # If the clade has children, it's an internal node
        if clade.is_terminal() == False:
            clade.name = None  # Clear the inner label
        #iterate through children_microtype and get the snp pos in each splicer
        
def do_mafft_align(id, seq_records, fpath):
    # print(f'Starting MAFFT alignment for {id}')
    if not seq_records:
        return
    # Ensure the tmp directory exists
    tmp_dir = os.path.join(fpath, "align")
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    # File paths for temporary files
    fa_file = os.path.join(tmp_dir, f'{id}_mt.fasta')
    align_file = os.path.join(tmp_dir, f'{id}_align.fasta')
    tree_file = os.path.join(tmp_dir, f'{id}_tree.nwk')
    try:
        # Write input sequences to the temporary FASTA file
        with open(fa_file, "w") as output_file:
            SeqIO.write(seq_records, output_file, "fasta")

        # Run MAFFT alignment
        mafft_cline = ["mafft", fa_file]
        result = subprocess.run(mafft_cline, capture_output=True, text=True)
        stdout = result.stdout
        with open(align_file, "w") as output_file:
            output_file.write(stdout)
        alignment = AlignIO.read(StringIO(stdout), "fasta")

        # Calculate the distance matrix
        calculator = DistanceCalculator('identity')  # or 'euclidean' or another distance metric
        distance_matrix = calculator.get_distance(alignment)

        # Construct a phylogenetic tree using the NJ method
        constructor = DistanceTreeConstructor()
        tree = constructor.nj(distance_matrix)
        remove_inner_labels(tree)
        Phylo.write(tree, tree_file, "newick")
        #print(f'Finished MAFFT alignment for {id}')
        return tree
    except Exception as e:
        print(f"Error during MAFFT alignment for {id}: {e}")
        raise

def do_alignment2(ref_mh_class, is_include_pre_mh, post_microhap_output_dir):
    children_microtype_dict:Dict[str, ComboMicroType] = {} #including dna and protein
    cur_snp_pos_tot_set = set()
    cur_aa_pos_tot_set = set()
    dna_tree = None
    aa_tree = None
    #pdb.set_trace()
    if is_include_pre_mh:
        #pdb.set_trace()
        mh_seq_df = ref_mh_class.get_mar_microhap_df()#mh lookup table
        #print_time(f"{mh_seq_df}")
        if len(mh_seq_df) == 0:
            return children_microtype_dict, [], [], dna_tree, aa_tree
        mar = ref_mh_class.get_locus()
        cur_dna_ref = ref_mh_class.get_cur_dna_ref()
        cur_aa_ref = ref_mh_class.get_cur_aa_ref() if ref_mh_class.get_has_exon() else None
        
        #print(f'{mar} ref_mh_class.get_ref_microtype_dict() len is {len(ref_mh_class.get_ref_microtype_dict())}')
        cur_snp_pos_tot_set = set(ref_mh_class.get_tot_snp_pos())
        cur_aa_pos_tot_set = set(ref_mh_class.get_tot_sap_pos())
        cur_dna_seq_records = []
        cur_aa_seq_map = {}
        for _, row in mh_seq_df.iterrows():
            locus, mh_label, mh_seq, mh_id, mp_label, mp_seq, mp_id = row
            tmp_mt = ComboMicroType()
            tmp_mt.set_mar(locus)
            
            tmp_mh = MicroType()
            tmp_mh.set_mar(locus)
            tmp_mh.set_mt(mh_label)
            tmp_mh.set_seq(mh_seq)
            
            cur_dna_seq_records.append(SeqRecord(Seq(mh_seq), id = mh_label))
            dna_indels_pos, dna_mismatches_pos, snp_str = do_pairwise_alignment(cur_dna_ref, mh_seq, ref_mh_class.get_triml(), True)
            if len(dna_indels_pos) == 0:
                tmp_mh.set_var_pos_list(dna_mismatches_pos)
                cur_snp_pos_tot_set.update(dna_mismatches_pos)
                tmp_mh.set_var_nm_str(snp_str)
            else:
                tmp_mh.set_is_indel(True)
            tmp_mt.set_microhap(tmp_mh)
            if ref_mh_class.get_has_exon():
                tmp_mt.set_has_mp(True)
                tmp_mp = MicroType()
                tmp_mp.set_mar(locus)
                tmp_mp.set_mt(mp_label)
                if cur_aa_ref is not None and len(cur_aa_ref) and mp_seq is not None and len(mp_seq) > 0:
                    cur_aa_seq_map[mp_seq] = mp_label
                    #cur_aa_seq_records.add(SeqRecord(Seq(mp_seq), id = mp_label))
                    tmp_mp.set_seq(mp_seq)
                    aa_indels_pos, aa_mismatches_pos, sap_str = do_pairwise_alignment(cur_aa_ref, mp_seq)
                    if len(aa_indels_pos) == 0:
                        tmp_mp.set_var_pos_list(aa_mismatches_pos)
                        cur_aa_pos_tot_set.update(aa_mismatches_pos)
                        tmp_mp.set_var_nm_str(sap_str)
                    else:
                        tmp_mp.set_is_indel(True)
                tmp_mt.set_micropep(tmp_mp)
            children_microtype_dict[mh_seq] = tmp_mt
        dna_tree = do_mafft_align(f'{mar}_dna', cur_dna_seq_records, post_microhap_output_dir)
        aa_tree = None
        if len(cur_aa_seq_map) > 0:
            aa_tree = do_mafft_align(f'{mar}_aa', [SeqRecord(Seq(seq), id=label) for seq, label in cur_aa_seq_map.items()], post_microhap_output_dir)
        output_phlylo_tree(dna_tree, aa_tree, post_microhap_output_dir, mar)
        cur_snp_pos_tot_set = sorted(cur_snp_pos_tot_set)
        cur_aa_pos_tot_set = sorted(cur_aa_pos_tot_set)
    return children_microtype_dict, list(cur_snp_pos_tot_set), list(cur_aa_pos_tot_set), dna_tree, aa_tree

def output_phlylo_tree(dna_tree, aa_tree, output_dir, mar):
    if dna_tree is None and aa_tree is None:
        return
    if dna_tree is not None and aa_tree is not None:
        fig, (ax1, ax2)=plt.subplots(1, 2, figsize=(20, 10), dpi = 600)
        Phylo.draw(dna_tree, do_show=False, axes = ax1)
        ax1.set_title("DNA tree")
        ax1.set_ylabel("microtype")
        Phylo.draw(aa_tree, do_show=False, axes = ax2)
        ax2.set_title("AA tree")
        ax2.set_ylabel("microtype")
        fig.suptitle(f"Phylogenetic Trees of {mar}", fontsize=16)
    elif dna_tree is not None:
        fig, ax1=plt.subplots(1,figsize=(15, 10), dpi = 600)
        Phylo.draw(dna_tree, do_show=False, axes = ax1)
        ax1.set_title("DNA tree")
        ax1.set_ylabel("microtype")
        fig.suptitle(f"Phylogenetic Tree {mar}", fontsize=16)
    elif aa_tree is not None:
        fig, ax1=plt.subplots(1,figsize=(15, 10), dpi = 600)
        Phylo.draw(aa_tree, do_show=False, axes = ax1)
        ax1.set_title("AA tree")
        ax1.set_ylabel("microtype")
        fig.suptitle(f"Phylogenetic Tree {mar}", fontsize=16)
    fig.subplots_adjust(left=0.15, right=0.95, top=0.9, bottom=0.1)
    fig.savefig(os.path.join(output_dir, "align", f"{mar}_mt_phylo_tree.pdf"), dpi=600, bbox_inches="tight")
    plt.close(fig)