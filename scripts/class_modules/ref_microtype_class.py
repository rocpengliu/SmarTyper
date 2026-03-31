import warnings
warnings.filterwarnings("ignore", message="mkl-service")

from ..utils import modern_messagebox
import pandas as pd
from typing import Dict
from ..utils.utils_func import get_exon_start_end_pos_from_dna_exon_pos, trans_single_dna, extract_sap_pos_from_snp_pos_list
from ..utils.utils_common import print_time
import pdb
from .microtype_class import ComboMicroType

class RefMicroType:
    def __init__(self) -> None:
        self._locus=""
        self._fprimer=""
        self._rprimer=""
        self._triml=0
        self._trimr=0
        self._ori_dna_ref = "" #paired with _ori_aa_ref if it has exons
        self._cur_dna_ref = "" #trimmed ones, and paired with _cur_aa_ref if it has exons,
        self._ori_cds_ref = "" # paired with _ori_aa_ref if it has exons but without introns
        self._cur_cds_ref = "" #trimmed ones, and paired with _cur_aa_ref if it has exons, but without introns
        self._ori_snp_pos=[]
        self._cur_snp_pos=[]
        self._tot_snp_pos=[]
        self._has_exon = False
        self._ori_exon_pos=[]
        self._ori_aa_exon_pos=[]
        self._cur_exon_pos=[]
        self._cur_aa_exon_pos=[]
        self._ori_sap_pos=[]
        self._cur_sap_pos=[]
        self._tot_sap_pos=[]
        self._ori_aa_ref = ""
        self._cur_aa_ref = ""
        self._children_microtype_dict:Dict[str, ComboMicroType] = {} # key is mh_seq value is ComboMicroType
        self._cur_children_microtype_dict:Dict[str, ComboMicroType] = {} # key is mh_seq value is ComboMicroType
        self._cur_mar_microhap_df = pd.DataFrame()
        self._pre_mar_microhap_df = pd.DataFrame()
        self._mar_microhap_df = pd.DataFrame() # this is the lookup table and is combined the cur and pre lookuptables
        self._is_mt = False
        self._cur_dna_tre = None #phylo tree for dna
        self._cur_aa_tre = None #phylo tree for aa
        
        self._final_mar_cur_microhap_nested_dict = {} # nested_dict{mar : {sample:dataframe}}
        self._final_mar_pre_microhap_nested_dict = {} #nested_dict{mar : {sample:dataframe}}#this should be idential as the metadata.pre_microhap_df, here is just for the convenient for other analysis
        self._final_mar_cur_sim_microhap_nested_dict = {}#for the sample X allel table  sample, mar_allele1, mar_allele2
        self._final_mar_pre_sim_microhap_nested_dict = {}
        
        self._final_mar_cur_microhap_nested_dict = {}
        self._final_mar_cur_sim_microhap_nested_dict = {}
        
        self._final_mar_cur_micropep_nested_dict = {}
        self._final_mar_cur_sim_micropep_nested_dict = {}
        self._dna_base_freq_df = pd.DataFrame()
        self._aa_base_freq_df = pd.DataFrame()
    
    def get_locus(self):
        return self._locus
    def set_locus(self, locus):
        try:
            if isinstance(locus, str):
                self._locus = locus
            else:
                raise ValueError("locus must be a string")
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))
    def get_fprimer(self):
        return self._fprimer
    def set_fprimer(self, fprimer):
        try:
            if isinstance(fprimer, str):
                self._fprimer = fprimer
            else:
                raise ValueError("fprimer must be a string")
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))
    def get_rprimer(self):
        return self._rprimer
    def set_rprimer(self, rprimer):
        try:
            if isinstance(rprimer, str):
                self._rprimer = rprimer
            else:
                raise ValueError("rprimer must be a string")
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))
    def get_triml(self):
        return self._triml
    def set_triml(self, triml): 
        try:
            if isinstance(triml, int):
                self._triml = triml
            else:
                raise ValueError("triml must be an integer")
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))
    def get_trimr(self):
        return self._trimr
    def set_trimr(self, trimr):
        try:
            if isinstance(trimr, int):
                self._trimr = trimr
            else:
                raise ValueError("trimr must be an integer")
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))
    def get_ori_dna_ref(self):
        return self._ori_dna_ref
    def set_ori_dna_ref(self, ori_dna_ref):
        try:
            if isinstance(ori_dna_ref, str):
                self._ori_dna_ref = ori_dna_ref
            else:
                raise ValueError("ori_dna_ref must be a string")
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))
    def get_cur_dna_ref(self):
        return self._cur_dna_ref
    def set_cur_dna_ref(self, cur_dna_ref):
        try:
            if isinstance(cur_dna_ref, str):
                self._cur_dna_ref = cur_dna_ref
            else:
                raise ValueError("cur_dna_ref must be a string")
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))
    def get_ori_snp_pos(self):
        return self._ori_snp_pos
    def set_ori_snp_pos(self, ori_snp_pos):
        try:
            self._ori_snp_pos = sorted(ori_snp_pos)
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))
    def get_cur_snp_pos(self):
        return self._cur_snp_pos
    def set_cur_snp_pos(self, cur_snp_pos):
        try:
            self._cur_snp_pos = sorted(cur_snp_pos)
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))
    def get_has_exon(self):
        return self._has_exon
    def set_has_exon(self, has_exon):
        try:
            if isinstance(has_exon, bool):
                self._has_exon = has_exon
            else:
                raise ValueError("has_exon must be a boolean")
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))
    def get_ori_exon_pos(self):
        return self._ori_exon_pos
    def set_ori_exon_pos(self, ori_exon_pos):
        try:
            self._ori_exon_pos = ori_exon_pos
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))
    def get_cur_exon_pos(self):
        return self._cur_exon_pos
    def set_cur_exon_pos(self, cur_exon_pos):
        try:
            self._cur_exon_pos = cur_exon_pos
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))
    
    def get_ori_aa_exon_pos(self):
        return self._ori_aa_exon_pos
    def set_ori_aa_exon_pos(self, ori_aa_exon_pos):
        try:
            self._ori_aa_exon_pos = ori_aa_exon_pos
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))
    def get_cur_aa_exon_pos(self):
        return self._cur_aa_exon_pos
    def set_cur_aa_exon_pos(self, cur_aa_exon_pos):
        try:
            self._cur_aa_exon_pos = cur_aa_exon_pos
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))

    def get_ori_sap_pos(self):
        return self._ori_sap_pos
    def set_ori_sap_pos(self, ori_sap_pos):
        try:
            self._ori_sap_pos = ori_sap_pos
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))
    def get_cur_sap_pos(self):
        return self._cur_sap_pos
    def set_cur_sap_pos(self, cur_sap_pos):
        try:
            self._cur_sap_pos = cur_sap_pos
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))
    def get_children_microtype_dict(self):
        return self._children_microtype_dict
    def set_children_microtype_dict(self, children_microtype_dict):
        try:
            if isinstance(children_microtype_dict, dict):
                self._children_microtype_dict = children_microtype_dict
            else:
                raise ValueError("children_microtype_dict must be a dictionary")
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))
    def get_cur_children_microtype_dict(self):
        return self._cur_children_microtype_dict
    def set_cur_children_microtype_dict(self, cur_children_microtype_dict):
        try:
            if isinstance(cur_children_microtype_dict, dict):
                self._cur_children_microtype_dict = cur_children_microtype_dict
            else:
                raise ValueError("cur_children_microtype_dict must be a dictionary")
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))
    def get_cur_mar_microhap_df(self):
        return self._cur_mar_microhap_df
    def set_cur_mar_microhap_df(self, cur_mar_microhap_df):
        try:
            if isinstance(cur_mar_microhap_df, pd.DataFrame):
                self._cur_mar_microhap_df = cur_mar_microhap_df
            else:
                raise ValueError("cur_mar_microhap_df must be a pandas DataFrame")
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))
    def get_pre_mar_microhap_df(self):
        return self._pre_mar_microhap_df
    def set_pre_mar_microhap_df(self, pre_mar_microhap_df):
        try:
            if isinstance(pre_mar_microhap_df, pd.DataFrame):
                self._pre_mar_microhap_df = pre_mar_microhap_df
            else:
                raise ValueError("pre_mar_microhap_df must be a pandas DataFrame")
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))
    def get_mar_microhap_df(self):
        return self._mar_microhap_df
    def set_mar_microhap_df(self, mar_microhap_df):
        try:
            if isinstance(mar_microhap_df, pd.DataFrame):
                self._mar_microhap_df = mar_microhap_df
            else:
                raise ValueError("mar_microhap_df must be a pandas DataFrame")
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))
            
    def get_is_mt(self):
        return self._is_mt
    def set_is_mt(self, is_mt):
        try:
            if isinstance(is_mt, bool):
                self._is_mt = is_mt
            else:
                raise ValueError("is_mt must be a boolean")
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))
    def get_tot_snp_pos(self):
        return self._tot_snp_pos
    def set_tot_snp_pos(self, tot_snp_pos):
        try:
            self._tot_snp_pos = sorted(tot_snp_pos)
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))
    def get_tot_sap_pos(self):
        return self._tot_sap_pos
    def set_tot_sap_pos(self, tot_sap_pos):
        try:
            self._tot_sap_pos = tot_sap_pos
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))
    def get_ori_aa_ref(self):
        return self._ori_aa_ref
    def set_ori_aa_ref(self, ori_aa_ref):
        try:
            if isinstance(ori_aa_ref, str):
                self._ori_aa_ref = ori_aa_ref
            else:
                raise ValueError("ori_aa_ref must be a string")
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))
    def get_cur_aa_ref(self):
        return self._cur_aa_ref
    def set_cur_aa_ref(self, cur_aa_ref):
        try:
            if isinstance(cur_aa_ref, str):
                self._cur_aa_ref = cur_aa_ref
            else:
                raise ValueError("cur_aa_ref must be a string")
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))
    
    def get_cur_cds_ref(self):
        return self._cur_cds_ref
    def set_cur_cds_ref(self, cur_cds_ref):
        try:
            if isinstance(cur_cds_ref, str):
                self._cur_cds_ref = cur_cds_ref
            else:
                raise ValueError("cur_cds_ref must be a string")
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))
    def get_ori_cds_ref(self):
        return self._ori_cds_ref
    def set_ori_cds_ref(self, ori_cds_ref):
        try:
            if isinstance(ori_cds_ref, str):
                self._ori_cds_ref = ori_cds_ref
            else:
                raise ValueError("ori_cds_ref must be a string")
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))
    
    def get_cur_dna_tre(self):
        return self._cur_dna_tre
    def set_cur_dna_tre(self, cur_dna_tre):
        self._cur_dna_tre = cur_dna_tre
    def get_cur_aa_tre(self):
        return self._cur_aa_tre
    def set_cur_aa_tre(self, cur_aa_tre):
        self._cur_aa_tre = cur_aa_tre
        
    def get_final_mar_cur_microhap_nested_dict(self):
        return self._final_mar_cur_microhap_nested_dict
    def set_final_mar_cur_microhap_nested_dict(self, final_mar_cur_microhap_nested_dict):
        self._final_mar_cur_microhap_nested_dict = final_mar_cur_microhap_nested_dict
    def get_final_mar_pre_microhap_nested_dict(self):
        return self._final_mar_pre_microhap_nested_dict
    def set_final_mar_pre_microhap_nested_dict(self, final_mar_pre_microhap_nested_dict):
        self._final_mar_pre_microhap_nested_dict = final_mar_pre_microhap_nested_dict
    def get_final_mar_cur_sim_microhap_nested_dict(self):
        return self._final_mar_cur_sim_microhap_nested_dict
    def set_final_mar_cur_sim_microhap_nested_dict(self, final_mar_cur_sim_microhap_nested_dict):
        self._final_mar_cur_sim_microhap_nested_dict = final_mar_cur_sim_microhap_nested_dict
    def get_final_mar_pre_sim_microhap_nested_dict(self):
        return self._final_mar_pre_sim_microhap_nested_dict
    def set_final_mar_pre_sim_microhap_nested_dict(self, final_mar_pre_sim_microhap_nested_dict):
        self._final_mar_pre_sim_microhap_nested_dict = final_mar_pre_sim_microhap_nested_dict
        
    def get_final_mar_cur_micropep_nested_dict(self):
        return self._final_mar_cur_micropep_nested_dict
    def set_final_mar_cur_micropep_nested_dict(self, final_mar_cur_micropep_nested_dict):
        self._final_mar_cur_micropep_nested_dict = final_mar_cur_micropep_nested_dict
    def get_final_mar_cur_sim_micropep_nested_dict(self):
        return self._final_mar_cur_sim_micropep_nested_dict
    def set_final_mar_cur_sim_micropep_nested_dict(self, final_mar_cur_sim_micropep_nested_dict):
        self._final_mar_cur_sim_micropep_nested_dict = final_mar_cur_sim_micropep_nested_dict
        
    def get_dna_base_freq_df(self):
        return self._dna_base_freq_df
    def set_dna_base_freq_df(self, dna_base_freq_df):
        try:
            if isinstance(dna_base_freq_df, pd.DataFrame):
                self._dna_base_freq_df = dna_base_freq_df
            else:
                raise ValueError("dna_base_freq_df must be a pandas DataFrame")
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))
    def get_aa_base_freq_df(self):
        return self._aa_base_freq_df
    def set_aa_base_freq_df(self, aa_base_freq_df):
        try:
            if isinstance(aa_base_freq_df, pd.DataFrame):
                self._aa_base_freq_df = aa_base_freq_df
            else:
                raise ValueError("aa_base_freq_df must be a pandas DataFrame")
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))

    def populate_ref_mt(self):
        self.set_tot_snp_pos(self.get_cur_snp_pos())
        if not self.get_has_exon():
            return
        self.set_ori_aa_exon_pos(get_exon_start_end_pos_from_dna_exon_pos(self.get_ori_exon_pos()))
        self.set_cur_aa_exon_pos(get_exon_start_end_pos_from_dna_exon_pos(self.get_cur_exon_pos()))
        ori_cds_seq, ori_aa_seq = trans_single_dna(self.get_ori_dna_ref(), self.get_ori_exon_pos())
        self.set_ori_cds_ref(ori_cds_seq)
        self.set_ori_aa_ref(ori_aa_seq)
        cur_cds_seq, cur_aa_seq = trans_single_dna(self.get_cur_dna_ref(), self.get_cur_exon_pos())
        self.set_cur_cds_ref(cur_cds_seq)
        self.set_cur_aa_ref(cur_aa_seq)
        self.set_ori_sap_pos(extract_sap_pos_from_snp_pos_list(self.get_ori_snp_pos(), self.get_ori_exon_pos()))
        self.set_cur_sap_pos(self.get_ori_sap_pos())
        if self.get_triml() != 0 or self.get_trimr() != 0:
            self.set_cur_sap_pos(extract_sap_pos_from_snp_pos_list(self.get_cur_snp_pos(), self.get_cur_exon_pos()))
        self.set_tot_sap_pos(self.get_cur_sap_pos())
    
    def generate_base_freq_df(self, dna=True):
        #pdb.set_trace()
        seq_set = set()
        for _, combo_mt in self.get_children_microtype_dict().items():
            if dna:
                seq = combo_mt.get_microhap().get_seq()
                if seq and not combo_mt.get_microhap().get_is_indel():
                    seq_set.add(seq)
            else:
                seq = combo_mt.get_micropep().get_seq()
                if seq and not combo_mt.get_micropep().get_is_indel():
                    seq_set.add(seq)
        if len(seq_set) == 0:
            return
        seq_df = pd.DataFrame([list(sequ) for sequ in seq_set])
        freq_data = []
        # Logomaker expects one-character symbol columns (e.g. A/C/G/T),
        # and rows corresponding to sequence positions.
        symbol_order = sorted({str(sym) for sym in seq_df.values.flatten() if pd.notna(sym) and str(sym) != ""})
        for col in seq_df.columns:
            counts = seq_df[col].astype(str).value_counts(normalize=True).reindex(symbol_order, fill_value=0)
            freq_data.append(counts)
        base_freq_df = pd.concat(freq_data, axis=1).T
        base_freq_df.columns = symbol_order
        if dna:
            self.set_dna_base_freq_df(base_freq_df)
        else:
            self.set_aa_base_freq_df(base_freq_df)
    
    def get_longest_label_nm(self, dna=True):
        longest_label = ""
        for _, combo_mt in self.get_children_microtype_dict().items():
            if dna:
                if len(combo_mt.get_microhap().get_mt()) > len(longest_label):
                    longest_label = combo_mt.get_microhap().get_mt()
            else:
                if combo_mt.get_has_mp():
                    if len(combo_mt.get_micropep().get_mt()) > len(longest_label):
                        longest_label = combo_mt.get_micropep().get_mt()
        return longest_label
            
