import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import multiprocessing as mp
from ..utils.utils_common import print_time
import copy
from ..utils.utils_func import populate_mar_sam_microhap, populate_each_mar_mp_dict, populate_each_mar_mh_dict, trans_single_dna
from ..utils.utils_common import print_time, thread_lock
from ..utils.utils_alignment import do_alignment2
from ..utils import modern_messagebox
import pdb
import traceback
class PostMicrohapClass:
    def __init__(self) -> None:
        
        self._final_microhap_df = pd.DataFrame() #with allele names change to mh name for the microhap_df
        self._final_microhap_df_simple = pd.DataFrame() #only contain mh name in sample X marker 
        
        self._final_micropep_df = pd.DataFrame() #with allele names change to mp name for the micropep_df
        self._final_micropep_df_simple = pd.DataFrame() #only contain mp name in
        
        #self._final_all_microhap_df = pd.DataFrame() #with allele names change to mh name for the microhap_df
        #self._final_all_microhap_df_simple = pd.DataFrame() #only contain mh name in sample X marker 
        
        #self._mar_microhap_df_simple_dict = {} #{mar:dataframe for all samples simple mh} 
        
        #self._mar_micropep_df_simple_dict = {} # {mar: df with columns=['locus', 'label', 'seq']} for micropeptide, only for markers with exon
        
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
        
    def get_final_micropep_df(self):
        return self._final_micropep_df
    def set_final_micropep_df(self, final_micropep_df):
        self._final_micropep_df = final_micropep_df
    def get_final_micropep_df_simple(self):
        return self._final_micropep_df_simple
    def set_final_micropep_df_simple(self, final_micropep_df_simple):
        self._final_micropep_df_simple = final_micropep_df_simple
    
    # def get_final_all_microhap_df(self):
    #     return self._final_all_microhap_df
    
    # def set_final_all_microhap_df(self, final_all_microhap_df):
    #     self._final_all_microhap_df = final_all_microhap_df
    
    # def get_final_all_microhap_df_simple(self):
    #     return self._final_all_microhap_df_simple
    
    # def set_final_all_microhap_df_simple(self, final_all_microhap_df_simple):
    #     self._final_all_microhap_df_simple = final_all_microhap_df_simple
        
    def get_final_microhap_df(self):
        return self._final_microhap_df
    
    def set_final_microhap_df(self, final_microhap_df):
        self._final_microhap_df = final_microhap_df
    
    def get_final_microhap_df_simple(self):
        return self._final_microhap_df_simple
    
    def set_final_microhap_df_simple(self, final_microhap_df_simple):
        self._final_microhap_df_simple = final_microhap_df_simple
        
    # def get_mar_microhap_df_simple_dict(self):
    #     return self._mar_microhap_df_simple_dict

    # def set_mar_microhap_df_simple_dict(self, mar_microhap_df_simple_dict):
    #     self._mar_microhap_df_simple_dict = mar_microhap_df_simple_dict
        

    def read_df_files(self, sam, suffix, file_dir)->dict:
        print(f"reading microhap file for {sam}")
        fpath=os.path.join(file_dir, sam, suffix)
        if not os.path.isfile(fpath):
            modern_messagebox.showerror(None, "File Not Found", f"{fpath} is not a file")
            raise ValueError(f"{fpath} is not a file")
        tmp_df = (pd.read_csv(fpath, delimiter = '\t')
                        .pipe(lambda df : df.rename(columns={df.columns[0]:'locus'}))
                        .pipe(lambda df: df.assign(sample=sam)))
        tmp_df = tmp_df.reindex(columns=['sample'] + [col for col in tmp_df.columns if col != 'sample'])
        mar_dict={}
        if tmp_df.shape[0] !=0:
            markers=tmp_df['locus'].unique()
            if len(markers) > 0:
                for mar in markers:
                    mar_dict[mar] = tmp_df[tmp_df['locus']==mar]
        return mar_dict

    def populate_one_microhap_dict(self, parameter_class, metadata_class, cur = True, log_func = None)->bool:
        n_threads = parameter_class.get_thread()
        ctx = mp.get_context("spawn")
        print_time(f"starting to populate microhap dictionary for {cur}")
        if log_func is not None:
            log_func(f"Populating {'current' if cur else 'pre'} microhap dictionary...")
        parent_mh_df = metadata_class.get_cur_microhap_df() if cur else metadata_class.get_pre_microhap_df()
        if parent_mh_df is not None and parent_mh_df.shape[0] > 0:
            markers = sorted(parent_mh_df['locus'].unique())
            samples = sorted(parent_mh_df['sample'].unique()) if cur else []
            mar_df_dict = {}
            num_mars = 0
            with ProcessPoolExecutor(max_workers=n_threads, mp_context=ctx) as executor:
                futures={executor.submit(populate_mar_sam_microhap,
                                         mar, 
                                         samples, 
                                         parent_mh_df[parent_mh_df['locus']==mar].reset_index(drop=True), 
                                         self.get_loc_ref_dict().get(mar, None),
                                         cur): mar for mar in markers}
                for future in as_completed(futures):
                    mar = futures[future]
                    try:
                        mar_df_dict[mar]=future.result()
                        num_mars += 1
                        if num_mars % 10 == 0:
                            print_time(f"populate_one_microhap_dict Processed {num_mars} out of {len(markers)} markers...")
                            if log_func is not None:
                                log_func(f"Processed {num_mars} out of {len(markers)} markers for {'current' if cur else 'pre'} microhap dictionary...")
                        #print(f"finished to populate_one_microhap_dict for marker: {mar}")
                    except Exception as exc:
                        print(f"Error in {mar}: {exc}")
            if cur:
                self._cur_mar_microhap_dict = mar_df_dict
            else:
                self._pre_mar_microhap_dict = mar_df_dict
        print_time(f"finished to populate microhap dictionary")
        if log_func is not None:
            log_func(f"Finished populating {'current' if cur else 'pre'} microhap dictionary.")
        return True

    def populate_pre_post_microhap_dict(self, parameter_class, metadata_class, log_func = None)->bool:
        self.populate_one_microhap_dict(parameter_class, metadata_class, True, log_func)
        if parameter_class.get_has_pre_mh():
            self.populate_one_microhap_dict(parameter_class, metadata_class, False, log_func)
        return True
    
    def populate_microhap_dict(self, parameter_class, metadata_class, log_func = None)->bool:
        print_time(f"starting to populate_microhap_dict")
        if log_func is not None:
            log_func("Starting to populate post microhap dictionary...")
        #pdb.set_trace()
        num_mars = 0
        mh_lookup_table_dict = {}
        for mar in metadata_class.get_ref_markers_list():
            tmp_mar_ref = self.get_loc_ref_dict().get(mar, None)
            if tmp_mar_ref is not None:
                tmp_cur_mar_mh_df = copy.deepcopy(self.get_cur_mar_microhap_dict().get(mar, None))
                if tmp_cur_mar_mh_df is not None:
                    if parameter_class.get_has_pre_mh():
                        tmp_pre_mar_mt_df = copy.deepcopy(self.get_pre_mar_microhap_dict().get(mar, None))
                        pre_mar_mh_seqs_set = set()
                        max_id = 0
                        start_1 = False
                        if tmp_pre_mar_mt_df is not None:
                            pre_mar_mh_seqs_set = set(tmp_pre_mar_mt_df['mh_seq'].unique())
                            max_id = tmp_pre_mar_mt_df['mh_id'].max()
                            start_1 = True
                        cur_mar_mh_seqs_set = set(tmp_cur_mar_mh_df['mh_seq'].unique())
                        new_mar_mh_seqs_list = sorted(cur_mar_mh_seqs_set.difference(pre_mar_mh_seqs_set))
                        
                        tmp_mar_mp_seqs_set = set()
                        tmp_mar_mp_seqs_list = []
                        tmp_mar_mp_seqs_id_list = []
                        tmp_mar_mh_mp_id_map = {}#mh: (mp: id)
                        if tmp_mar_ref.get_has_exon():
                            mp_start_1 = False
                            mp_max_id = 0
                            mp_map = {}
                            pre_mar_mp_seqs_set = {seq.strip() for seq in tmp_pre_mar_mt_df['mp_seq'].dropna() if isinstance(seq, str) and seq.strip()}
                            if len(pre_mar_mp_seqs_set) > 0:
                                mp_max_id = tmp_pre_mar_mt_df['mp_id'].max()
                                mp_start_1 = True
                                for _, row in tmp_pre_mar_mt_df.iterrows():
                                    mp_map[row['mp_seq']] = row['mp_id']
                                    tmp_mar_mh_mp_id_map[row['mh_seq']] = (row['mp_seq'], row['mp_id'])

                            for nt_seq in new_mar_mh_seqs_list:
                                _, aa_seq = trans_single_dna(nt_seq, tmp_mar_ref.get_cur_exon_pos())
                                tmp_mar_mp_seqs_set.add(aa_seq)
                                tmp_mar_mh_mp_id_map[nt_seq] = (aa_seq, None) # assign mp id later
                                
                            if len(tmp_mar_mp_seqs_set) > 0:
                                for aa_seq in tmp_mar_mp_seqs_set:
                                    if aa_seq not in mp_map:
                                        mp_max_id += 1
                                        mp_map[aa_seq] = mp_max_id
                            
                            for nt_seq, (aa_seq, mp_id) in tmp_mar_mh_mp_id_map.items():
                                if mp_id is None:
                                    tmp_mar_mh_mp_id_map[nt_seq] = (aa_seq, mp_map[aa_seq])
                        if len(new_mar_mh_seqs_list) != 0:
                            for nt_seq in new_mar_mh_seqs_list:
                                aa_seq, mp_id = tmp_mar_mh_mp_id_map[nt_seq]
                                tmp_mar_mp_seqs_list.append(aa_seq)
                                tmp_mar_mp_seqs_id_list.append(mp_id)
                            tmp_df = pd.DataFrame({'locus':[mar]*len(new_mar_mh_seqs_list),
                                                    'mh_label':[f'mh_{i + (max_id + 1 if start_1 else max_id)}' for i in range(len(new_mar_mh_seqs_list))],
                                                    'mh_seq':list(new_mar_mh_seqs_list),
                                                    'mh_id': [i + (max_id + 1 if start_1 else max_id) for i in range(len(new_mar_mh_seqs_list))],
                                                    'mp_label': [f'mp_{mp_id}' for mp_id in tmp_mar_mp_seqs_id_list],
                                                    'mp_seq': tmp_mar_mp_seqs_list,
                                                    'mp_id': tmp_mar_mp_seqs_id_list
                                                    })
                            mar_microhap_df = pd.concat([tmp_pre_mar_mt_df, tmp_df], ignore_index=True)
                            tmp_mar_ref.set_mar_microhap_df(mar_microhap_df)
                            tmp_mar_ref.set_cur_mar_microhap_df(mar_microhap_df[mar_microhap_df['mh_seq'].isin(cur_mar_mh_seqs_set)].reset_index(drop=True))
                            tmp_mar_ref.set_has_new_mh(True)
                        else:
                            tmp_mar_ref.set_mar_microhap_df(tmp_pre_mar_mt_df)
                            tmp_mar_ref.set_cur_mar_microhap_df(tmp_pre_mar_mt_df)
                            tmp_mar_ref.set_has_new_mh(False)
                            
                        if tmp_pre_mar_mt_df is not None:
                            tmp_mar_ref.set_pre_mar_microhap_df(tmp_pre_mar_mt_df)
                        else:
                            tmp_mar_ref.set_pre_mar_microhap_df(pd.DataFrame())
                    else:
                        tmp_mar_ref.set_mar_microhap_df(tmp_cur_mar_mh_df)
                        tmp_mar_ref.set_cur_mar_microhap_df(tmp_cur_mar_mh_df)
                    mh_lookup_table_dict[mar] = tmp_mar_ref.get_mar_microhap_df()
                    num_mars += 1
                    if num_mars % 10 == 0:
                        print_time(f"populate_microhap_dict Processed {num_mars} out of {len(metadata_class.get_ref_markers_list())} markers...")
                        if log_func is not None:
                            log_func(f"Processed {num_mars} out of {len(metadata_class.get_ref_markers_list())} marker for post microhap...")
            else:
                if log_func is not None:
                    log_func(f"Error: cannot find {mar} in reference markers!")
                modern_messagebox.showerror(None, "Marker Not Found", f"Error: cannot find {mar} in reference markers!")
                raise ValueError(f"Error: cannot find {mar} in reference markers!\n")
        self.output_mh_lookup_table(parameter_class, mh_lookup_table_dict)
        if log_func is not None:
            log_func("Finished populating post microhap dictionary.")
        print_time(f"finished to populate post microhap dictionary")
        return True

    def output_mh_lookup_table(self, parameter_class, mh_lookup_table_dict):
        mh_lookup_table = pd.concat(mh_lookup_table_dict.values(), ignore_index = True)
        if mh_lookup_table is not None and mh_lookup_table.shape[0] > 0:
            mh_lookup_table = mh_lookup_table.sort_values(['locus', 'mh_id']).reset_index(drop=True)
            mh_lookup_table.to_csv(os.path.join(parameter_class.get_post_microhap_output_dir(), "All_mt_lookup_table.txt"), sep = '\t', index = False)

    def perform_seq_alignment(self, parameter_class, log_func = None)->bool:
        print_time(f"Performing sequence alignment...")
        if log_func is not None:
            log_func("Performing sequence alignment...")
        num_mars = 0
        ctx = mp.get_context("spawn")
        with ProcessPoolExecutor(max_workers=parameter_class.get_thread(), mp_context=ctx) as executor:
            align_futures={}
            for mar, ref_mh_class in self.get_loc_ref_dict().items():
                is_include_pre_mh = parameter_class.get_include_pre_mh() # bool
                post_microhap_output_dir = parameter_class.get_post_microhap_output_dir()
                # mar, already have
                future = executor.submit(do_alignment2, ref_mh_class, is_include_pre_mh, post_microhap_output_dir)
                align_futures[future]=mar
            for future in as_completed(align_futures):
                mar = align_futures[future]
                try:
                    children_microtype_dict, cur_snp_pos_list, cur_aa_pos_list, dna_tree, aa_tree = future.result()
                    self.get_loc_ref_dict()[mar].set_children_microtype_dict(children_microtype_dict)
                    self.get_loc_ref_dict()[mar].generate_base_freq_df(dna=True)
                    self.get_loc_ref_dict()[mar].generate_base_freq_df(dna=False)
                    self.get_loc_ref_dict()[mar].set_tot_snp_pos(cur_snp_pos_list)
                    self.get_loc_ref_dict()[mar].set_tot_sap_pos(cur_aa_pos_list)
                    self.get_loc_ref_dict()[mar].set_cur_dna_tre(dna_tree)
                    self.get_loc_ref_dict()[mar].set_cur_aa_tre(aa_tree)
                    num_mars += 1
                    if num_mars % 10 == 0:
                        print_time(f"perform_seq_alignment Processed {num_mars} out of {len(self.get_loc_ref_dict())} markers...")
                        if log_func is not None:
                            log_func(f"Processed {num_mars} out of {len(self.get_loc_ref_dict())} markers for sequence alignment...")
                    #print(f"finished alignment for marker: {mar}")
                except Exception as exc:
                        print(f'Error while performing mh alignment for marker {mar}: {exc}')
                        if log_func is not None:
                            log_func(f"Error while performing mh alignment for marker {mar}: {exc}")
        print_time(f"finished sequence alignment...")
        if log_func is not None:
            log_func("Finished sequence alignment.")
        return True
    
    def populate_final_mar_mp_df_dict(self, parameter_class, metadata_class, log_func = None) -> bool:
        cur_mp_df = copy.deepcopy(metadata_class.get_cur_microhap_df())
        cur_mp_df.drop(columns=['sprop', 'mut', 'indel', 'id'], inplace=True)
        final_cur_mp_dict = {}
        final_cur_sim_mp_dict = {}
        futures = {}
        sub_markers = []
        com_markers = []
        ctx = mp.get_context("spawn")  # safest across OSes
        num_mars = 0
        with ProcessPoolExecutor( max_workers=parameter_class.get_thread(), mp_context=ctx) as executor:
            for mar, mar_value in self.get_loc_ref_dict().items():
                if not mar_value.get_has_exon():
                    continue
                mp_lookup_table_dict = (
                    mar_value.get_mar_microhap_df().set_index('mh_seq')['mp_seq'].to_dict()
                )
                mp_lookup_label_table_dict = (
                    mar_value.get_mar_microhap_df().set_index('mp_seq')['mp_label'].to_dict()
                )
                if not mp_lookup_table_dict:
                    continue
                cur_mar_mp_df = cur_mp_df[cur_mp_df['locus'] == mar].copy()
                if cur_mar_mp_df.empty:
                    continue
                cur_mar_mp_df['mp_seq'] = (cur_mar_mp_df['mh_seq'].map(mp_lookup_table_dict).fillna(''))
                cur_mar_mp_df['mp_label'] = (cur_mar_mp_df['mp_seq'].map(mp_lookup_label_table_dict).fillna('-9'))
                cur_mar_mp_df['allele'] = cur_mar_mp_df['mp_label']
                if cur_mar_mp_df.empty:
                    continue
                # 🔑 serialize explicitly
                #cur_mar_mp_df.drop(columns=['mh_seq'], inplace=True)
                records = cur_mar_mp_df.to_dict(orient='records')
                mar_combo_mt = self.get_loc_ref_dict().get(mar, None).get_children_microtype_dict()
                if mar_combo_mt is None:
                    continue
                future = executor.submit(populate_each_mar_mp_dict, mar, records, mar_combo_mt)
                futures[future] = mar
                sub_markers.append(mar)
            for future in as_completed(futures):
                mar = futures[future]
                try:
                    final_sam_cur_mp_dict, final_sam_cur_mp_sim_dict = future.result()
                    self.get_loc_ref_dict()[mar].set_final_mar_cur_micropep_nested_dict(final_sam_cur_mp_dict)
                    final_cur_mp_dict[mar] = pd.concat(final_sam_cur_mp_dict.values(), ignore_index=True)
                    self.get_loc_ref_dict()[mar].set_final_mar_cur_sim_micropep_nested_dict(final_sam_cur_mp_sim_dict)
                    final_cur_sim_mp_dict[mar] = pd.concat(final_sam_cur_mp_sim_dict.values(), ignore_index=True)
                    com_markers.append(mar)
                    num_mars += 1
                    if num_mars % 10 == 0:
                        print_time(f"pupulate_final_mar_mp_df_dict Processed {num_mars} out of {len(self.get_loc_ref_dict())} markers for final microhap...")
                        if log_func is not None:
                            log_func(f"Processed {num_mars} out of {len(self.get_loc_ref_dict())} markers for final microhap...")
                except Exception as e:
                    print(f"Error processing marker {mar}: {e}", flush=True)
                    if log_func is not None:
                        log_func(f"Error processing marker {mar}: {e}")
                    traceback.print_exc()
                    executor.shutdown(wait=False, cancel_futures=True)
                    raise
        self.output_final_micropep_table(parameter_class, final_cur_mp_dict, final_cur_sim_mp_dict)
        print(f"Total markers submitted: {len(sub_markers)}, completed: {len(com_markers)} for final microhap")
        if log_func is not None:
            log_func(f"Total markers submitted: {len(sub_markers)}, completed: {len(com_markers)} for final microhap")
        return True    
                
    def populate_final_mar_mh_df_dict(self, parameter_class, metadata_class, log_func = None) -> bool:
        print_time("starting populate_final_mar_mh_df_dict")
        if log_func is not None:
            log_func("Populating final microhap DataFrame dictionary...")
        cur_mh_df = metadata_class.get_cur_microhap_df()
        final_cur_mh_dict = {}
        final_cur_sim_mh_dict = {}
        futures = {}
        sub_markers = []
        com_markers = []
        ctx = mp.get_context("spawn")  # safest across OSes
        num_mars = 0
        with ProcessPoolExecutor( max_workers=parameter_class.get_thread(), mp_context=ctx) as executor:
            for mar, mar_value in self.get_loc_ref_dict().items():
                mh_lookup_table_dict = (
                    mar_value.get_mar_microhap_df()
                    .set_index('mh_seq')['mh_label']
                    .to_dict()
                )
                if not mh_lookup_table_dict:
                    continue
                cur_mar_mh_df = cur_mh_df[cur_mh_df['locus'] == mar].copy()
                if cur_mar_mh_df.empty:
                    continue
                cur_mar_mh_df['allele'] = (cur_mar_mh_df['mh_seq'].map(mh_lookup_table_dict).fillna('-9'))
                # 🔑 serialize explicitly, must convert to records for multiple threading
                records = cur_mar_mh_df.to_dict(orient='records')
                    
                future = executor.submit(populate_each_mar_mh_dict, mar, records)
                futures[future] = mar
                sub_markers.append(mar)
            for future in as_completed(futures):
                mar = futures[future]
                try:
                    final_sam_cur_mh_dict, final_sam_cur_mh_sim_dict = future.result()
                    self.get_loc_ref_dict()[mar].set_final_mar_cur_microhap_nested_dict(final_sam_cur_mh_dict)
                    final_cur_mh_dict[mar] = pd.concat(final_sam_cur_mh_dict.values(), ignore_index=True)
                    self.get_loc_ref_dict()[mar].set_final_mar_cur_sim_microhap_nested_dict(final_sam_cur_mh_sim_dict)
                    final_cur_sim_mh_dict[mar] = pd.concat(final_sam_cur_mh_sim_dict.values(), ignore_index=True)
                    com_markers.append(mar)
                    num_mars += 1
                    if num_mars % 10 == 0:
                        print_time(f"populate_final_mar_mh_df_dict Processed {num_mars} out of {len(self.get_loc_ref_dict())} markers for final microhap...")
                        if log_func is not None:
                            log_func(f"Processed {num_mars} out of {len(self.get_loc_ref_dict())} markers for final microhap...")
                except Exception as e:
                    print(f"Error processing marker {mar}: {e}", flush=True)
                    if log_func is not None:
                        log_func(f"Error processing marker {mar}: {e}")
                    traceback.print_exc()
                    executor.shutdown(wait=False, cancel_futures=True)
                    raise
        self.output_final_microhap_table(parameter_class, final_cur_mh_dict, final_cur_sim_mh_dict)
        print(f"Total markers submitted: {len(sub_markers)}, completed: {len(com_markers)} for final microhap")
        if log_func is not None:
            log_func(f"Total markers submitted: {len(sub_markers)}, completed: {len(com_markers)} for final microhap")
        return True
    
    def output_final_micropep_table(self, parameter_class, final_cur_mp_dict, final_cur_sim_mp_dict):
        if final_cur_mp_dict.values():
            self._final_micropep_df = pd.concat(final_cur_mp_dict.values(), ignore_index = True)
            self._final_micropep_df = self._final_micropep_df.sort_values(by=['sample', 'locus']).reset_index(drop=True)
        else:
            self._final_micropep_df = pd.DataFrame()
        if self._final_micropep_df.shape[0] > 0:
            self._final_micropep_df.to_csv(os.path.join(parameter_class.get_post_microhap_output_dir(), "All_cur_mp_table.txt"), sep = '\t', index = False)

        final_cur_sim_mp_df_list = []
        for i, (mar, df) in enumerate(final_cur_sim_mp_dict.items()):
            if i == 0:
                final_cur_sim_mp_df_list.append(df)
            else:
                final_cur_sim_mp_df_list.append(df.drop(columns='sample'))
        if final_cur_sim_mp_df_list:
            self._final_micropep_df_simple = pd.concat(final_cur_sim_mp_df_list, axis = 1)
        else:
            self._final_micropep_df_simple = pd.DataFrame()
        if self._final_micropep_df_simple.shape[0] > 0:
            self._final_micropep_df_simple.to_csv(os.path.join(parameter_class.get_post_microhap_output_dir(), "All_cur_mp_sim_table.txt"), sep = '\t', index = False)
    
    def output_final_microhap_table(self, parameter_class, final_cur_mh_dict, final_cur_sim_mh_dict):
        if final_cur_mh_dict.values():
            self._final_microhap_df = pd.concat(final_cur_mh_dict.values(), ignore_index = True)
            self._final_microhap_df = self._final_microhap_df.sort_values(by=['sample', 'locus']).reset_index(drop=True)
        else:
            self._final_microhap_df = pd.DataFrame()
        if self._final_microhap_df.shape[0] > 0:
            self._final_microhap_df.to_csv(os.path.join(parameter_class.get_post_microhap_output_dir(), "All_cur_mh_table.txt"), sep = '\t', index = False)

        final_cur_sim_mh_df_list = []
        for i, (mar, df) in enumerate(final_cur_sim_mh_dict.items()):
            if i == 0:
                final_cur_sim_mh_df_list.append(df)
            else:
                final_cur_sim_mh_df_list.append(df.drop(columns='sample'))
        if final_cur_sim_mh_df_list:
            self._final_microhap_df_simple = pd.concat(final_cur_sim_mh_df_list, axis = 1)
        else:
            self._final_microhap_df_simple = pd.DataFrame()
        if self._final_microhap_df_simple.shape[0] > 0:
            self._final_microhap_df_simple.to_csv(os.path.join(parameter_class.get_post_microhap_output_dir(), "All_cur_mh_sim_table.txt"), sep = '\t', index = False)

    def print(self):
        for mar, mar_value in self.get_loc_ref_dict().items():
            print(f"Marker: {mar}")
            mar_value.print_ref()