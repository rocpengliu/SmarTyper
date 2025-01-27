import warnings
warnings.filterwarnings("ignore", message="mkl-service")

from tkinter import messagebox  # Importing messagebox for error handling
import pandas as pd
from typing import Dict
from ..utils.utils_common import print_time
import pdb
from ..utils.common import dna_base_list, aa_base_list
import copy
from .segment_class import SegmentClass

class CompreVariationClass:
    def __init__(self):
        self._id = "" # mar_spacer_0_mh_0 for dna and mar_spacer_0_mp_0 for aa if no splicer, should be mar_mh_0
        self._mar = "" #marker
        self._splicer = "" #splicer_0
        self._mt = "" #microtype, mh_0 or mp_0
        self._seq = "" #dna_seq or aa_seq
        self._snp_pos_list = [] #snp position if in the true splicer, it should [(ori_pos0, cur_pos0), (ori_pos1, cur_pos1)]
        self._indel_pos_list = []
        self._snp_str = ""
        
    def get_snp_str(self):
        return self._snp_str
    
    def set_snp_str(self, snp_str):
        self._snp_str = snp_str
    
    def get_id(self):
        return self._id
    
    def set_id(self, id):
        self._id = id
    
    def get_mar(self):
        return self._mar
    
    def set_mar(self, mar):
        self._mar = mar
    
    def get_splicer(self):
        return self._splicer
    
    def set_splicer(self, splicer):
        self._splicer = splicer
        
    def get_mt(self):
        return self._mt
    
    def set_mt(self, mt):
        self._mt = mt
    
    def get_seq(self):
        return self._seq
    
    def set_seq(self, seq):
        self._seq = seq
    
    def get_snp_pos_list(self):
        return self._snp_pos_list
    
    def set_snp_pos_list(self, snp_pos_list):
        self._snp_pos_list = snp_pos_list
    
    def get_indel_pos_list(self):
        return self._indel_pos_list
    
    def set_indel_pos_list(self, indel_pos_list):
        self._indel_pos_list = indel_pos_list

