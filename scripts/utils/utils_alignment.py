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

# def do_alignment(ref_mh_class, is_include_pre_mh, post_microhap_output_dir):
#     children_microtype_dict:Dict[str, CompreMicrotypeClass] = {} #including dna and protein
#     #pdb.set_trace()
#     if is_include_pre_mh:
#         #pdb.set_trace()
#         mh_seq_df = ref_mh_class.get_mar_microhap_df().copy()#mh lookup table
#         #print_time(f"{mh_seq_df}")
#         if len(mh_seq_df) == 0:
#             return children_microtype_dict
#         mar = ref_mh_class.get_locus()
#         #print(f'{mar} ref_mh_class.get_ref_microtype_dict() len is {len(ref_mh_class.get_ref_microtype_dict())}')
#         if not ref_mh_class.get_has_splicer():
#             #print(f'{mar} does not have ref_mh_class.get_has_splicer()')
#             splicer = "splicer_0"
#             ref_microtype_dict = ref_mh_class.get_ref_microtype_dict()
#             #print(f"Available splicers: {list(ref_microtype_dict.keys())}")
#             splicer_obj = ref_microtype_dict.get(splicer)
#             if splicer_obj is None:
#                 #print(f"Splicer {splicer} not found in ref_microtype_dict for {mar}, skipping alignment.")
#                 return children_microtype_dict
#             ref_splicer0_mt_seq = copy.deepcopy(splicer_obj.get_ref_dna_seq())
#             tmp_compre_mt = CompreMicrotypeClass()
#             tmp_compre_mt.set_mar(mar)
#             tmp_compre_mt.set_splicer(splicer)
#             tmp_compre_mt.set_dna_mh_df(mh_seq_df)
#             tmp_compre_mt.set_target_dna_snp_pos_list(ref_mh_class.get_snppos())
#             tmp_compre_mt.set_ref_dna_seq(ref_mh_class.get_dna_ref())
#             tot_snp_pos_set = set()
#             seq_records = []
#             for _, row in mh_seq_df.iterrows():
#                 _, label, seq, idx = row
#                 tmp_compre_var = CompreVariationClass()
#                 id = f'{mar}_{label}'
#                 tmp_compre_var.set_id(id)
#                 tmp_compre_var.set_mar(mar)
#                 tmp_compre_var.set_splicer(splicer)
#                 tmp_compre_var.set_mt(label)
#                 tmp_compre_var.set_seq(seq)
#                 tmp_compre_var.set_index(idx)
#                 #print(f"Before do_pairwise_alignment for {id}")
#                 indels_pos, mismatches_pos, snp_str = do_pairwise_alignment(ref_splicer0_mt_seq, seq)
#                 #print(f"After do_pairwise_alignment for {id}")
#                 tmp_compre_var.set_indel_pos_list(indels_pos)
#                 tmp_compre_var.set_snp_pos_list(mismatches_pos)
#                 tmp_compre_var.set_snp_str(snp_str)
#                 tmp_compre_mt.get_dna_mh_dict()[label]=tmp_compre_var
#                 if len(indels_pos) == 0:
#                     tot_snp_pos_set.update(mismatches_pos)
#                 seq_records.append(SeqRecord(Seq(seq), id=id))
#             tmp_compre_mt.set_tot_dna_snp_pos_list(sorted(tot_snp_pos_set))
#             tmp_compre_mt.generate_base_freq_df()
#             tmp_compre_mt.set_dna_tre(do_mafft_align(f'{mar}_{splicer}', seq_records, post_microhap_output_dir))
#             children_microtype_dict[splicer] = tmp_compre_mt
#         else:
#             #splicer for the whole length alignment only for dna alingment, aa should be the following ones splicer_0
#             splicer = "splicer"
#             ref_splicer_mt_seq = copy.deepcopy(ref_mh_class.get_dna_ref())#CompreMicrotypeClass
#             tmp_compre_mt = CompreMicrotypeClass()
#             tmp_compre_mt.set_mar(mar)
#             tmp_compre_mt.set_splicer(splicer)
#             tmp_compre_mt.set_dna_mh_df(mh_seq_df)
#             tmp_compre_mt.set_target_dna_snp_pos_list(ref_mh_class.get_snppos())
#             tmp_compre_mt.set_ref_dna_seq(ref_mh_class.get_dna_ref())
#             tot_snp_pos_set = set()
#             seq_records = []
#             for _, row in mh_seq_df.iterrows():
#                 _, label, seq, idx = row
#                 tmp_compre_var = CompreVariationClass()
#                 id = f'{mar}_{label}'
#                 tmp_compre_var.set_id(id)
#                 tmp_compre_var.set_mar(mar)
#                 tmp_compre_var.set_splicer(splicer)
#                 tmp_compre_var.set_mt(label)
#                 tmp_compre_var.set_seq(seq)
#                 tmp_compre_var.set_index(idx)
#                 indels_pos, mismatches_pos, snp_str = do_pairwise_alignment(ref_splicer_mt_seq, seq)
#                 tmp_compre_var.set_indel_pos_list(indels_pos)
#                 tmp_compre_var.set_snp_pos_list(mismatches_pos)
#                 tmp_compre_var.set_snp_str(snp_str)
#                 tmp_compre_mt.get_dna_mh_dict()[label]=tmp_compre_var
#                 if len(indels_pos) == 0:
#                     tot_snp_pos_set.update(mismatches_pos)
#                 seq_records.append(SeqRecord(Seq(seq), id=id))
#             tmp_compre_mt.set_tot_dna_snp_pos_list(sorted(tot_snp_pos_set))
#             tmp_compre_mt.generate_base_freq_df()
#             tmp_compre_mt.set_dna_tre(do_mafft_align(f'{mar}_{splicer}', seq_records, post_microhap_output_dir))
#             children_microtype_dict[splicer] = tmp_compre_mt