# class RefMicrotype:
#     def __init__(self) -> None:
#         self._locus=""
#         self._fprimer=""
#         self._rprimer=""
#         self._triml=0
#         self._trimr=0
#         self._snppos=[]
#         self._orisnppos=[]
#         self._newsnppos=[] #//for snp output, if homo, should be empty
#         self._sappos=[] # sap is single aa polymorphism, this is only valid for _aa_ref, see _aa_ref
#         self._codingpos=[] # must start with 0, if the full length should be 0:(len-1); but after the spliting, it should become 0:len 
#                             #"2:20, 30:50, 50:70, 80:90, 100:120|2:20, 80:90, 100:120|50:70, 80:90, 100:120" to [[(2, 20), (30, 50), (50,70), (80,90), (100,120)], [(2, 20), (70, 80)], [(3, 30), (90, 120)]]
#                             #the first list must be the most exons and the rest must be a subset of the first list of exons for eukaryotic
#                             #while for the prokayotic, each list of exons is a independent one.
        
#         #####need to remove
#         self._overlapped_gene = False #assume exons in eukaryotic are not overlapping while prokaryotic are overlapping
#         self._splicer_exon_list_dict = {} # [[(0, 3), (5, 8), (12, 15), (20, 21)], [(0, 3), (5, 8)], [(12, 15), (20, 21)], [(5, 8), (12, 15), (20, 21)]]
#                                         #{'splicer_0': [0, 1, 2, 3], 'splicer_1': [0, 1], 'splicer_2': [2, 3], 'splicer_3': [1, 2, 3]}
#                                         #this is true if it is not overlapped gene, this is used to map the aaseq seq codingpos
#         ############
        
