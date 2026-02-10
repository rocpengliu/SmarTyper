import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import multiprocessing as mp
from ..utils.utils_common import print_time
import copy
from ..utils.utils_func import populate_mar_sam_microhap, populate_each_mar_mh_dict
from ..utils.utils_common import print_time, thread_lock
from ..utils.utils_alignment import do_alignment
from ..utils import modern_messagebox
import pdb
import traceback
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
            modern_messagebox.showerror(None, "File Not Found", f"{fpath} is not a file")
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

    def populate_one_microhap_dict(self, parameter_class, metadata_class, cur = True, log_func = None)->bool:
        n_threads = parameter_class.get_thread()
        ctx = mp.get_context("spawn")
        print_time(f"starting to populate microhap dictionary for {cur}")
        if log_func is not None:
            log_func(f"Populating {'current' if cur else 'pre'} microhap dictionary...")
        parent_mh_df = metadata_class.get_cur_microhap_df() if cur else metadata_class.get_pre_microhap_df()
        if parent_mh_df is not None and parent_mh_df.shape[0] > 0:
            markers = sorted(parent_mh_df['Locus'].unique())
            samples = sorted(parent_mh_df['Sample'].unique()) if cur else []
            mar_df_dict = {}
            num_mars = 0
            with ProcessPoolExecutor(max_workers=n_threads, mp_context=ctx) as executor:
                futures={executor.submit(populate_mar_sam_microhap,
                                         mar, 
                                         samples, 
                                         parent_mh_df[parent_mh_df['Locus']==mar].reset_index(drop=True), 
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
        mh_lookup_table_dir = {}
        for mar in metadata_class.get_ref_markers_list():
            tmp_mar_ref = self.get_loc_ref_dict().get(mar, None)
            if tmp_mar_ref is not None:
                tmp_cur_mar_mh_df = copy.deepcopy(self.get_cur_mar_microhap_dict().get(mar, None))
                if tmp_cur_mar_mh_df is not None:
                    if parameter_class.get_has_pre_mh():
                        tmp_pre_mar_mh_df = copy.deepcopy(self.get_pre_mar_microhap_dict().get(mar, None))
                        pre_mar_mh_seqs_set = set()
                        max_id = 0
                        start_1 = False
                        if tmp_pre_mar_mh_df is not None:
                            pre_mar_mh_seqs_set = set(tmp_pre_mar_mh_df['Seq'].unique())
                            max_id = tmp_pre_mar_mh_df['ID'].max()
                            start_1 = True
                        cur_mar_mh_seqs_set = set(tmp_cur_mar_mh_df['Seq'].unique())
                        new_mar_mh_seqs_list = sorted(cur_mar_mh_seqs_set.difference(pre_mar_mh_seqs_set))
                        if len(new_mar_mh_seqs_list) != 0:
                            tmp_df = pd.DataFrame({'Locus':[mar]*len(new_mar_mh_seqs_list),
                                                    'Label':[f'mh_{i + (max_id + 1 if start_1 else max_id)}' for i in range(len(new_mar_mh_seqs_list))],
                                                    'Seq':list(new_mar_mh_seqs_list),
                                                    'ID': [i + (max_id + 1 if start_1 else max_id) for i in range(len(new_mar_mh_seqs_list))]
                                                    })
                            mar_microhap_df = pd.concat([tmp_pre_mar_mh_df, tmp_df], ignore_index=True)
                            tmp_mar_ref.set_mar_microhap_df(mar_microhap_df)
                            tmp_mar_ref.set_cur_mar_microhap_df(mar_microhap_df[mar_microhap_df['Seq'].isin(cur_mar_mh_seqs_set)].reset_index(drop=True))
                            tmp_mar_ref.set_has_new_mh(True)
                        else:
                            tmp_mar_ref.set_mar_microhap_df(tmp_pre_mar_mh_df)
                            tmp_mar_ref.set_cur_mar_microhap_df(tmp_pre_mar_mh_df)
                            tmp_mar_ref.set_has_new_mh(False)
                            
                        if tmp_pre_mar_mh_df is not None:
                            tmp_mar_ref.set_pre_mar_microhap_df(tmp_pre_mar_mh_df)
                        else:
                            tmp_mar_ref.set_pre_mar_microhap_df(pd.DataFrame())
                    else:
                        tmp_mar_ref.set_mar_microhap_df(tmp_cur_mar_mh_df)
                        tmp_mar_ref.set_cur_mar_microhap_df(tmp_cur_mar_mh_df)
                    mh_lookup_table_dir[mar] = tmp_mar_ref.get_mar_microhap_df()
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
        self.output_mh_lookup_table(parameter_class, mh_lookup_table_dir)
        if log_func is not None:
            log_func("Finished populating post microhap dictionary.")
        print_time(f"finished to populate post microhap dictionary")
        return True

    def output_mh_lookup_table(self, parameter_class, mh_lookup_table_dir):
        mh_lookup_table = pd.concat(mh_lookup_table_dir.values(), ignore_index = True)
        if mh_lookup_table is not None and mh_lookup_table.shape[0] > 0:
            mh_lookup_table = mh_lookup_table.sort_values(['Locus', 'ID']).reset_index(drop=True)
            mh_lookup_table.to_csv(os.path.join(parameter_class.get_post_microhap_output_dir(), "All_mh_lookup_table.txt"), sep = '\t', index = False)
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
                future = executor.submit(do_alignment, ref_mh_class, is_include_pre_mh, post_microhap_output_dir)
                align_futures[future]=mar
            for future in as_completed(align_futures):
                mar = align_futures[future]
                try:
                    children_microtype_dict = future.result()
                    self.get_loc_ref_dict()[mar].set_children_microtype_dict(children_microtype_dict)
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
                    .set_index('Seq')['Label']
                    .to_dict()
                )
                if not mh_lookup_table_dict:
                    continue
                cur_mar_mh_df = cur_mh_df[cur_mh_df['Locus'] == mar].copy()
                if cur_mar_mh_df.empty:
                    continue
                cur_mar_mh_df['Allele'] = (cur_mar_mh_df['Sequence'].map(mh_lookup_table_dict).fillna('-9'))
                # 🔑 serialize explicitly
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

    
    # def populate_final_mar_mh_df_dict2(self, parameter_class, metadata_class)->bool:
    #     print_time(f"staring to populate_final_mar_mh_df_dict")
    #     cur_mh_df = metadata_class.get_cur_microhap_df()
    #     final_cur_mh_dict = {}
    #     final_cur_sim_mh_dict = {}
    #     num_mars = 0
    #     for mar, mar_value in self.get_loc_ref_dict().items():
    #         try:             
    #             mh_lookup_table_dict = mar_value.get_mar_microhap_df().set_index('Seq')['Label'].to_dict()
    #             if mh_lookup_table_dict is None or not mh_lookup_table_dict:
    #                 continue
    #             cur_mar_mh_df = cur_mh_df[cur_mh_df['Locus'] == mar].reset_index(drop=True).copy()
    #             if cur_mar_mh_df is None or len(cur_mar_mh_df) == 0:
    #                 continue
    #             cur_mar_mh_df['Allele']=cur_mar_mh_df['Sequence'].map(mh_lookup_table_dict).fillna('-9')
                
    #             final_sam_cur_mh_dict, final_sam_cur_mh_sim_dict = populate_each_mar_mh_dict(mar, cur_mar_mh_df)
                
    #             self.get_loc_ref_dict().get(mar).set_final_mar_cur_microhap_nested_dict(final_sam_cur_mh_dict)
    #             final_cur_mh_dict[mar] = pd.concat(final_sam_cur_mh_dict.values(), ignore_index = True)
    #             self.get_loc_ref_dict().get(mar).set_final_mar_cur_sim_microhap_nested_dict(final_sam_cur_mh_sim_dict)
    #             final_cur_sim_mh_dict[mar] = pd.concat(final_sam_cur_mh_sim_dict.values(), ignore_index = True)
    #             num_mars += 1
    #             if num_mars % 10 == 0:
    #                 print_time(f"populate_final_mar_mh_df_dict Processed {num_mars} out of {len(self.get_loc_ref_dict())} markers...")
    #         except Exception as e:
    #             print(f"An error occurred while processing {mar}: {e}")
    #             import traceback
    #             traceback.print_exc()
        
    #     self.output_final_microhap_table(parameter_class, final_cur_mh_dict, final_cur_sim_mh_dict)
    #     print_time(f"finished to populate_final_mar_mh_df_dict")
    #     return True
    
    def output_final_microhap_table(self, parameter_class, final_cur_mh_dict, final_cur_sim_mh_dict):
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

    def print(self):
        for mar, mar_value in self.get_loc_ref_dict().items():
            print(f"Marker: {mar}")
            mar_value.print_ref()