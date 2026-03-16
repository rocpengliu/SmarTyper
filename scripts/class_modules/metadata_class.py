import os
import pandas as pd
from tkinter import messagebox
from ..utils.utils_func import split_codingpos, check_overlapping_gene, get_splicer_exon_list_map, get_new_codingpos
from ..utils.utils_common import print_time
from .ref_microhap_class import RefMicrotype
import pdb
from ..utils import modern_messagebox

class MetaDataClass:
    def __init__(self):
        self._sample_df =pd.DataFrame()
        self._loc_df = pd.DataFrame()
        self._samples_list=[]
        self._ref_markers_list=[]
        self._cur_mh_markers_list=[]
        self._cur_mh_samples_list=[]
        self._pre_mh_markers_list=[]
        self._pre_mh_samples_list=[]
        self._sex_df = pd.DataFrame()
        self._cur_microhap_df = pd.DataFrame()#read the all_sample_final_microhap_file
        self._pre_microhap_df = pd.DataFrame() # read the pre microhap file

    def get_sample_df(self):
        return self._sample_df
    
    def set_sample_df(self, sample_df):
        self._sample_df = sample_df
    
    def get_loc_df(self):
        return self._loc_df
    
    def set_loc_df(self, loc_df):
        self._loc_df = loc_df
    
    def get_samples_list(self):
        return self._samples_list
    
    def set_samples_list(self, samples_list):
        self._samples_list = samples_list

    def get_ref_markers_list(self):
        return self._ref_markers_list
    
    def set_ref_markers_list(self, ref_markers_list):
        self._ref_markers_list = ref_markers_list
        
    def get_cur_mh_markers_list(self):
        return self._cur_mh_markers_list
    
    def set_cur_mh_markers_list(self, cur_mh_markers_list):
        self._cur_mh_markers_list = cur_mh_markers_list
    
    def get_cur_mh_samples_list(self):
        return self._cur_mh_samples_list
    
    def set_cur_mh_samples_list(self, cur_mh_samples_list):
        self._cur_mh_samples_list = cur_mh_samples_list
    
    def get_pre_mh_markers_list(self):
        return self._pre_mh_markers_list
    
    def set_pre_mh_markers_list(self, pre_mh_markers_list):
        self._pre_mh_markers_list = pre_mh_markers_list
        
    def get_pre_mh_samples_list(self):
        return self._pre_mh_samples_list
    
    def set_pre_mh_samples_list(self, pre_mh_samples_list):
        self._pre_mh_samples_list = pre_mh_samples_list
        
    def get_sex_df(self):
        return self._sex_df
    
    def set_sex_df(self, sex_df):
        self._sex_df = sex_df
    
    def read_sexfile(self, parameter_class):
        fpath =parameter_class.get_sexfile()
        if os.path.isfile(fpath):
            self._sex_df = pd.read_csv(fpath, delimiter="\t")
    
    def get_cur_microhap_df(self):
        return self._cur_microhap_df
    
    def set_cur_microhap_df(self, cur_microhap_df):
        self._cur_microhap_df = cur_microhap_df

    def get_pre_microhap_df(self):
        return self._pre_microhap_df
    
    def set_pre_microhap_df(self, pre_microhap_df):
        self._pre_microhap_df = pre_microhap_df
    def read_samplefile(self, parameter_class):
        fpath = parameter_class.get_samplefile()
        print(f"reading sample file: {fpath}")
        if os.path.isfile(fpath):
            sampletable = pd.read_csv(fpath, delimiter="\t", header=None)
            if sampletable.shape[0] == 0:
                modern_messagebox.showerror("Invalid Input", "sample table must not be empty!")
                raise ValueError("sample table must not be empty!")
            if sampletable.shape[1] == 3 and parameter_class.get_seqtype() == "se":
                sampletable.columns = ['sample', 'read1', 'grp']
            elif sampletable.shape[1] == 4 and parameter_class.get_seqtype() == "pe":
                sampletable.columns = ['sample', 'read1', 'read2', 'grp']
            else:
                modern_messagebox.showerror("Invalid Input", "sample table must has 3 or 4 columns")
                raise ValueError("sample table must has 3 or 4 columns")
            sampletable['sample'] = sampletable['sample'].astype(str)
            self._sample_df=sampletable.astype({'sample':str})
            self._samples_list=sorted(sampletable['sample'].unique())
            
    def read_locifile(self, parameter_class, post_microhap_class, mh=False):
        fpath=parameter_class.get_locifile()
        print_time(f"reading loci file: {fpath}")
        #pdb.set_trace()
        if os.path.isfile(fpath):
            locitable =  pd.read_csv(fpath, delimiter="\t", header =None)
            if locitable.shape[0] == 0:
                modern_messagebox.showerror("Invalid Input", "loci table must not be empty!")
                raise ValueError("loci table must not be empty!")
            ncol = locitable.shape[1]
            if  ncol == 8 and parameter_class.get_analtype() == "snp":
                locitable.columns=['locus', 'fprimer', 'rprimer', 'triml', 'trimr', 'snppos', 'codingpos', 'ref']
            elif ncol == 8 and parameter_class.get_analtype() == "sat":
                locitable.columns=['locus', 'fprimer', 'rprimer', 'fflank', 'rflank', 'repeat', 'numrep', 'mra']
            else:
                modern_messagebox.showerror("Invalid Input", "loci table must have 8 columns")
                raise ValueError("loci table must have 8 columns")
            locitable['locus'] = locitable['locus'].astype(str)
            locitable = locitable.sort_values(by='locus')

            if parameter_class.get_analtype() == "snp":
                #pdb.set_trace()
                for idx, row in locitable.iterrows():
                    mar_ref = RefMicrotype()
                    mar_ref.set_locus(row['locus'].strip())
                    mar_ref.set_fprimer(row['fprimer'].strip())
                    mar_ref.set_rprimer(row['rprimer'].strip())
                    mar_ref.set_triml(int(row['triml']))
                    mar_ref.set_trimr(int(row['trimr']))
                    mar_ref.set_ori_dna_ref(row['ref'].strip())
                    mar_ref.set_dna_ref(row['ref'].strip())
                    if mar_ref.get_trimr() >= len(mar_ref.get_dna_ref()):
                        modern_messagebox.showerror(None, "Invalid Input", f"{row['locus']} tail trim length is too long")
                        raise ValueError(f"{row['locus']} tail trim length is too long")
                    if mar_ref.get_trimr() != 0:
                        mar_ref.set_dna_ref(mar_ref.get_dna_ref()[:-mar_ref.get_trimr()])
                    if mar_ref.get_triml() >= len(mar_ref.get_dna_ref()):
                        modern_messagebox.showerror(None, "Invalid Input", f"{row['locus']} head trim length is too long")
                        raise ValueError(f"{row['locus']} head trim length is too long")
                    if mar_ref.get_triml() != 0:
                        mar_ref.set_dna_ref(mar_ref.get_dna_ref()[mar_ref.get_triml():])
                    if len(mar_ref.get_dna_ref()) == 0:
                        modern_messagebox.showerror(None, "Invalid Input", f"{row['locus']} trim length is too long")
                        raise ValueError(f"{row['locus']} trim length is too long")
                    if pd.notna(row['snppos']) and str(row['snppos']).replace(' ', '') not in ["0", "0.0", "na", "nan", ""]:
                        snpos = [int(pos.strip()) for pos in str(row['snppos']).replace(" ", "").split('|')]
                        snpos = sorted(snpos)
                        if len(snpos) != 0:
                            mar_ref.set_orisnppos(sorted(snpos))
                            trimmedsnpos = []
                            if mar_ref.get_trimr() != 0:
                                trimmedsnpos=[pos for pos in snpos if pos <= (len(mar_ref.get_ori_dna_ref()) - mar_ref.get_trimr())]
                            if mar_ref.get_triml() != 0:
                                trimmedsnpos=[(pos - mar_ref.get_triml()) for pos in trimmedsnpos if (pos >= mar_ref.get_triml())]
                            if len(trimmedsnpos) != 0:
                                mar_ref.set_snppos(trimmedsnpos)
                            else:
                                mar_ref.set_snppos(snpos)
                            # if mh:
                            #     trimmedsnpos = []
                            #     if mar_ref.get_trimr() != 0:
                            #         trimmedsnpos=[pos for pos in snpos if pos <= (len(mar_ref.get_ori_dna_ref()) - mar_ref.get_trimr())]
                            #     if mar_ref.get_triml() != 0:
                            #         trimmedsnpos=[(pos - mar_ref.get_triml()) for pos in trimmedsnpos if (pos >= mar_ref.get_triml())]
                            #     if len(trimmedsnpos) != 0:
                            #         mar_ref.set_snppos(trimmedsnpos)
                            # else:
                            #     mar_ref.set_snppos(sorted(snpos))
                    #pdb.set_trace()
                    if mh:
                        if str(row['codingpos']).replace(' ', '') != '0':
                            codingpos = split_codingpos(row['codingpos'])
                            if mar_ref.get_triml() != 0 or mar_ref.get_trimr() != 0:
                                newcodingpos = get_new_codingpos(codingpos, mar_ref.get_triml(), mar_ref.get_trimr(), len(mar_ref.get_ori_dna_ref()))
                                if len(newcodingpos) == 0:
                                    modern_messagebox.showerror(None, "Invalid Input", f"{row['locus']} trim lengths have sth wrong")
                                    raise ValueError(f"{row['locus']} triml or trimr has the problem with exon pos!")
                                codingpos = newcodingpos
                            if codingpos is not None and len(codingpos) != 0:
                                mar_ref.set_has_splicer(True)
                                mar_ref.set_overlapped_gene(not check_overlapping_gene(codingpos))
                                mar_ref.set_codingpos(codingpos)
                                if not mar_ref.is_overlapped_gene():
                                    mar_ref.set_splicer_exon_list_dict(get_splicer_exon_list_map(codingpos))
                    mar_ref.populate_ref_compre_mt()#must be put here because when mh is false, it still needs to populate
                    post_microhap_class.get_loc_ref_dict()[row['locus']]=mar_ref
                post_microhap_class.set_loc_ref_dict(dict(sorted(post_microhap_class.get_loc_ref_dict().items())))
            self._loc_df = locitable
            self.set_ref_markers_list(sorted(locitable['locus'].unique()))
            print_time(f'total {len(self.get_ref_markers_list())} markers read from loci file')
            if len(self.get_ref_markers_list()) == 0:
                modern_messagebox.showerror(None, "Invalid Input", f"loci file: {fpath} is not valid")
                raise ValueError(f"please upload loci file first")

    def read_cur_microhap_file(self, parameter_class):
        #pdb.set_trace()
        fpath = parameter_class.get_cur_microhap_input_file()
        if not os.path.isfile(fpath):
            modern_messagebox.showerror(None, "Invalid Input", f"{fpath} is not a file")
            raise ValueError(f"{fpath} is not a file")
        tmp_df = pd.read_csv(fpath, delimiter = '\t')
        print(f'microhap file size is {tmp_df.shape}')
        if tmp_df.shape[0] == 0:
            modern_messagebox.showerror(None, "Invalid Input", "microhap table is empty!")
            raise ValueError(f"microhap table is empty!")
        else:
            self.set_cur_microhap_df(tmp_df)
            samples_list = sorted(tmp_df['sample'].unique())
            mar_list = sorted(tmp_df['locus'].unique())
            self.set_cur_mh_samples_list(sorted(set((self.get_cur_mh_samples_list() or []) + samples_list)))
            self.set_cur_mh_markers_list(sorted(set((self.get_cur_mh_markers_list() or []) + mar_list)))

            if len(self.get_cur_mh_markers_list()) == 0:
                modern_messagebox.showerror(None, "Invalid Input", f"microhap file: {fpath} is not valid")
                raise ValueError(f"micorhpa file: {fpath} is not valid")
            if self.get_cur_mh_markers_list() > self.get_ref_markers_list():
                modern_messagebox.showerror(None, "Invalid Input", f"microhap file: {fpath} contains new markers which are not in the ref loci table")
                raise ValueError(f"microhap file: {fpath} contains new markers which are not in the ref loci table")
    
    def read_pre_microhap_file(self, parameter_class):
        #pdb.set_trace()
        fpath = parameter_class.get_pre_microhap_input_file()
        if not os.path.isfile(fpath):
            modern_messagebox.showerror(None, "Invalid Input", f"{fpath} is not a file")
            raise ValueError(f"{fpath} is not a file")
        if len(self.get_cur_microhap_df())==0:
            modern_messagebox.showerror(None, "Invalid Input", f"please read microhap file first before reading pre microhap file") 
            raise ValueError(f"please read microhap file first before reading pre microhap file")
        tmp_df = pd.read_csv(fpath, delimiter = '\t', dtype={'id':'Int64'})
        print_time(f'microhap file size is {tmp_df.shape}')
        if tmp_df.shape[0] == 0:
            parameter_class.set_has_pre_mh(False)
            modern_messagebox.showerror(None, "Invalid Input", "pre-microhap table is empty!")
            raise ValueError(f"pre-microhap table is empty")
        else:
            self.set_pre_microhap_df(tmp_df)
            mar_list = sorted(tmp_df['locus'].unique())
            self.set_pre_mh_markers_list(mar_list)
            if self.get_pre_mh_markers_list() < self.get_ref_markers_list():
                modern_messagebox.showerror(None, "Invalid Input", f"pre microhap file: {fpath} contains new markers which are not in the ref loci table")
                raise ValueError(f"pre microhap file: {fpath} contains new markers which are not in the ref loci table")