#         self._exon_list=[] # [(0,3), (5, 8), (12, 15), (20, 21)]  ############new
        
        
#         self._aa_codingpos=[] # for aaseqs
#         self._ori_dna_ref=""
#         self._dna_ref=""
#         self._aa_ref = "" # only for the non overlapped genes with splicers, and this is the longest possible exon list, the splicer_0, same as dna_ref.
        
#         self._ref_microtype_dict:Dict[str, CompreMicrotypeClass] = {} #key is splicer_0 value is CompreMicrotypeClass
        
#         self._cur_ref_microtype_dict:Dict[str, CompreMicrotypeClass] = {} #only for cur_mh
        
#         self._has_splicer = False
#         self._begin_with_splicer0 = False # only if _has_splicer = True and if the first splicer is  the full length of the ref, 
#         self._children_microtype_dict:Dict[str, CompreMicrotypeClass] = {} # key is splicer_0 value is CompreMicrotypeClass
#         self._cur_children_microtype_dict:Dict[str, CompreMicrotypeClass] = {} # only for cur_mh
        
#         self._mar_microhap_df = pd.DataFrame() #final df with columns=['locus', 'label', 'seq'] for all the microhap lookup table
#         self._pre_mar_microhap_df = pd.DataFrame() #fprecolumns=['locus', 'label', 'seq'] for all the microhap lookup table
#         self._cur_mar_microhap_df = pd.DataFrame()
        