#             #print(f'{mar} has ref_mh_class.get_has_splicer()')
#             if len(ref_mh_class.get_ref_microtype_dict()) == 0:
#                 return children_microtype_dict
#             for idx, (splicer, mt_it) in enumerate(ref_mh_class.get_ref_microtype_dict().items()):
#                 #print(f'processing {mar}_{splicer}')
#                 ref_splicer_mt = copy.deepcopy(mt_it)#CompreMicrotypeClass
#                 tmp_compre_mt = CompreMicrotypeClass()
#                 tmp_compre_mt.set_mar(mar)
#                 tmp_compre_mt.set_splicer(splicer)
#                 tmp_compre_mt.set_target_dna_snp_pos_list(ref_splicer_mt.get_target_dna_snp_pos_list())
#                 tmp_compre_mt.set_target_aa_snp_pos_list(ref_splicer_mt.get_target_aa_snp_pos_list())
#                 dna_ref = ref_splicer_mt.get_ref_dna_seq()
#                 aa_ref = ref_splicer_mt.get_ref_aa_seq()
#                 tmp_compre_mt.set_ref_dna_seq(dna_ref)
#                 tmp_compre_mt.set_ref_aa_seq(aa_ref)
#                 mh_df = pd.DataFrame(columns=['mar', 'label', 'seq'])
#                 mp_df = pd.DataFrame(columns=['mar', 'label', 'seq'])
#                 dna_tot_snp_pos_set = set()
#                 aa_tot_snp_pos_set = set()
#                 dna_seq_records = []
#                 aa_seq_records = []
#                 tmp_compre_mt.set_splicer_pos_list(ref_splicer_mt.get_splicer_pos_list())
#                 tmp_compre_mt.set_splicer_aa_pos_list(ref_splicer_mt.get_splicer_aa_pos_list())
#                 for _, row in mh_seq_df.iterrows():#mh lookup table
#                     mar2, label, seq, index = row
#                     dna_seq, aa_seq = trans_single_dna(seq, ref_splicer_mt.get_splicer_pos_list())
#                     mh_df.loc[len(mh_df)] = [mar2,label,dna_seq]
#                     mp_df.loc[len(mp_df)] = [mar2,label,aa_seq]
#                     dna_tmp_compre_var = CompreVariationClass()
#                     id = f'{mar}_{splicer}_{label}'
#                     dna_tmp_compre_var.set_id(id)
#                     dna_tmp_compre_var.set_mar(mar)
#                     dna_tmp_compre_var.set_splicer(splicer)
#                     dna_tmp_compre_var.set_mt(label)
#                     dna_tmp_compre_var.set_seq(dna_seq)

