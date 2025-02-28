import os
import pandas as pd
from tkinter import messagebox  # Importing messagebox for error handling
from concurrent.futures import ThreadPoolExecutor, as_completed
from ..utils.utils_common import print_time
import copy
from ..utils.utils_func import trans_single_dna
from ..utils.utils_common import print_time, thread_lock
from ..utils.utils_alignment import do_pairwise_alignment
from .microtype_class import CompreMicrotypeClass, CompreVariationClass
from typing import Dict
import pdb
from io import StringIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio import SeqIO
from Bio.Align.Applications import MafftCommandline
from Bio import AlignIO, Phylo
from Bio.Phylo.TreeConstruction import DistanceTreeConstructor, DistanceCalculator

class PostMicrohapClass:
    def __init__(self) -> None:
        
        self._final_microhap_df = pd.DataFrame() #with allele names change to mh name for the microhap_df
        self._final_microhap_df_simple = pd.DataFrame() #only contain mh name in sample X marker 
        
        self._final_all_microhap_df = pd.DataFrame() #with allele names change to mh name for the microhap_df
        self._final_all_microhap_df_simple = pd.DataFrame() #only contain mh name in sample X marker 
        
        self._mar_microhap_df_simple_dict = {} #{mar:dataframe for all samples simple mh} 
        
        self._pre_mar_microhap_dict = {} #  {mar: df with columns=['locus', 'label', 'seq']} for previous one
        self._cur_mar_microhap_dict = {} # {mar : df with columns=['locus', 'label', 'seq']} for the current one
        
        self._mar_mh_alignment_dict={} #store the mar alignment file, nested {mar:{mh:alignment}}
        self._mar_snp_pos_dict={} # {mar:MicrohapCombo} 
        self._selected_marker=""
        self._working_markers_list=[]
        self._dna_or_aa = ""
        self._loc_ref_dict={} # {mar: RefMicrohaptype}
    
    def get_dna_or_aa(self):
        return self._dna_or_aa
    
    def set_dna_or_aa(self, dna_or_aa):
        self._dna_or_aa = dna_or_aa

    def get_working_markers_list(self):
        return self._working_markers_list
    
    def set_working_markers_list(self, working_markers_list):
        self._working_markers_list = working_markers_list
        
    def get_loc_ref_dict(self):
        return self._loc_ref_dict
    def set_loc_ref_dict(self, loc_ref_dict):
        self._loc_ref_dict = loc_ref_dict
        
    def get_selected_marker(self):
        return self._selected_marker
    
    def set_selected_marker(self, selected_marker):
        self._selected_marker = selected_marker
        
    def get_pre_mar_microhap_dict(self):
        return self._pre_mar_microhap_dict
    
    def set_pre_mar_microhap_dict(self, pre_mar_microhap_dict):
        self._pre_mar_microhap_dict = pre_mar_microhap_dict
    
    def get_cur_mar_microhap_dict(self):
        return self._cur_mar_microhap_dict
    
    def set_cur_mar_microhap_dict(self, cur_mar_microhap_dict):
        self._cur_mar_microhap_dict = cur_mar_microhap_dict
    
    def get_mar_snp_pos_dict(self):
        return self._mar_snp_pos_dict
    
    def set_mar_snp_pos_dict(self, mar_snp_pos_dict):
        self._mar_snp_pos_dict = mar_snp_pos_dict
        
    def get_mar_mh_alignment_dict(self):
        return self._mar_mh_alignment_dict
    
    def set_mar_mh_alignment_dict(self, mar_mh_alignment_dict):
        self._mar_mh_alignment_dict = mar_mh_alignment_dict
        
    def get_mar_microhap_df_dict(self):
        return self._mar_microhap_df_dict
    
    def set_mar_microhap_df_dict(self, mar_microhap_df_dict):
        self._mar_microhap_df_dict = mar_microhap_df_dict
    
    def get_final_all_microhap_df(self):
        return self._final_all_microhap_df
    
    def set_final_all_microhap_df(self, final_all_microhap_df):
        self._final_all_microhap_df = final_all_microhap_df
    
    def get_final_all_microhap_df_simple(self):
        return self._final_all_microhap_df_simple
    
    def set_final_all_microhap_df_simple(self, final_all_microhap_df_simple):
        self._final_all_microhap_df_simple = final_all_microhap_df_simple
        
    def get_final_microhap_df(self):
        return self._final_microhap_df
    
    def set_final_microhap_df(self, final_microhap_df):
        self._final_microhap_df = final_microhap_df
    
    def get_final_microhap_df_simple(self):
        return self._final_microhap_df_simple
    
    def set_final_microhap_df_simple(self, final_microhap_df_simple):
        self._final_microhap_df_simple = final_microhap_df_simple
        
    def get_mar_microhap_df_simple_dict(self):
        return self._mar_microhap_df_simple_dict

    def set_mar_microhap_df_simple_dict(self, mar_microhap_df_simple_dict):
        self._mar_microhap_df_simple_dict = mar_microhap_df_simple_dict

    def read_df_files(self, sam, suffix, file_dir)->dict:
        print(f"reading microhap file for {sam}")
        fpath=os.path.join(file_dir, sam, suffix)
        if not os.path.isfile(fpath):
            raise ValueError(f"{fpath} is not a file")
        tmp_df = (pd.read_csv(fpath, delimiter = '\t')
                        .pipe(lambda df : df.rename(columns={df.columns[0]:'Locus'}))
                        .pipe(lambda df: df.assign(Sample=sam)))
        tmp_df = tmp_df.reindex(columns=['Sample'] + [col for col in tmp_df.columns if col != 'Sample'])
        mar_dict={}
        if tmp_df.shape[0] !=0:
            markers=tmp_df['Locus'].unique()
            if len(markers) > 0:
                for mar in markers:
                    mar_dict[mar] = tmp_df[tmp_df['Locus']==mar]
        return mar_dict

    def populate_mar_sam_microhap(self, mar, samples, parent_mh_df, cur = True)->pd.DataFrame:
        if cur:
            mar_sam_microhap=set()#microhap seqs
            for sam in samples:
                mar_sam_microhap_df = parent_mh_df.loc[(parent_mh_df['Sample']==sam) & (parent_mh_df['Locus']==mar)]
                zygo= mar_sam_microhap_df['Zygosity'].iloc[0]
                if zygo == "homo":
                    mar_sam_microhap.add(mar_sam_microhap_df['Sequence'].iloc[0])
                elif zygo == "heter":
                    mar_sam_microhap.add(mar_sam_microhap_df['Sequence'].iloc[0])
                    mar_sam_microhap.add(mar_sam_microhap_df['Sequence'].iloc[1])
            if mar_sam_microhap:
                mar_sam_microhap = sorted(mar_sam_microhap)
            tmp_df = pd.DataFrame(columns=['locus', 'label', 'seq'])
            if len(mar_sam_microhap)!=0:
                tmp_df=pd.DataFrame({
                                'locus':[mar]*len(mar_sam_microhap),
                                'label':[f'mh_{i}' for i in range(len(mar_sam_microhap))],
                                'seq':mar_sam_microhap})
        else:
            tmp_df=parent_mh_df.loc[(parent_mh_df['Locus'] == mar) & (parent_mh_df['Allele'] != "-9"), ['Locus', 'Allele', 'Sequence']]
            if tmp_df is None :
                tmp_df = pd.DataFrame()
                tmp_df.columns = ['locus','label','seq']
                return tmp_df
            tmp_df = tmp_df.reset_index(drop=True)
            tmp_df = tmp_df.drop_duplicates(subset='Sequence')
            tmp_df.columns = ['locus','label','seq']
        tmp_df = tmp_df.sort_values(by="label").reset_index(drop=True)
        return tmp_df

    def populate_one_microhap_dict(self, parameter_class, metadata_class, cur = True)->None:
        n_threads = parameter_class.get_thread()
        print_time(f"starting to populate_one_microhap_dict for {cur}")
        with ThreadPoolExecutor(max_workers=n_threads) as executor:
            futures={}
            parent_mh_df = metadata_class.get_cur_microhap_df() if cur else metadata_class.get_pre_microhap_df()
            if parent_mh_df is not None and parent_mh_df.shape[0] > 0:
                markers = sorted(parent_mh_df['Locus'].unique())
                samples = sorted(parent_mh_df['Sample'].unique())
                mar_df_dict = {}
                for mar in markers:
                    future = executor.submit(self.populate_mar_sam_microhap, mar, samples, parent_mh_df, cur)
                    futures[future]=mar
                for future in as_completed(futures):
                    mar = futures[future]
                    try:
                        microhap_df = future.result()
                        with thread_lock:
                            mar_df_dict[mar]=microhap_df
                            # if not cur:
                            #     print_time(f'{mar} microhap_df is {microhap_df}')
                        print_time(f"finished to populate_one_microhap_dict for marker: {mar}")
                    except Exception as exc:
                        print(f"Error in {mar}: {exc}")
                mar_df_dict = dict(sorted(mar_df_dict.items()))
                if cur:
                    self._cur_mar_microhap_dict = mar_df_dict
                else:
                    self._pre_mar_microhap_dict = mar_df_dict

        print_time(f"finished to populate_one_microhap_dict")

    def populate_pre_post_microhap_dict(self, parameter_class, metadata_class)->None:
        self.populate_one_microhap_dict(parameter_class, metadata_class)
        if parameter_class.get_has_pre_mh():
            self.populate_one_microhap_dict(parameter_class, metadata_class, False)
    def populate_microhap_dict(self, parameter_class, metadata_class)->None:
        print_time(f"starting to populate_microhap_dict")
        #pdb.set_trace()
        for mar in metadata_class.get_ref_markers_list():
            tmp_mar_ref = self.get_loc_ref_dict().get(mar, None)
            if tmp_mar_ref is not None:
                tmp_cur_mar_mh_df = copy.deepcopy(self.get_cur_mar_microhap_dict().get(mar, None))
                if tmp_cur_mar_mh_df is not None:
                    if parameter_class.get_has_pre_mh():
                        tmp_pre_mar_mh_df = copy.deepcopy(self.get_pre_mar_microhap_dict().get(mar, None))
                        pre_mar_mh_seqs_set = set()
                        if tmp_pre_mar_mh_df is not None:
                            pre_mar_mh_seqs_set = set(tmp_pre_mar_mh_df['seq'].unique())
                        cur_mar_mh_seqs_set = set(tmp_cur_mar_mh_df['seq'].unique())
                        new_mar_mh_seqs_list = sorted(cur_mar_mh_seqs_set.difference(pre_mar_mh_seqs_set))
                        if len(new_mar_mh_seqs_list) != 0:
                            tmp_df = pd.DataFrame({'locus':[mar]*len(new_mar_mh_seqs_list),
                                                    'label':[f'mh_{i+len(pre_mar_mh_seqs_set)}' for i in range(len(new_mar_mh_seqs_list))],
                                                    'seq':list(new_mar_mh_seqs_list)
                                                    })
                            tmp_mar_ref.set_mar_microhap_df(pd.concat([tmp_pre_mar_mh_df, tmp_df], ignore_index=True))
                            tmp_mar_ref.set_cur_mar_microhap_df(tmp_df)
                            if tmp_pre_mar_mh_df is not None:
                                tmp_mar_ref.set_pre_mar_microhap_df(tmp_pre_mar_mh_df)
                            else:
                                tmp_mar_ref.set_pre_mar_microhap_df(pd.DataFrame())
                            tmp_mar_ref.set_has_new_mh(True)
                        else:
                            tmp_mar_ref.set_mar_microhap_df(tmp_pre_mar_mh_df)
                            tmp_mar_ref.set_cur_mar_microhap_df(tmp_pre_mar_mh_df)
                            if tmp_pre_mar_mh_df is not None:
                                tmp_mar_ref.set_pre_mar_microhap_df(tmp_pre_mar_mh_df)
                            else:
                                tmp_mar_ref.set_pre_mar_microhap_df(pd.DataFrame())
                            tmp_mar_ref.set_has_new_mh(False)
                    else:
                        tmp_mar_ref.set_mar_microhap_df(tmp_cur_mar_mh_df)
                        tmp_mar_ref.set_cur_mar_microhap_df(tmp_cur_mar_mh_df)
            else:
                raise ValueError(f"Error: cannot find {mar} in reference markers!\n")

        print_time(f"finished to populate_microhap_dict")

    def do_translate(self, mar_mh_df, ref_refMicrotype):
        if len(ref_refMicrotype.get_codingpos()) != 0:
            for seq in mar_mh_df['seq']:
                pass

    def populate_microhap_aa_dict(self, n_threads, mar_refs_dict)->None:
        with ThreadPoolExecutor(max_workers=n_threads) as executor:
            futures={}
            for mar in self.get_markers():
                mar_mh_df = self.get_mar_microhap_dict().get(mar, None)
                ref_refMicrotype = mar_refs_dict.get(mar, None)
                if mar_mh_df is not None and ref_refMicrotype is not None and len(ref_refMicrotype.get_codingpos()) != 0:
                    future = executor.submit(self.do_translate, mar_mh_df, ref_refMicrotype)
                    futures[future]=mar
            for future in as_completed(futures):
                mar = futures[future]
                try:
                    future.result()
                except Exception as exc:
                        print(f'Error while performing translation for marker {mar}: {exc}')
    def do_mafft_align(self, id, seq_records, fpath):
        print_time(f'Starting MAFFT alignment for {id}')
        if not seq_records:
            return
        # Ensure the tmp directory exists
        tmp_dir = os.path.join(fpath, "align")
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)

        # File paths for temporary files
        fa_file = os.path.join(tmp_dir, f'{id}_mh.fasta')
        align_file = os.path.join(tmp_dir, f'{id}_align.fasta')
        try:
            # Write input sequences to the temporary FASTA file
            with open(fa_file, "w") as output_file:
                SeqIO.write(seq_records, output_file, "fasta")

            # Run MAFFT alignment
            mafft_cline = MafftCommandline(input=fa_file)
            stdout, stderr = mafft_cline()
            alignment = AlignIO.read(StringIO(stdout), "fasta")

            # Calculate the distance matrix
            calculator = DistanceCalculator('identity')  # or 'euclidean' or another distance metric
            distance_matrix = calculator.get_distance(alignment)

            # Construct a phylogenetic tree using the NJ method
            constructor = DistanceTreeConstructor()
            tree = constructor.nj(distance_matrix)
            self.remove_inner_labels(tree)
            print_time(f'Finished MAFFT alignment for {id}')
            return tree
        except Exception as e:
            print(f"Error during MAFFT alignment for {id}: {e}")
            raise
    def remove_inner_labels(self, tree):
        for clade in tree.find_clades():
            # If the clade has children, it's an internal node
            if clade.is_terminal() == False:
                clade.name = None  # Clear the inner label
    def do_alignment(self, ref_mh_class, parameter_class):
        children_microtype_dict:Dict[str, CompreMicrotypeClass] = {} #including dna and protein
        #pdb.set_trace()
        if parameter_class.get_include_pre_mh():
            #pdb.set_trace()
            mh_seq_df = ref_mh_class.get_mar_microhap_df().copy()#mh lookup table
            #print_time(f"{mh_seq_df}")
            if len(mh_seq_df) == 0:
                return children_microtype_dict
            mar = ref_mh_class.get_locus()
            print_time(f'{mar} ref_mh_class.get_ref_microtype_dict() len is {len(ref_mh_class.get_ref_microtype_dict())}')
            if not ref_mh_class.get_has_splicer():
                print_time(f'{mar} does not have ref_mh_class.get_has_splicer()')
                #pdb.set_trace()
                splicer = "splicer_0"
                ref_splicer0_mt_seq = copy.deepcopy(ref_mh_class.get_ref_microtype_dict().get(splicer).get_ref_dna_seq())#CompreMicrotypeClass
                tmp_compre_mt = CompreMicrotypeClass()
                tmp_compre_mt.set_mar(mar)
                tmp_compre_mt.set_splicer(splicer)
                tmp_compre_mt.set_dna_mh_df(mh_seq_df)
                tmp_compre_mt.set_target_dna_snp_pos_list(ref_mh_class.get_snppos())
                tmp_compre_mt.set_ref_dna_seq(ref_mh_class.get_dna_ref())
                tot_snp_pos_set = set()
                seq_records = []
                for _, row in mh_seq_df.iterrows():
                    _, label, seq = row
                    tmp_compre_var = CompreVariationClass()
                    id = f'{mar}_{label}'
                    tmp_compre_var.set_id(id)
                    tmp_compre_var.set_mar(mar)
                    tmp_compre_var.set_splicer(splicer)
                    tmp_compre_var.set_mt(label)
                    tmp_compre_var.set_seq(seq)
                    indels_pos, mismatches_pos, snp_str = do_pairwise_alignment(ref_splicer0_mt_seq, seq)
                    tmp_compre_var.set_indel_pos_list(indels_pos)
                    tmp_compre_var.set_snp_pos_list(mismatches_pos)
                    tmp_compre_var.set_snp_str(snp_str)
                    tmp_compre_mt.get_dna_mh_dict()[label]=tmp_compre_var
                    if len(indels_pos) == 0:
                        tot_snp_pos_set.update(mismatches_pos)
                    seq_records.append(SeqRecord(Seq(seq), id=id))
                tmp_compre_mt.set_tot_dna_snp_pos_list(sorted(tot_snp_pos_set))
                tmp_compre_mt.generate_base_freq_df()
                tmp_compre_mt.set_dna_tre(self.do_mafft_align(f'{mar}_{splicer}', seq_records, parameter_class.get_post_microhap_output_dir()))
                children_microtype_dict[splicer] = tmp_compre_mt
            else:
                #splicer for the whole length alignment only for dna alingment, aa should be the following ones splicer_0
                splicer = "splicer"
                ref_splicer_mt_seq = copy.deepcopy(ref_mh_class.get_dna_ref())#CompreMicrotypeClass
                tmp_compre_mt = CompreMicrotypeClass()
                tmp_compre_mt.set_mar(mar)
                tmp_compre_mt.set_splicer(splicer)
                tmp_compre_mt.set_dna_mh_df(mh_seq_df)
                tmp_compre_mt.set_target_dna_snp_pos_list(ref_mh_class.get_snppos())
                tmp_compre_mt.set_ref_dna_seq(ref_mh_class.get_dna_ref())
                tot_snp_pos_set = set()
                seq_records = []
                for _, row in mh_seq_df.iterrows():
                    _, label, seq = row
                    tmp_compre_var = CompreVariationClass()
                    id = f'{mar}_{label}'
                    tmp_compre_var.set_id(id)
                    tmp_compre_var.set_mar(mar)
                    tmp_compre_var.set_splicer(splicer)
                    tmp_compre_var.set_mt(label)
                    tmp_compre_var.set_seq(seq)
                    indels_pos, mismatches_pos, snp_str = do_pairwise_alignment(ref_splicer_mt_seq, seq)
                    tmp_compre_var.set_indel_pos_list(indels_pos)
                    tmp_compre_var.set_snp_pos_list(mismatches_pos)
                    tmp_compre_var.set_snp_str(snp_str)
                    tmp_compre_mt.get_dna_mh_dict()[label]=tmp_compre_var
                    if len(indels_pos) == 0:
                        tot_snp_pos_set.update(mismatches_pos)
                    seq_records.append(SeqRecord(Seq(seq), id=id))
                tmp_compre_mt.set_tot_dna_snp_pos_list(sorted(tot_snp_pos_set))
                tmp_compre_mt.generate_base_freq_df()
                tmp_compre_mt.set_dna_tre(self.do_mafft_align(f'{mar}_{splicer}', seq_records, parameter_class.get_post_microhap_output_dir()))
                children_microtype_dict[splicer] = tmp_compre_mt

                print_time(f'{mar} has ref_mh_class.get_has_splicer()')
                if len(ref_mh_class.get_ref_microtype_dict()) == 0:
                    return children_microtype_dict
                for idx, (splicer, mt_it) in enumerate(ref_mh_class.get_ref_microtype_dict().items()):
                    print_time(f'processing {mar}_{splicer}')
                    ref_splicer_mt = copy.deepcopy(mt_it)#CompreMicrotypeClass
                    tmp_compre_mt = CompreMicrotypeClass()
                    tmp_compre_mt.set_mar(mar)
                    tmp_compre_mt.set_splicer(splicer)
                    tmp_compre_mt.set_target_dna_snp_pos_list(ref_splicer_mt.get_target_dna_snp_pos_list())
                    tmp_compre_mt.set_target_aa_snp_pos_list(ref_splicer_mt.get_target_aa_snp_pos_list())
                    dna_ref = ref_splicer_mt.get_ref_dna_seq()
                    aa_ref = ref_splicer_mt.get_ref_aa_seq()
                    tmp_compre_mt.set_ref_dna_seq(dna_ref)
                    tmp_compre_mt.set_ref_aa_seq(aa_ref)
                    mh_df = pd.DataFrame(columns=['mar', 'label', 'seq'])
                    mp_df = pd.DataFrame(columns=['mar', 'label', 'seq'])
                    dna_tot_snp_pos_set = set()
                    aa_tot_snp_pos_set = set()
                    dna_seq_records = []
                    aa_seq_records = []
                    tmp_compre_mt.set_splicer_pos_list(ref_splicer_mt.get_splicer_pos_list())
                    tmp_compre_mt.set_splicer_aa_pos_list(ref_splicer_mt.get_splicer_aa_pos_list())
                    for _, row in mh_seq_df.iterrows():#mh lookup table
                        mar2, label, seq = row
                        dna_seq, aa_seq = trans_single_dna(seq, ref_splicer_mt.get_splicer_pos_list())
                        mh_df.loc[len(mh_df)] = [mar2,label,dna_seq]
                        mp_df.loc[len(mp_df)] = [mar2,label,aa_seq]
                        dna_tmp_compre_var = CompreVariationClass()
                        id = f'{mar}_{splicer}_{label}'
                        dna_tmp_compre_var.set_id(id)
                        dna_tmp_compre_var.set_mar(mar)
                        dna_tmp_compre_var.set_splicer(splicer)
                        dna_tmp_compre_var.set_mt(label)
                        dna_tmp_compre_var.set_seq(dna_seq)

                        dna_indels_pos, dna_mismatches_pos, dna_snp_str = do_pairwise_alignment(dna_ref, dna_seq)
                        dna_tmp_compre_var.set_indel_pos_list(dna_indels_pos)
                            #ori_pos_list = ref_splicer_mt.convert_pos_cur_2_ori(dna_mismatches_pos)
                        dna_tmp_compre_var.set_snp_pos_list(dna_mismatches_pos)
                        dna_tmp_compre_var.set_snp_str(dna_snp_str)
                        tmp_compre_mt.get_dna_mh_dict()[label]=dna_tmp_compre_var
                        if len(dna_indels_pos) == 0:
                            dna_tot_snp_pos_set.update(dna_mismatches_pos)
                        dna_seq_records.append(SeqRecord(Seq(dna_seq), id=id))

                        aa_tmp_compre_var = CompreVariationClass()
                        id = f'{mar}_{splicer}_{label.replace("mh_", "mp_", 1)}'
                        aa_tmp_compre_var.set_id(id)
                        aa_tmp_compre_var.set_mar(mar)
                        aa_tmp_compre_var.set_splicer(splicer)
                        aa_tmp_compre_var.set_mt(label)
                        aa_tmp_compre_var.set_seq(aa_seq)

                        aa_indels_pos, aa_mismatches_pos, aa_snp_str = do_pairwise_alignment(aa_ref, aa_seq)
                        aa_tmp_compre_var.set_indel_pos_list(aa_indels_pos)
                        aa_tmp_compre_var.set_snp_pos_list(aa_mismatches_pos)
                        aa_tmp_compre_var.set_snp_str(aa_snp_str)
                        tmp_compre_mt.get_aa_mp_dict()[label]=aa_tmp_compre_var
                        if len(aa_indels_pos) == 0:
                            aa_tot_snp_pos_set.update(aa_mismatches_pos)
                        aa_seq_records.append(SeqRecord(Seq(aa_seq), id=id))
                    #tot_ori_pos_list = ref_splicer_mt.convert_pos_cur_2_ori(sorted(dna_tot_snp_pos_set))
                    tmp_compre_mt.set_tot_dna_snp_pos_list(sorted(dna_tot_snp_pos_set))
                    tmp_compre_mt.set_tot_aa_snp_pos_list(sorted(aa_tot_snp_pos_set))
                    tmp_compre_mt.set_dna_mh_df(mh_df)
                    tmp_compre_mt.set_aa_mh_df(mp_df)
                    tmp_compre_mt.generate_base_freq_df()
                    tmp_compre_mt.generate_base_freq_df(False)
                    if idx == 0 or ref_mh_class.is_overlapped_gene():
                        tmp_compre_mt.set_aa_tre(self.do_mafft_align(f'{mar}_{splicer}', aa_seq_records, parameter_class.get_post_microhap_output_dir()))
                    #tmp_compre_mt.set_dna_tre(self.do_mafft_align(f'{mar}_{splicer}', dna_seq_records))
                    children_microtype_dict[splicer] = tmp_compre_mt
        return children_microtype_dict
            #iterate through children_microtype and get the snp pos in each splicer
    def perform_seq_alignment(self, parameter_class)->None:
        print_time("Performing sequence alignment...")
        with ThreadPoolExecutor(max_workers=parameter_class.get_thread()) as executor:
            align_futures={}
            for mar, ref_mh_class in self.get_loc_ref_dict().items():
                future = executor.submit(self.do_alignment, ref_mh_class, parameter_class)
                align_futures[future]=mar
            for future in as_completed(align_futures):
                mar = align_futures[future]
                try:
                    children_microtype_dict = future.result()
                    with thread_lock:
                        self.get_loc_ref_dict()[mar].set_children_microtype_dict(children_microtype_dict)
                    print_time(f"finished alignment for marker: {mar}")
                except Exception as exc:
                        print(f'Error while performing mh alignment for marker {mar}: {exc}')
        print_time("finished sequence alignment...")

    def populate_each_mar_mh_dict(self, mar, cur_mar_mh_df, pre_mar_mh_df, mh_lookup_table_dict)->tuple:
        final_sam_cur_mh_dict = {}
        final_sam_pre_mh_dict = {}
        final_sam_cur_mh_sim_dict={}#simple df sample, mar_allele1, mar_allele2
        final_sam_pre_mh_sim_dict={}
        if pre_mar_mh_df is not None and pre_mar_mh_df.shape[0]!=0:
            for sam in sorted(pre_mar_mh_df['Sample'].unique()):
                tmp_df = pre_mar_mh_df[pre_mar_mh_df['Sample'] == sam].reset_index(drop=True)
                final_sam_pre_mh_dict[sam] = tmp_df
                tmp_sim_df = tmp_df[['Sample', 'Allele']].reset_index(drop=True).copy()
                tmp_sim_df = tmp_sim_df.pivot_table(index='Sample',
                                                    columns=tmp_sim_df.groupby('Sample').cumcount(),
                                                    values='Allele',
                                                    aggfunc='first').reset_index()
                tmp_sim_df.columns=['Sample', f'{mar}_allele1', f'{mar}_allele2']
                final_sam_pre_mh_sim_dict[sam] = tmp_sim_df
        if cur_mar_mh_df is not None and cur_mar_mh_df.shape[0] != 0:
            #pdb.set_trace()
            cur_mar_mh_df['Allele']=cur_mar_mh_df['Sequence'].map(mh_lookup_table_dict).fillna('-9')
            for sam in sorted(cur_mar_mh_df['Sample'].unique()):
                tmp_df = cur_mar_mh_df[cur_mar_mh_df['Sample'] == sam].reset_index(drop=True)
                final_sam_cur_mh_dict[sam] = tmp_df
                tmp_sim_df = tmp_df[['Sample', 'Allele', 'Zygosity']].reset_index(drop=True).copy()
                zygo = tmp_sim_df['Zygosity'].iloc[0]
                if zygo == 'homo':
                    tmp_sim_df.at[1, 'Allele']=tmp_sim_df['Allele'].iloc[0]
                elif zygo == 'heter':
                    tmp_sim_df=tmp_sim_df.sort_values(by='Allele')
                    #pass
                else:
                    tmp_sim_df.at[0, 'Allele'] = '-9'
                    tmp_sim_df.at[1, 'Allele'] = '-9'
                tmp_sim_df=tmp_sim_df.drop('Zygosity', axis=1)
                tmp_sim_df = tmp_sim_df.pivot_table(index='Sample',
                                            columns=tmp_sim_df.groupby('Sample').cumcount(),
                                            values='Allele',
                                            aggfunc='first').reset_index()
                tmp_sim_df.columns=['Sample', f'{mar}_allele1', f'{mar}_allele2']
                final_sam_cur_mh_sim_dict[sam] = tmp_sim_df
        #pdb.set_trace()
        return final_sam_cur_mh_dict,final_sam_cur_mh_sim_dict, final_sam_pre_mh_dict,final_sam_pre_mh_sim_dict

    def populate_final_mar_mh_df_dict(self, parameter_class, metadata_class)->bool:
        print_time("staring to populate_final_mar_mh_df_dict")
        n_threads = parameter_class.get_thread()
        cur_mh_df = metadata_class.get_cur_microhap_df()
        pre_mh_df = metadata_class.get_pre_microhap_df()
        final_cur_mh_dict = {}
        final_cur_sim_mh_dict = {}
        final_pre_mh_dict = {}
        final_pre_sim_mh_dict = {}
        with ThreadPoolExecutor(max_workers=n_threads) as executor:
            futures ={}
            for mar, mar_value in self.get_loc_ref_dict().items():
                try:
                    mh_lookup_table_dict = mar_value.get_mar_microhap_df().set_index('seq')['label'].to_dict()
                    #print_time(f"mh_lookup_table_dict is {mh_lookup_table_dict}")
                    if mh_lookup_table_dict is None or not mh_lookup_table_dict:
                        continue
                    cur_mar_mh_df = cur_mh_df[cur_mh_df['Locus'] == mar].reset_index(drop=True).copy()
                    #print_time(f"cur_mar_mh_df is {cur_mar_mh_df}")
                    if cur_mar_mh_df is None or len(cur_mar_mh_df) == 0:
                        continue
                    pre_mar_mh_df = pd.DataFrame()
                    if parameter_class.get_has_pre_mh():
                        pre_mar_mh_df = pre_mh_df[pre_mh_df['Locus'] == mar].reset_index(drop=True).copy()
                    future = executor.submit(self.populate_each_mar_mh_dict, mar, cur_mar_mh_df, pre_mar_mh_df, mh_lookup_table_dict)
                    futures[future]=mar
                except Exception as e:
                        print(f"An error occurred while processing {mar}: {e}")
            for future in as_completed(futures):
                mar = futures[future]
                try:
                    final_sam_cur_mh_dict,final_sam_cur_mh_sim_dict, final_sam_pre_mh_dict,final_sam_pre_mh_sim_dict = future.result()
                    with thread_lock:
                        self.get_loc_ref_dict().get(mar).set_final_mar_cur_microhap_nested_dict(final_sam_cur_mh_dict)
                        final_cur_mh_dict[mar] = pd.concat(final_sam_cur_mh_dict.values(), ignore_index = True)
                        self.get_loc_ref_dict().get(mar).set_final_mar_cur_sim_microhap_nested_dict(final_sam_cur_mh_sim_dict)
                        final_cur_sim_mh_dict[mar] = pd.concat(final_sam_cur_mh_sim_dict.values(), ignore_index = True)
                        if parameter_class.get_has_pre_mh():
                            self.get_loc_ref_dict().get(mar).set_final_mar_pre_microhap_nested_dict(final_sam_pre_mh_dict)
                            final_pre_mh_dict[mar] = pd.concat(final_sam_pre_mh_dict.values(), ignore_index = True)
                            self.get_loc_ref_dict().get(mar).set_final_mar_pre_sim_microhap_nested_dict(final_sam_pre_mh_sim_dict)
                            final_pre_sim_mh_dict[mar] = pd.concat(final_sam_pre_mh_sim_dict.values(), ignore_index = True)
                except Exception as exc:
                    print(f"Error while populating final mh df for marker {mar}: {exc}")
        self.output_final_microhap_table(parameter_class, final_cur_mh_dict, final_cur_sim_mh_dict, final_pre_mh_dict, final_pre_sim_mh_dict)
        print_time("finished to populate_final_mar_mh_df_dict")
        return True
    def output_final_microhap_table(self, parameter_class, final_cur_mh_dict, final_cur_sim_mh_dict, final_pre_mh_dict, final_pre_sim_mh_dict):
        if final_cur_mh_dict.values():
            self._final_microhap_df = pd.concat(final_cur_mh_dict.values(), ignore_index = True)
            self._final_microhap_df = self._final_microhap_df.sort_values(by=['Sample', 'Locus']).reset_index(drop=True)
        else:
            self._final_microhap_df = pd.DataFrame()
        if self._final_microhap_df.shape[0] > 0:
            self._final_microhap_df.to_csv(os.path.join(parameter_class.get_post_microhap_output_dir(), "All_cur_mh_table.txt"), sep = '\t', index = False)
        
        final_cur_sim_mh_df_list = []
        for i, (mar, df) in enumerate(final_cur_sim_mh_dict.items()):
            if i == 0:
                final_cur_sim_mh_df_list.append(df)
            else:
                final_cur_sim_mh_df_list.append(df.drop(columns='Sample'))
        if final_cur_sim_mh_df_list:
            self._final_microhap_df_simple = pd.concat(final_cur_sim_mh_df_list, axis = 1)
        else:
            self._final_microhap_df_simple = pd.DataFrame()
        if self._final_microhap_df_simple.shape[0] > 0:
            self._final_microhap_df_simple.to_csv(os.path.join(parameter_class.get_post_microhap_output_dir(), "All_cur_mh_sim_table.txt"), sep = '\t', index = False)
        
        if parameter_class.get_has_pre_mh():
            if final_pre_mh_dict.values():
                final_pre_mh_df = pd.concat(final_pre_mh_dict.values(), ignore_index = True)
            else:
                final_pre_mh_df = pd.DataFrame()
            if final_pre_mh_df.shape[0] > 0:
                self._final_microhap_df = pd.concat([final_pre_mh_df, self._final_microhap_df], ignore_index=True) if self._final_microhap_df.shape[0] > 0 else final_pre_mh_df
                self._final_microhap_df.to_csv(os.path.join(parameter_class.get_post_microhap_output_dir(), "All_mh_table.txt"), sep = '\t', index = False)
            
            final_pre_sim_mh_df_list = []
            for i, (mar,df) in enumerate(final_pre_sim_mh_dict.items()):
                if i == 0:
                    final_pre_sim_mh_df_list.append(df)
                else:
                    final_pre_sim_mh_df_list.append(df.drop(columns='Sample'))
            if final_pre_sim_mh_df_list:
                final_pre_sim_mh_df = pd.concat(final_pre_sim_mh_df_list, axis = 1)
            else:
                final_pre_sim_mh_df = pd.DataFrame()
            if final_pre_sim_mh_df.shape[0] > 0:
                self._final_all_microhap_df_simple = pd.concat([final_pre_sim_mh_df, self._final_microhap_df_simple], ignore_index=True) if self._final_microhap_df_simple.shape[0] > 0 else final_pre_sim_mh_df
                self._final_all_microhap_df_simple.to_csv(os.path.join(parameter_class.get_post_microhap_output_dir(), "All_mh_sim_table.txt"), sep = '\t', index = False)
    def print(self):
        for mar, mar_value in self.get_loc_ref_dict().items():
            print(f"Marker: {mar}")
            mar_value.print_ref()

    # def populate_final_mar_mh_df_dict(self, parameter_class, metadata_class)->bool:
        # n_threads=parameter_class.get_thread()
        # output_dir=parameter_class.get_post_microhap_output_dir()
        # cur_mh_df = metadata_class.get_cur_microhap_df()
        # pre_mh_df = metadata_class.get_pre_microhap_df()
        # tot_mh_df = pd.DataFrame()
        # if parameter_class.get_include_pre_mh() and pre_mh_df.shape[0] != 0:
        #     tot_mh_df = pd.concat([pre_mh_df, tot_mh_df], ignore_index=True)
        # else:
        #     tot_mh_df = cur_mh_df.copy()
        # tot_mh_df = tot_mh_df.sort_values(by=['Locus', 'Sample']).reset_index(drop=True)
        # markers=sorted(tot_mh_df['Locus'].unique())
        # samples=sorted(tot_mh_df['Sample'].unique())
        # with ThreadPoolExecutor(max_workers=n_threads) as executor:
        #     futures={}
        #     for mar in markers:
        #         mar_mh_df = tot_mh_df[tot_mh_df['Locus'] == mar].copy().reset_index(drop=True)
        #         mar_mh_parents=self.get_mar_microhap_dict().get(mar)
        #         future=executor.submit(self.populate_each_mar_mh_df,samples, mar, mar_mh_df, mar_mh_parents)
        #         futures[future]=mar
        #     for future in as_completed(futures):
        #         mar = futures[future]
        #         try:
        #             mar_mh_df, mar_mh_df_sim = future.result()
        #             with thread_lock:
        #                 self._mar_microhap_df_dict[mar] = mar_mh_df
        #                 self._mar_microhap_df_simple_dict[mar] = mar_mh_df_sim
        #         except Exception as exc:
        #             print(f"Error while populating final mh df for marker {mar}: {exc}")
        #     self._mar_microhap_df_dict=dict(sorted(self.get_mar_microhap_df_dict().items()))
        #     self._mar_microhap_df_simple_dict = dict(sorted(self.get_mar_microhap_df_simple_dict().items()))
            
        # self._final_microhap_df = pd.concat(self.get_mar_microhap_df_dict().values(), ignore_index=True)
        # self._final_microhap_df=self._final_microhap_df.sort_values(by=['Sample', 'Locus'], ascending=[True,True])
        # self._final_microhap_df.reset_index(drop=True, inplace=True)
        # output_path=os.path.join(output_dir, "all_sample_microhap_comprehensive_table.txt")
        # try:
        #     self._final_microhap_df.to_csv(output_path, sep = "\t", index=False)
        # except Exception as e:
        #     print(f"Error while writing to file {output_path}: {e}")
            
        # simple_mh_df = pd.concat(self.get_mar_microhap_df_simple_dict().values(), axis=1)
        # if simple_mh_df.shape[0] == len(samples):
        #     simple_mh_df=simple_mh_df.sort_index(axis=1)
        #     simple_mh_df.insert(0, 'Sample', samples)
        #     simple_mh_df=simple_mh_df.sort_values(by='Sample', ascending=True)
        #     simple_mh_df.reset_index(drop=True,inplace=True)
        #     self._final_microhap_df_simple = simple_mh_df
        #     output_path=os.path.join(output_dir, "all_sample_microhap_table.txt")
        #     try:
        #         simple_mh_df.to_csv(output_path, sep = "\t", index=False)
        #     except Exception as e:
        #             print(f"Error while writing to file {output_path}: {e}")
        # else:
        #     raise ValueError("Error in populating final mh df. The number of samples in the simple_mh_df does not match with the number of samples.")
        # return True