#         self._final_mar_cur_microhap_nested_dict = {} # nested_dict{mar : {sample:dataframe}}
#         self._final_mar_pre_microhap_nested_dict = {} #nested_dict{mar : {sample:dataframe}}#this should be idential as the metadata.pre_microhap_df, here is just for the convenient for other analysis
#         self._final_mar_cur_sim_microhap_nested_dict = {}#for the sample X allel table  sample, mar_allele1, mar_allele2
#         self._final_mar_pre_sim_microhap_nested_dict = {}
        
#         self._has_new_mh = False
    
#     def get_new_snp_pos(self):
#         return self._newsnppos
#     def set_new_snp_pos(self, newsnppos):
#         try:
#             self._newsnppos = sorted(newsnppos)
#         except ValueError as e:
#             modern_messagebox.showerror(None, "Invalid Input", str(e))
    
#     def get_sappos(self):
#         return self._sappos
    
#     def set_sappos(self, sappos):
#         self._sappos = sappos
        
#     def get_splicer_exon_list_dict(self):
#         return self._splicer_exon_list_dict
    
#     def set_splicer_exon_list_dict(self, splicer_exon_list_dict):
#         self._splicer_exon_list_dict = splicer_exon_list_dict
    
#     def get_aa_codingpos(self):
#         return self._aa_codingpos
    