class CompreMicrotypeClass:
    def __init__(self) -> None:
        self._mar = ""
        self._splicer="" #splicer 0 if no splicer
        #self._has_aa = False # this is coupled with refMicrotype for _begin_with_splicer0 , if it has the splicer, but the first splicer is not the full len of ref.
        self._exon1_start_at_pos0 = False #if the first exon in this splicer starting at pos0
        self._exon1_aa_start_at_pos0 = False #if the first aa exon in this splicer starting at pos0
        self._splicer_pos_list = [] # [(pos1:pos2), (pos3:pos4)]
        self._splicer_aa_pos_list = [] # for aa seq 
        #self._intron_pos_list = [] # [(pos1:pos2), (pos3:pos4)] used for convert between the _tot_dna_snp_pos_list and _target_dna_snp_pos_list and others
        self._exon_intron_pos_list = [] #[SegmentClass] used for converting between orginal pos and actual pos in this splicer
        self._exon_intron_aa_pos_list = []
        #self._converted_splicer_pos_list = [] #[(0:5),(5:10)] this is the actually exon's position list, exon1 0:5, exon2:5:10
        self._target_dna_snp_pos_list = []# target snps [cur_pos0, cur_pos1] is the pos in the splicer, but it has to be converted to the orignal one which is the pos in the DNA seq(the actual whole DNAseq)
        self._tot_dna_snp_pos_list = [] ##total valide heter snps in the populatio mhs by summaring the _dna_mh_dict
        self._target_aa_snp_pos_list = []
        self._tot_aa_snp_pos_list = []

        self._ref_dna_seq = ""
        self._ref_aa_seq = ""

        self._dna_mh_df = pd.DataFrame()#only for children
        self._aa_mp_df = pd.DataFrame()#only for children not for reference

        self._dna_mh_dict:Dict[str, CompreVariationClass] = {} # key is mh_0 value is CompreVariationClass #only for children not for reference
        self._aa_mp_dict:Dict[str, CompreVariationClass] = {} #key is mp_0, value is CompreVariationClass
        
        self._dna_base_freq_df = pd.DataFrame()
        self._aa_base_freq_df= pd.DataFrame()
        
        self._dna_tre = None #phylo tree for dna
        self._aa_tre = None

    def get_dna_tre(self):
        return self._dna_tre
    
    def set_dna_tre(self, dna_tre):
        self._dna_tre = dna_tre
    
    def get_aa_tre(self):
        return self._aa_tre
    
    def set_aa_tre(self, aa_tre):
        self._aa_tre = aa_tre
        
    def get_exon_intron_aa_pos_list(self):
        return self._exon_intron_aa_pos_list
    
    def set_exon_intron_aa_pos_list(self, exon_intron_aa_pos_list):
        self._exon_intron_aa_pos_list = exon_intron_aa_pos_list
        
    def is_exon1_aa_start_at_pos0(self):
        return self._exon1_aa_start_at_pos0
    
    def set_exon1_aa_start_at_pos0(self, exon1_aa_start_at_pos0):
        self._exon1_aa_start_at_pos0 = exon1_aa_start_at_pos0
        
    def get_splicer_aa_pos_list(self):
        return self._splicer_aa_pos_list
    
    def set_splicer_aa_pos_list(self, splicer_aa_pos_list):
        self._splicer_aa_pos_list = splicer_aa_pos_list
        
    def get_dna_base_freq_df(self):
        return self._dna_base_freq_df
    def set_dna_base_freq_df(self, dna_base_freq_df):
        self._dna_base_freq_df = dna_base_freq_df
    
    def get_aa_base_freq_df(self):
        return self._aa_base_freq_df
    def set_aa_base_freq_df(self, aa_base_freq_df):
        self._aa_base_freq_df = aa_base_freq_df
        
    def get_label(self, include_ref = True):
        label = ""
        if len(self._splicer_pos_list) == 0:
            if include_ref:
                label = f"{self._mar}_ref"
            else:
                label = f"{self._mar}"
        else:
            label = f"{self._mar}_{self._splicer}"
        return label
    
    def get_dna_mh_df(self):
        return self._dna_mh_df
    
    def set_dna_mh_df(self, dna_mh_df):
        self._dna_mh_df = dna_mh_df
    
    def get_aa_mp_df(self):
        return self._aa_mp_df
    
    def set_aa_mh_df(self, aa_mp_df):
        self._aa_mp_df = aa_mp_df
        
    def get_mar(self):
        return self._mar
    
    def set_mar(self, mar):
        self._mar = mar
        
    def get_splicer(self):
        return self._splicer
    
    def set_splicer(self, splicer):
        self._splicer = splicer
    
    def get_exon1_start_at_pos0(self):
        return self._exon1_start_at_pos0
    
    def set_exon1_start_at_pos0(self, exon1_start_at_pos0):
        self._exon1_start_at_pos0 = exon1_start_at_pos0
        
    def get_splicer_pos_list(self):
        return self._splicer_pos_list
    
    def set_splicer_pos_list(self, splicer_pos_list):
        self._splicer_pos_list = splicer_pos_list
    
    def get_exon_intron_pos_list(self):
        return self._exon_intron_pos_list
    
    def set_exon_intron_pos_list(self, exon_intron_pos_list):
        self._exon_intron_pos_list = exon_intron_pos_list
    
    # def get_converted_splicer_pos_list(self):
    #     return self._converted_splicer_pos_list
    
    # def set_converted_splicer_pos_list(self, converted_splicer_pos_list):
    #     self._converted_splicer_pos_list = converted_splicer_pos_list
    
    def get_target_dna_snp_pos_list(self):
        return self._target_dna_snp_pos_list
    
    def set_target_dna_snp_pos_list(self, target_dna_snp_pos_list):
        self._target_dna_snp_pos_list = target_dna_snp_pos_list
    
    def get_tot_dna_snp_pos_list(self):
        return self._tot_dna_snp_pos_list
    
    def set_tot_dna_snp_pos_list(self, tot_dna_snp_pos_list):
        self._tot_dna_snp_pos_list = tot_dna_snp_pos_list
    
    def get_target_aa_snp_pos_list(self):
        return self._target_aa_snp_pos_list
    
    def set_target_aa_snp_pos_list(self, target_aa_snp_pos_list):
        self._target_aa_snp_pos_list = target_aa_snp_pos_list
    
    def get_tot_aa_snp_pos_list(self):
        return self._tot_aa_snp_pos_list
    
    def set_tot_aa_snp_pos_list(self, tot_aa_snp_pos_list):
        self._tot_aa_snp_pos_list = tot_aa_snp_pos_list
    
    def get_ref_dna_seq(self):
        return self._ref_dna_seq
    
    def set_ref_dna_seq(self, ref_dna_seq):
        self._ref_dna_seq = ref_dna_seq
    
    def get_ref_aa_seq(self):
        return self._ref_aa_seq
    
    def set_ref_aa_seq(self, ref_aa_seq):
        self._ref_aa_seq = ref_aa_seq
    
    def get_dna_mh_dict(self):
        return self._dna_mh_dict
    
    def set_dna_mh_dict(self, dna_mh_dict):
        self._dna_mh_dict = dna_mh_dict
    
    def get_aa_mp_dict(self):
        return self._aa_mp_dict
    
    def set_aa_mp_dict(self, aa_mp_dict):
        self._aa_mp_dict = aa_mp_dict\
    
    def cal_new_splicer_pos_list(self, snppos, dna = True)->list:
        print_time(f'dna true or false is {dna}')
        pos_set = set()
        for pos_tuple in (self.get_splicer_pos_list() if dna else self.get_splicer_aa_pos_list()):
            start_pos, end_pos = pos_tuple
            print_time(f'start_pos {start_pos}, end_pos {end_pos}')
            tmp_pos_list = [pos for pos in snppos if pos in range(start_pos, end_pos)]
            pos_set.update(tmp_pos_list)
        return sorted(pos_set)
    def populate_aa_pos_list(self, snppos, aa_ref):
        exon_id = 0
        intron_id = 0
        seg_id = 0
        tot_exon_len = 0
        offset_len = 0 #tot intron length
        exon_intron_pos_list = []
        for idx, pos_tuple in enumerate(self.get_splicer_aa_pos_list()):
            start_pos, end_pos = pos_tuple
            if idx == 0:
                if pos_tuple[0] == 0:#start with exon
                    self.set_exon1_start_at_pos0(True)
                    exon_seg = SegmentClass()
                    exon_seg.set_seg_type('exon')
                    exon_seg.set_offset_len(0)
                    exon_seg.set_seg_id_in_zon(0)
                    exon_seg.set_seg_id_in_gene(0)
                    exon_seg.set_start_pos_in_gene(0)
                    exon_seg.set_end_pos_in_gene(end_pos)
                    exon_seg.set_start_pos_in_zon(0)
                    exon_seg.set_end_pos_in_zon(end_pos)
                    exon_intron_pos_list.append(exon_seg)
                    tot_exon_len += (end_pos - start_pos)
                    exon_id += 1
                    seg_id += 1
                else:
                    self.set_exon1_start_at_pos0(False)
                    intron_seg = SegmentClass()
                    intron_seg.set_seg_type('intron')
                    intron_seg.set_seg_id_in_zon(0)
                    intron_seg.set_seg_id_in_gene(0)
                    intron_seg.set_start_pos_in_gene(0)
                    intron_seg.set_end_pos_in_gene(start_pos)
                    intron_seg.set_start_pos_in_zon(0)
                    intron_seg.set_end_pos_in_zon(start_pos)
                    
                    exon_intron_pos_list.append(intron_seg)
                    
                    offset_len = (start_pos - 0)
                    intron_id += 1
                    seg_id += 1
                    
                    exon_seg = SegmentClass()
                    exon_seg.set_seg_type('exon')
                    exon_seg.set_offset_len(offset_len)
                    exon_seg.set_seg_id_in_gene(seg_id)
                    exon_seg.set_seg_id_in_zon(0)
                    exon_seg.set_start_pos_in_gene(start_pos)
                    exon_seg.set_end_pos_in_gene(end_pos)
                    exon_seg.set_start_pos_in_zon(0)
                    tot_exon_len += (end_pos - start_pos)
                    exon_seg.set_end_pos_in_zon(0 + tot_exon_len)
                    
                    exon_intron_pos_list.append(exon_seg)
                    
                    exon_id += 1
                    seg_id += 1
            else:
                intron_seg = SegmentClass()
                intron_seg.set_seg_type('intron')
                intron_seg.set_seg_id_in_gene(seg_id)
                intron_seg.set_seg_id_in_zon(intron_id)
                intron_start = offset_len + tot_exon_len
                intron_end = start_pos
                intron_seg.set_start_pos_in_gene(intron_start)
                intron_seg.set_end_pos_in_gene(intron_end)
                intron_seg.set_start_pos_in_zon(offset_len)
                offset_len += (intron_end - intron_start)
                intron_seg.set_end_pos_in_zon(offset_len)
                
                exon_intron_pos_list.append(intron_seg)
                
                intron_id += 1
                seg_id += 1
                
                exon_seg = SegmentClass()
                exon_seg.set_seg_type('exon')
                exon_seg.set_offset_len(offset_len)
                exon_seg.set_seg_id_in_gene(seg_id)
                exon_seg.set_seg_id_in_zon(exon_id)
                exon_seg.set_start_pos_in_gene(start_pos)
                exon_seg.set_end_pos_in_gene(end_pos)
                exon_seg.set_start_pos_in_zon(tot_exon_len)
                tot_exon_len += (end_pos - start_pos)
                exon_seg.set_end_pos_in_zon(tot_exon_len)
                
                exon_intron_pos_list.append(exon_seg)
                
                seg_id += 1
                exon_id += 1
                
                if idx == (len(self.get_splicer_aa_pos_list()) - 1):
                    if pos_tuple[1] < len(aa_ref): # the last intron no more exons
                        intron_seg = SegmentClass()
                        intron_seg.set_seg_type('intron')
                        intron_seg.set_seg_id_in_gene(seg_id)
                        intron_seg.set_seg_id_in_zon(intron_id)
                        intron_seg.set_start_pos_in_gene(end_pos)
                        intron_seg.set_end_pos_in_gene(len(aa_ref))
                        intron_seg.set_start_pos_in_zon(offset_len)
                        intron_seg.set_end_pos_in_zon(offset_len + (len(aa_ref) - end_pos))
                        exon_intron_pos_list.append(intron_seg)
        self.set_exon_intron_aa_pos_list(exon_intron_pos_list)
        ori_pos_list = self.cal_new_splicer_pos_list(snppos, False)
        converted_pos_list = self.convert_pos_ori_2_cur(ori_pos_list, False)
        self.set_target_aa_snp_pos_list(converted_pos_list)

    def populate_dna_pos_list(self, snppos, dna_ref):
        #pdb.set_trace()
        exon_id = 0
        intron_id = 0
        seg_id = 0
        tot_exon_len = 0
        offset_len = 0 #tot intron length
        exon_intron_pos_list = []
        for idx, pos_tuple in enumerate(self.get_splicer_pos_list()):
            start_pos, end_pos = pos_tuple
            if idx == 0:
                if pos_tuple[0] == 0:#start with exon
                    self.set_exon1_start_at_pos0(True)
                    exon_seg = SegmentClass()
                    exon_seg.set_seg_type('exon')
                    exon_seg.set_offset_len(0)
                    exon_seg.set_seg_id_in_zon(0)
                    exon_seg.set_seg_id_in_gene(0)
                    exon_seg.set_start_pos_in_gene(0)
                    exon_seg.set_end_pos_in_gene(end_pos)
                    exon_seg.set_start_pos_in_zon(0)
                    exon_seg.set_end_pos_in_zon(end_pos)
                    exon_intron_pos_list.append(exon_seg)
                    tot_exon_len += (end_pos - start_pos)
                    exon_id += 1
                    seg_id += 1
                else:
                    self.set_exon1_start_at_pos0(False)
                    intron_seg = SegmentClass()
                    intron_seg.set_seg_type('intron')
                    intron_seg.set_seg_id_in_zon(0)
                    intron_seg.set_seg_id_in_gene(0)
                    intron_seg.set_start_pos_in_gene(0)
                    intron_seg.set_end_pos_in_gene(start_pos)
                    intron_seg.set_start_pos_in_zon(0)
                    intron_seg.set_end_pos_in_zon(start_pos)
                    
                    exon_intron_pos_list.append(intron_seg)
                    
                    offset_len = (start_pos - 0)
                    intron_id += 1
                    seg_id += 1
                    
                    exon_seg = SegmentClass()
                    exon_seg.set_seg_type('exon')
                    exon_seg.set_offset_len(offset_len)
                    exon_seg.set_seg_id_in_gene(seg_id)
                    exon_seg.set_seg_id_in_zon(0)
                    exon_seg.set_start_pos_in_gene(start_pos)
                    exon_seg.set_end_pos_in_gene(end_pos)
                    exon_seg.set_start_pos_in_zon(0)
                    tot_exon_len += (end_pos - start_pos)
                    exon_seg.set_end_pos_in_zon(0 + tot_exon_len)
                    
                    exon_intron_pos_list.append(exon_seg)
                    
                    exon_id += 1
                    seg_id += 1
            else:
                intron_seg = SegmentClass()
                intron_seg.set_seg_type('intron')
                intron_seg.set_seg_id_in_gene(seg_id)
                intron_seg.set_seg_id_in_zon(intron_id)
                intron_start = offset_len + tot_exon_len
                intron_end = start_pos
                intron_seg.set_start_pos_in_gene(intron_start)
                intron_seg.set_end_pos_in_gene(intron_end)
                intron_seg.set_start_pos_in_zon(offset_len)
                offset_len += (intron_end - intron_start)
                intron_seg.set_end_pos_in_zon(offset_len)
                
                exon_intron_pos_list.append(intron_seg)
                
                intron_id += 1
                seg_id += 1
                
                exon_seg = SegmentClass()
                exon_seg.set_seg_type('exon')
                exon_seg.set_offset_len(offset_len)
                exon_seg.set_seg_id_in_gene(seg_id)
                exon_seg.set_seg_id_in_zon(exon_id)
                exon_seg.set_start_pos_in_gene(start_pos)
                exon_seg.set_end_pos_in_gene(end_pos)
                exon_seg.set_start_pos_in_zon(tot_exon_len)
                tot_exon_len += (end_pos - start_pos)
                exon_seg.set_end_pos_in_zon(tot_exon_len)
                
                exon_intron_pos_list.append(exon_seg)
                
                seg_id += 1
                exon_id += 1
                
                if idx == (len(self.get_splicer_pos_list()) - 1):
                    if pos_tuple[1] < len(dna_ref): # the last intron no more exons
                        intron_seg = SegmentClass()
                        intron_seg.set_seg_type('intron')
                        intron_seg.set_seg_id_in_gene(seg_id)
                        intron_seg.set_seg_id_in_zon(intron_id)
                        intron_seg.set_start_pos_in_gene(end_pos)
                        intron_seg.set_end_pos_in_gene(len(dna_ref))
                        intron_seg.set_start_pos_in_zon(offset_len)
                        intron_seg.set_end_pos_in_zon(offset_len + (len(dna_ref) - end_pos))
                        exon_intron_pos_list.append(intron_seg)
        self.set_exon_intron_pos_list(exon_intron_pos_list)#must consider the trim left and trim right
        ori_pos_list = self.cal_new_splicer_pos_list(snppos)#filter the oringal snppos to the ori_pos_list because snppos contains all the snps, but not all the snps are in this splicer
        converted_pos_list = self.convert_pos_ori_2_cur(ori_pos_list)#convert to the current splicer position
        print_time(f'populate_pos_list: oringal pos is {ori_pos_list} and converted pos is {converted_pos_list}')
        self.set_target_dna_snp_pos_list(converted_pos_list)#must consider the trim left and trim right
        aa_pos_set = [pos // 3 for pos in converted_pos_list]
        aa_pos_set = list(set(aa_pos_set))
        self.set_target_aa_snp_pos_list(sorted(aa_pos_set))
        print_time(f'exon_intron_pos_list size is {len(exon_intron_pos_list)}')
        # for idx, seg in enumerate(exon_intron_pos_list):
        #     seg.print()
    # def populate_pos_list(self, snppos, dna_ref):
    #     pos_set = set()
    #     intron_pos_list = []
    #     for idx, pos_tuple in enumerate(self.get_splicer_pos_list()):
    #         tmp_pos_list = [pos for pos in snppos if pos in range(pos_tuple[0], pos_tuple[1])]
    #         pos_set.update(tmp_pos_list)
    #         if idx == 0:
    #             if pos_tuple[0] == 0:
    #                 self.set_exon1_start_at_pos0(True)
    #             elif pos_tuple[0] > 0:
    #                 new_pos_tuple = (0, pos_tuple[0])
    #                 intron_pos_list.append(new_pos_tuple)
    #         elif idx == (len(pos_tuple) - 1):
    #             if pos_tuple[1] < len(dna_ref):
    #                 new_pos_tuple = (pos_tuple[1], len(dna_ref))
    #                 intron_pos_list.append(new_pos_tuple)
    #         else:
    #             new_pos_tuple = (self.get_splicer_pos_list()[idx-1][1], pos_tuple[0])
    #             intron_pos_list.append(new_pos_tuple)
    #     self.set_intron_pos_list(intron_pos_list) #must consider the trim left and trim right
    #     self.set_target_dna_snp_pos_list(sorted(pos_set)) #must consider the trim left and trim right

    #     aa_pos_set = set(sorted([pos // 3 for pos in pos_set]))
    #     self.set_target_aa_snp_pos_list(sorted(aa_pos_set))
    def convert_pos_ori_2_cur(self, ori_pos_list, dna = True):
        work_list = self.get_exon_intron_pos_list() if dna else self.get_exon_intron_aa_pos_list()
        converted_list = []
        if len(work_list) != 0:
            for seg in work_list:
                if seg.get_seg_type() == 'exon':
                    ori_tmp_list = [pos for pos in ori_pos_list if pos in range(seg.get_start_pos_in_gene(), seg.get_end_pos_in_gene())]
                    converted_list.extend([pos - seg.get_offset_len() for pos in ori_tmp_list])
        if len(ori_pos_list) != len(converted_list):
            raise ValueError(f"ori_pos_list and converted_list len not match. ori_len={len(ori_pos_list)}, converted_len={len(converted_list)}")
        return sorted(converted_list)
    
    def convert_pos_cur_2_ori(self, cur_pos_list, dna=True):
        #pdb.set_trace()
        work_list = self.get_exon_intron_pos_list() if dna else self.get_exon_intron_aa_pos_list()
        ori_list = []
        if len(work_list) != 0:
            for seg in work_list:
                if seg.get_seg_type() == 'exon':
                    #seg.print()
                    cur_tmp_list = [pos for pos in cur_pos_list if pos in range(seg.get_start_pos_in_zon(), seg.get_end_pos_in_zon())]
                    ori_list.extend([pos + seg.get_offset_len() for pos in cur_tmp_list])
            if len(cur_pos_list)!= len(ori_list):
                raise ValueError(f"cur_pos_list and ori_list len not match. cur_len={len(cur_pos_list)}, ori_len={len(ori_list)}")
        else:
            ori_list = cur_pos_list.copy()
        return sorted(ori_list)
    def cal_longest_compre_var_label(self, dna = True):
        label_len = 0
        tmp_dict = self.get_dna_mh_dict() if dna else self.get_aa_mp_dict()
        if len(tmp_dict) == 0 or tmp_dict is None:
            raise ValueError(f"{self.get_mar}_{self.get_splicer()}'s children dict len is {len(tmp_dict)}")
        for cv in tmp_dict.values():
            tmp_len = len(cv.get_id())
            if tmp_len > label_len:
                label_len = tmp_len
        return label_len
    
    def generate_base_freq_df(self, dna=True):
        #pdb.set_trace()
        seq_seq_set = set()
        for miv in (self.get_dna_mh_dict().values() if dna else self.get_aa_mp_dict().values()):
            if len(miv.get_indel_pos_list()) == 0:
                seq_seq_set.add(miv.get_seq())
        if len(seq_seq_set) == 0:
            return
        seq_df = pd.DataFrame([list(sequ) for sequ in seq_seq_set])
        freq_data = []
        for col in seq_df.columns:
            counts = seq_df[col].value_counts(normalize=True).reindex((dna_base_list if dna else aa_base_list), fill_value=0)
            freq_data.append(counts)
        base_freq_df = pd.concat(freq_data, axis=1).T
        base_freq_df.columns = dna_base_list if dna else aa_base_list
        if dna:
            self.set_dna_base_freq_df(base_freq_df)
        else:
            self.set_aa_base_freq_df(base_freq_df)

    def extract_exon_cur_start_end_pos_list(self):
        pos_list = []
        if len(self.get_exon_intron_pos_list()) != 0:
            for seg in self.get_exon_intron_pos_list():
                if seg.get_seg_type() == "exon":
                    pos_list.append((seg.get_start_pos_in_gene(), seg.get_end_pos_in_gene()-1))
        return pos_list
    
    def extract_aa_exon_start_end_pos_list_in_splicer(self):
        pos_list = []
        if len(self.get_exon_intron_pos_list()) != 0:
            for seg in self.get_exon_intron_pos_list():
                if seg.get_seg_type() == "exon":
                    pos_list.append((seg.get_start_pos_in_zon(), seg.get_end_pos_in_zon()))
        if all(x % 3 == 0  and y % 3 == 0 for x, y in pos_list):
            pos_list = [(x // 3, y // 3) for x, y in pos_list]
            return pos_list
        else:
            raise ValueError(f'extract_aa_exon_start_end_pos_list_in_splicer, some pos_list in {pos_list} are not divisible by 3')