#                     dna_indels_pos, dna_mismatches_pos, dna_snp_str = do_pairwise_alignment(dna_ref, dna_seq)
#                     dna_tmp_compre_var.set_indel_pos_list(dna_indels_pos)
#                         #ori_pos_list = ref_splicer_mt.convert_pos_cur_2_ori(dna_mismatches_pos)
#                     dna_tmp_compre_var.set_snp_pos_list(dna_mismatches_pos)
#                     dna_tmp_compre_var.set_snp_str(dna_snp_str)
#                     tmp_compre_mt.get_dna_mh_dict()[label]=dna_tmp_compre_var
#                     if len(dna_indels_pos) == 0:
#                         dna_tot_snp_pos_set.update(dna_mismatches_pos)
#                     dna_seq_records.append(SeqRecord(Seq(dna_seq), id=id))

#                     aa_tmp_compre_var = CompreVariationClass()
#                     id = f'{mar}_{splicer}_{label.replace("mh_", "mp_", 1)}'
#                     aa_tmp_compre_var.set_id(id)
#                     aa_tmp_compre_var.set_mar(mar)
#                     aa_tmp_compre_var.set_splicer(splicer)
#                     aa_tmp_compre_var.set_mt(label)
#                     aa_tmp_compre_var.set_seq(aa_seq)

#                     aa_indels_pos, aa_mismatches_pos, aa_snp_str = do_pairwise_alignment(aa_ref, aa_seq)
#                     aa_tmp_compre_var.set_indel_pos_list(aa_indels_pos)
#                     aa_tmp_compre_var.set_snp_pos_list(aa_mismatches_pos)
#                     aa_tmp_compre_var.set_snp_str(aa_snp_str)
#                     tmp_compre_mt.get_aa_mp_dict()[label]=aa_tmp_compre_var
#                     if len(aa_indels_pos) == 0:
#                         aa_tot_snp_pos_set.update(aa_mismatches_pos)
#                     aa_seq_records.append(SeqRecord(Seq(aa_seq), id=id))
#                 #tot_ori_pos_list = ref_splicer_mt.convert_pos_cur_2_ori(sorted(dna_tot_snp_pos_set))
#                 tmp_compre_mt.set_tot_dna_snp_pos_list(sorted(dna_tot_snp_pos_set))
#                 tmp_compre_mt.set_tot_aa_snp_pos_list(sorted(aa_tot_snp_pos_set))
#                 tmp_compre_mt.set_dna_mh_df(mh_df)
#                 tmp_compre_mt.set_aa_mh_df(mp_df)
#                 tmp_compre_mt.generate_base_freq_df()
#                 tmp_compre_mt.generate_base_freq_df(False)
#                 if idx == 0 or ref_mh_class.is_overlapped_gene():
#                     tmp_compre_mt.set_aa_tre(do_mafft_align(f'{mar}_{splicer}', aa_seq_records, post_microhap_output_dir))
#                 #tmp_compre_mt.set_dna_tre(self.do_mafft_align(f'{mar}_{splicer}', dna_seq_records))
#                 children_microtype_dict[splicer] = tmp_compre_mt
#     return children_microtype_dict

def do_alignment2(ref_mh_class, is_include_pre_mh, post_microhap_output_dir):
    children_microtype_dict:Dict[str, ComboMicroType] = {} #including dna and protein
    #pdb.set_trace()
    if is_include_pre_mh:
        #pdb.set_trace()
        mh_seq_df = ref_mh_class.get_mar_microhap_df()#mh lookup table
        #print_time(f"{mh_seq_df}")
        if len(mh_seq_df) == 0:
            return children_microtype_dict
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
        cur_snp_pos_tot_set = sorted(cur_snp_pos_tot_set)
        cur_aa_pos_tot_set = sorted(cur_aa_pos_tot_set)
    return children_microtype_dict, list(cur_snp_pos_tot_set), list(cur_aa_pos_tot_set), dna_tree, aa_tree