#     def set_aa_codingpos(self, aa_codingpos):
#         self._aa_codingpos = aa_codingpos
        
#     def is_overlapped_gene(self):
#         return self._overlapped_gene
#     def set_overlapped_gene(self, overlapped_gene):
#         try:
#             if isinstance(overlapped_gene, bool):
#                 self._overlapped_gene = overlapped_gene
#             else:
#                 raise ValueError(f"{overlapped_gene} is not a boolean")
#         except ValueError as e:
#             modern_messagebox.showerror(None, "Invalid Input", str(e))
            
#     def get_ref_microtype_dict(self):
#         return self._ref_microtype_dict
    
#     def set_ref_microtype_dict(self, ref_microtype_dict):
#         self._ref_microtype_dict = ref_microtype_dict
    
#     def get_cur_ref_microtype_dict(self):
#         return self._cur_ref_microtype_dict
    
#     def set_cur_ref_microtype_dict(self, cur_ref_microtype_dict):
#         self._cur_ref_microtype_dict = cur_ref_microtype_dict
        
#     def get_cur_children_microtype_dict(self):
#         return self._cur_children_microtype_dict
    
#     def set_cur_children_microtype_dict(self, cur_children_microtype_dict):
#         self._cur_children_microtype_dict = cur_children_microtype_dict
    
#     def get_has_new_mh(self):
#         return self._has_new_mh

#     def set_has_new_mh(self, has_new_mh):
#         try:
#             if isinstance(has_new_mh, bool):
#                 self._has_new_mh = has_new_mh
#             else:
#                 raise ValueError(f"{has_new_mh} is not a boolean")
#         except ValueError as e:
#             modern_messagebox.showerror(None, "Invalid Input", str(e))
                
#     def get_locus(self):
#         return self._locus
    
#     def set_locus(self, locus):
#         try:
#             if isinstance(locus, str):
#                 self._locus = locus
#             else:
#                 raise ValueError("locus must be a string")
#         except ValueError as e:
#             modern_messagebox.showerror(None, "Invalid Input", str(e))
    
#     def get_fprimer(self):
#         return self._fprimer
    
#     def set_fprimer(self, fprimer):
#         try:
#             if isinstance(fprimer, str):
#                 self._fprimer = fprimer
#             else:
#                 raise ValueError("fprimer must be a string")
#         except ValueError as e:
#             modern_messagebox.showerror(None, "Invalid Input", str(e))
    
#     def get_rprimer(self):
#         return self._rprimer
    
#     def set_rprimer(self, rprimer):
#         try:
#             if isinstance(rprimer, str):
#                 self._rprimer = rprimer
#             else:
#                 raise ValueError("rprimer must be a string")
#         except ValueError as e:
#             modern_messagebox.showerror(None, "Invalid Input", str(e))
    
#     def get_triml(self):
#         return self._triml
    
#     def set_triml(self, triml):
#         try:
#             if isinstance(triml, int):
#                 self._triml = triml
#             else:
#                 raise ValueError("triml must be an integer")
#         except ValueError as e:
#             modern_messagebox.showerror(None, "Invalid Input", str(e))
    
#     def get_trimr(self):
#         return self._trimr
    
#     def set_trimr(self, trimr):
#         try:
#             if isinstance(trimr, int):
#                 self._trimr = trimr
#             else:
#                 raise ValueError("trimr must be an integer")
#         except ValueError as e:
#             modern_messagebox.showerror(None, "Invalid Input", str(e))
    
#     def get_snppos(self):
#         return self._snppos
    
#     def set_snppos(self, snppos):
#         try:
#             self._snppos = sorted(snppos)
#         except ValueError as e:
#             modern_messagebox.showerror(None, "Invalid Input", str(e))
    
#     def get_orisnppos(self):
#         return self._orisnppos

#     def set_orisnppos(self, orisnppos):
#         try:
#             self._orisnppos = sorted(orisnppos)
#         except ValueError as e:
#             modern_messagebox.showerror(None, "Invalid Input", str(e))
#     def get_dnaref(self):
#         return self._dnaref
    
#     def set_dnaref(self, dnaref):
#         try:
#             if isinstance(dnaref, str):
#                 self._dnaref = dnaref
#             else:
#                 raise ValueError("dnaref must be a string")
#         except ValueError as e:
#             modern_messagebox.showerror(None, "Invalid Input", str(e))
    
#     def get_codingpos(self):
#         return self._codingpos
    
#     def set_codingpos(self, codingpos):
#         try:
#             if isinstance(codingpos, list):
#                 self._codingpos = codingpos
#             else:
#                 raise ValueError("codingpos must be a list")
#         except ValueError as e:
#             modern_messagebox.showerror(None, "Invalid Input", str(e))
    
#     def get_dna_ref(self):
#         return self._dna_ref
    
#     def set_dna_ref(self, dna_ref):
#         try:
#             if isinstance(dna_ref, str):
#                 self._dna_ref = dna_ref
#             else:
#                 raise ValueError("dna_ref must be a string")
#         except ValueError as e:
#             modern_messagebox.showerror(None, "Invalid Input", str(e))
#     def get_ori_dna_ref(self):
#         return self._ori_dna_ref
#     def set_ori_dna_ref(self, ori_dna_ref):
#         try:
#             if isinstance(ori_dna_ref, str):
#                 self._ori_dna_ref = ori_dna_ref
#             else:
#                 raise ValueError("dna_ref must be a string")
#         except ValueError as e:
#             modern_messagebox.showerror(None, "Invalid Input", str(e))
#     def get_aa_ref(self):
#         return self._aa_ref
    
#     def set_aa_ref(self, aa_ref):
#         try:
#             if isinstance(aa_ref, str):
#                 self._aa_ref = aa_ref
#             else:
#                 raise ValueError("aa_ref must be a string")
#         except ValueError as e:
#             modern_messagebox.showerror(None, "Invalid Input", str(e))
            
#     def get_has_splicer(self):
#         return self._has_splicer
    
#     def set_has_splicer(self, go_aa):
#         try:
#             if isinstance(go_aa, bool):
#                 self._has_splicer = go_aa
#             else:
#                 raise ValueError("go_aa must be a boolean")
#         except ValueError as e:
#             modern_messagebox.showerror(None, "Invalid Input", str(e))
    
#     def get_begin_with_splicer0(self):
#         return self._begin_with_splicer0
    
#     def set_begin_with_splicer0(self, begin_with_splicer0):
#         try:
#             if isinstance(begin_with_splicer0, bool):
#                 self._begin_with_splicer0 = begin_with_splicer0
#             else:
#                 raise ValueError("go_aa must be a boolean")
#         except ValueError as e:
#             modern_messagebox.showerror(None, "Invalid Input", str(e))
    
#     def get_children_microtype_dict(self):
#         return self._children_microtype_dict
    
#     def set_children_microtype_dict(self, children_microtype_dict):
#         try:
#             if isinstance(children_microtype_dict, dict):
#                 self._children_microtype_dict = children_microtype_dict
#             else:
#                 raise ValueError("children_microtype must be a dictionary")
#         except ValueError as e:
#             modern_messagebox.showerror(None, "Invalid Input", str(e))
    
#     def get_mar_microhap_df(self):
#         return self._mar_microhap_df
    
#     def set_mar_microhap_df(self, mar_microhap_df):
#         try:
#             if isinstance(mar_microhap_df, pd.DataFrame):
#                 self._mar_microhap_df = mar_microhap_df
#             else:
#                 raise ValueError("mar_microhap_df must be a pandas DataFrame")
#         except ValueError as e:
#             modern_messagebox.showerror(None, "Invalid Input", str(e))
    
#     def get_pre_mar_microhap_df(self):
#         return self._pre_mar_microhap_df
    
#     def set_pre_mar_microhap_df(self, pre_mar_microhap_df):
#         try:
#             if isinstance(pre_mar_microhap_df, pd.DataFrame):
#                 self._pre_mar_microhap_df = pre_mar_microhap_df
#             else:
#                 raise ValueError(f"{pre_mar_microhap_df} is not a dataframe")
#         except ValueError as e:
#             modern_messagebox.showerror(None, "Invalid Input", str(e))
    
#     def get_cur_mar_microhap_df(self):
#         return self._cur_mar_microhap_df
    
#     def set_cur_mar_microhap_df(self, cur_mar_microhap_df):
#         try:
#             if isinstance(cur_mar_microhap_df, pd.DataFrame):
#                 self._cur_mar_microhap_df = cur_mar_microhap_df
#             else:
#                 raise ValueError(f"{cur_mar_microhap_df} is not a dataframe")
#         except ValueError as e:
#             modern_messagebox.showerror(None, "Invalid Input", str(e))
    
#     def get_final_mar_cur_microhap_nested_dict(self):
#         return self._final_mar_cur_microhap_nested_dict
    
#     def set_final_mar_cur_microhap_nested_dict(self, final_mar_cur_microhap_nested_dict):
#         try:
#             if isinstance(final_mar_cur_microhap_nested_dict, dict):
#                 self._final_mar_cur_microhap_nested_dict = final_mar_cur_microhap_nested_dict
#             else:
#                 raise ValueError("final_mar_cur_microhap_nested_dict must be a dictionary")
#         except ValueError as e:
#             modern_messagebox.showerror(None, "Invalid Input", str(e))
    
#     def get_final_mar_pre_microhap_nested_dict(self):
#         return self._final_mar_pre_microhap_nested_dict
    
#     def set_final_mar_pre_microhap_nested_dict(self, final_mar_pre_microhap_nested_dict):
#         try:
#             if isinstance(final_mar_pre_microhap_nested_dict, dict):
#                 self._final_mar_pre_microhap_nested_dict = final_mar_pre_microhap_nested_dict
#             else:
#                 raise ValueError("final_mar_pre_microhap_nested_dict must be a dictionary")
#         except ValueError as e:
#             modern_messagebox.showerror(None, "Invalid Input", str(e))
            
#     def get_final_mar_cur_sim_microhap_nested_dict(self):
#         return self._final_mar_cur_sim_microhap_nested_dict
#     def set_final_mar_cur_sim_microhap_nested_dict(self, final_mar_cur_sim_microhap_nested_dict):
#         try:
#             if isinstance(final_mar_cur_sim_microhap_nested_dict, dict):
#                 self._final_mar_cur_sim_microhap_nested_dict = final_mar_cur_sim_microhap_nested_dict
#             else:
#                 raise ValueError("final_mar_cur_sim_microhap_nested_dict must be a dictionary")
#         except ValueError as e:
#             modern_messagebox.showerror(None, "Invalid Input", str(e))
#     def get_final_mar_pre_sim_microhap_nested_dict(self):
#         return self._final_mar_pre_sim_microhap_nested_dict
#     def set_final_mar_pre_sim_microhap_nested_dict(self, final_mar_pre_sim_microhap_nested_dict):
#         try:
#             if isinstance(final_mar_pre_sim_microhap_nested_dict, dict):
#                 self._final_mar_pre_sim_microhap_nested_dict = final_mar_pre_sim_microhap_nested_dict
#             else:
#                 raise ValueError("final_mar_pre_sim_microhap_nested_dict must be a dictionary")
#         except ValueError as e:
#             modern_messagebox.showerror(None, "Invalid Input", str(e))
    
#     def populate_ref_compre_mt(self):
#         #pdb.set_trace()
#         #print_time(f'populate_ref_compre_mt for {self.get_locus()} begin_with_splicer is {self.get_begin_with_splicer0()}')
#         if self.get_has_splicer():
#             for idx, pos_tuple_list in enumerate(self.get_codingpos()):
#                 compre_mt = CompreMicrotypeClass()
#                 compre_mt.set_mar(self.get_locus())
#                 splicer_name = f'splicer_{idx}'
#                 compre_mt.set_splicer(splicer_name)
#                 compre_mt.set_splicer_pos_list(pos_tuple_list)
#                 dna_seq, aa_seq = trans_single_dna(self.get_dna_ref(), pos_tuple_list)
#                 compre_mt.set_ref_dna_seq(dna_seq)
#                 compre_mt.set_ref_aa_seq(aa_seq)
#                 compre_mt.populate_dna_pos_list(self.get_snppos(), self.get_dna_ref())
#                 if not self.is_overlapped_gene():
#                     splicer_exon_list = self.get_splicer_exon_list_dict().get(splicer_name)
#                     if idx == 0:
#                         self.set_aa_ref(aa_seq)
#                         self.set_sappos(compre_mt.get_target_aa_snp_pos_list())
#                         self.get_aa_codingpos().append(compre_mt.extract_aa_exon_start_end_pos_list_in_splicer())
#                         compre_mt.set_splicer_aa_pos_list(compre_mt.extract_aa_exon_start_end_pos_list_in_splicer())
#                     else:
#                         splicer_0_aa_codingpos_list = self.get_aa_codingpos()[0]
#                         aa_codingpos = [splicer_0_aa_codingpos_list[i] for i in splicer_exon_list]
#                         self.get_aa_codingpos().append(aa_codingpos)
#                         compre_mt.set_splicer_aa_pos_list(aa_codingpos)
#                     compre_mt.populate_aa_pos_list(self.get_sappos(), self.get_aa_ref())
#                 self._ref_microtype_dict[splicer_name] = compre_mt
#         else:
#             compre_mt = CompreMicrotypeClass()
#             compre_mt.set_mar(self.get_locus())
#             splicer_name = f'splicer_0'
#             compre_mt.set_splicer(splicer_name)
#             compre_mt.set_target_dna_snp_pos_list(self.get_snppos()) #must consider the trim left and trim right
#             compre_mt.set_ref_dna_seq(self.get_dna_ref())
#             self._ref_microtype_dict[splicer_name] = compre_mt
#         #print_time(f'populate_ref_compre_mt for {self.get_locus()} end')

#     def get_max_ref_label_len(self)->int:
#         return self.get_ref_microtype().get_max_label_len()

#     def get_max_children_label_len(self)->int:
#         max_len = 0
#         for _, child_mt in self.get_children_microtype_dict().items():
#             v_len = child_mt.get_max_label_len()
#             if v_len > max_len:
#                 max_len = v_len
#         return max_len
    
#     def print_ref(self):
#         ref_refmt = self.get_ref_microtype()
#         print(f"ref marker is {self.get_locus()}")
#         print(f"Ref Microtype: {ref_refmt.get_basename()}")
#         for dna, dna_value in ref_refmt.get_dna_microhaps_dict().items():
#             print(f'dna is {dna}')
#             print(f'for dna print is {dna_value.print()}')
#         for aa, aa_value in ref_refmt.get_aa_micropeps_dict().items():
#             print(f'aa is {aa}')
#             print(f'for dna print is {aa_value.print()}')