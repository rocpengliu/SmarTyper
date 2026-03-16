import os
import pandas as pd
from ..utils import modern_messagebox
from ..utils.common import micro_microhap_df_columns, micro_microhap_df_empty_row, micro_amplicon_df_columns, micro_amplicon_df_empty_row, ml_mh_df_columns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from ..utils.utils_common import print_time, thread_lock
from ..utils.utils_alignment import do_pairwise_alignment
from ..utils.utils_func import produce_reads_dis_fig, generate_page, init_sam_mar_ml, init_sam_microhaps, init_sam_amplicons, init_assigned_reads
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor, as_completed
from ..utils.modern_messagebox import showerror
import pdb

class MicroHapClass:
    def __init__(self):
        self._microhap_file = ""
        self._samples = pd.DataFrame()
        self._microhaps = pd.DataFrame()
        self._loci = pd.DataFrame()
        self._sam_amplicons_dir = {}# is {mar = {}}, nested dic
        self._sam_microhaps_dir = {}
        #self._sam_mar_ml_dir = {} # this is a nested dic {sam: {mar:}}
        self._sam_mar_ml_dict = {} # {sample : mar = {}}
        self._sam_mar_snp_dict = {} # {sample : mar = { new_snp_pos:[]}}
        #self._microhap_dict = {}#nested {marker:{seq:nm}}
        self._assigned_reads_dict={}#nested dictionary {sam, and each markers are the keys,}
        self._assigned_sam_reads_dict={}# sam is the key and total assigned reads for each marker is the value
    
    # def get_sam_mar_ml_dir(self):
    #     return self._sam_mar_ml_dir
    # def set_sam_mar_ml_dir(self, sam_mar_ml_dir):
    #     self._sam_mar_ml_dir = sam_mar_ml_dir
    def get_assigned_sam_reads_dict(self):
        return self._assigned_sam_reads_dict
    def set_assigned_sam_reads_dict(self, assigned_sam_reads_dict):
        self._assigned_sam_reads_dict = assigned_sam_reads_dict
    
    def get_assigned_reads_dict(self):
        return self._assigned_reads_dict
    
    def set_assigned_reads_dict(self, assigned_reads_dict):
        try:
            if isinstance(assigned_reads_dict, dict):
                self._assigned_reads_dict = assigned_reads_dict
            else:
                raise ValueError("assigned_reads_dict must be a dictionary")
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))
            
    def get_microhap_file(self):
        return self._microhap_file

    def set_microhap_file(self, microhap_file):
        try:
            if isinstance(microhap_file, str):
                if os.path.isfile(microhap_file):
                    self._microhap_file = microhap_file
                else:
                    raise ValueError("The specified microhap file does not exist.")
            else:
                raise ValueError("microhap_file must be a string")
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))
            
    def get_samples(self):
        return self._samples

    def set_samples(self, samples):
        try:
            if isinstance(samples, pd.DataFrame):
                self._samples = samples
            else:
                raise ValueError("samples must be a pandas DataFrame")
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))

    def get_microhaps(self):
        return self._microhaps

    def set_microhaps(self, microhaps):
        try:
            if isinstance(microhaps, pd.DataFrame):
                self._microhaps = microhaps
            else:
                raise ValueError("microhaps must be a pandas DataFrame")
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))

    # Getter and Setter for loci
    def get_loci(self):
        return self._loci

    def set_loci(self, loci):
        try:
            if isinstance(loci, pd.DataFrame):
                self._loci = loci
            else:
                raise ValueError("loci must be a pandas DataFrame")
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))
    
    # Getter and Setter for amplicons
    def get_sam_amplicons_dir(self):
        return self._sam_amplicons_dir

    def set_sam_amplicons_dir(self, sam_amplicons_dir):
        try:
            if isinstance(sam_amplicons_dir, dict):
                self._sam_amplicons_dir = sam_amplicons_dir
            else:
                raise ValueError("amplicons must be a dictionary")
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))

    def get_sam_microhaps_dir(self):
        return self._sam_microhaps_dir

    def set_sam_microhaps_dir(self, sam_microhaps_dir):
        try:
            if isinstance(sam_microhaps_dir, dict):
                self._sam_microhaps_dir = sam_microhaps_dir
            else:
                raise ValueError("microhap must be a dictionary")
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))

    def get_sam_mar_ml_dict(self):
        return self._sam_mar_ml_dict
    
    def set_sam_mar_ml_dict(self, sam_mar_ml_dict):
        self._sam_mar_ml_dict = sam_mar_ml_dict
    
    def get_sam_mar_snp_dict(self):
        return self._sam_mar_snp_dict
    
    def set_sam_mar_snp_dict(self, sam_mar_snp_dict):
        self._sam_mar_snp_dict = sam_mar_snp_dict
    
    def read_amplicon_file(self, file, mars, sample, post_microhap_class):
        print_time(f"starting to read sample {sample} amplicon file")
        tmp_df = pd.DataFrame()
        mars_amplicon = {}
        if os.path.isfile(file):
            tmp_df = pd.read_csv(file, delimiter = '\t',
                                 dtype = {
                                     'sample': str,
                                     'locus': str,
                                     'readt': int,
                                     'reads': int,
                                     'prop': float,
                                     'baseChange': str,
                                     'len': int,
                                     'seq': str
                                 })
        else:
            print_time(f"Warning: Sample {sample} {type} file not found")
        num_reads=0
        for mar in mars:
            #mar_ref = post_microhap_class.get_loc_ref_dict().get(mar, None)
            if os.path.isfile(file):
                tmp = tmp_df.query(f'locus == "{mar}"')
                if tmp is None or tmp.empty:
                    mars_amplicon[mar] = pd.DataFrame(columns=micro_amplicon_df_columns)
                    row0=micro_amplicon_df_empty_row[:]
                    row0[:2]=(sample,mar)
                    row0[-1]=f"{mar}_0"
                    mars_amplicon[mar].loc[0]=row0
                    row1=micro_amplicon_df_empty_row[:]
                    row1[:2]=(sample,mar)
                    row1[-1]=f"{mar}_1"
                    mars_amplicon[mar].loc[1]=row1
                else:
                    #pdb.set_trace()
                    tmp = tmp.reset_index(drop=True)
                    tmp = tmp.pipe(lambda df : df.assign(id=df['locus'] + '_' + df.index.astype(str)))
                    mars_amplicon[mar] = tmp
                    self._assigned_reads_dict[sample][mar]=tmp['readt'].iloc[0]
                    num_reads+=tmp['readt'].iloc[0]
            else:
                mars_amplicon[mar] = pd.DataFrame(columns=micro_amplicon_df_columns)
                row0=micro_amplicon_df_empty_row[:]
                row0[:2]=(sample,mar)
                row0[-1]=f"{mar}_0"
                mars_amplicon[mar].loc[0]=row0
                row1=micro_amplicon_df_empty_row[:]
                row1[:2]=(sample,mar)
                row1[-1]=f"{mar}_1"
                mars_amplicon[mar].loc[1]=row1
        self._assigned_sam_reads_dict[sample]=num_reads
        print_time(f"finished to read sample {sample} amplicon file")
        return mars_amplicon
    
    def read_mh_file(self, file, mars, sample, post_microhap_class, machine_learning_class, parameter_class):
        print_time(f"starting to read sample {sample} mh file")
        tmp_df = pd.DataFrame()
        mh_amplicon = {}
        if os.path.isfile(file):
            tmp_df = pd.read_csv(file, delimiter = '\t',
                                 dtype={
                                     'sample': str,
                                     'locus': str,
                                     'allele': str,
                                     'readt': int,
                                     'read': int,
                                     'rprop': float,
                                     'mprop': float,
                                     'sprop': float,
                                     'mut': str,
                                     'indel': str,
                                     'zygosity': str,
                                     'baseChange': str,
                                     'seq': str
                                 })
        else:
            print_time(f"Warning: Sample {sample} mh file not found")
        for mar in mars:
            mar_ref = post_microhap_class.get_loc_ref_dict().get(mar, None)
            ref_seq = ""
            if mar_ref is not None:
                ref_seq = mar_ref.get_dna_ref()
            if os.path.isfile(file):
                tmp = tmp_df.query(f'locus == "{mar}"')
                if tmp is None or tmp.empty:
                    mh_amplicon[mar] = pd.DataFrame(columns=micro_microhap_df_columns)
                    row0=micro_microhap_df_empty_row[:]
                    row0[:2]=(sample,mar)
                    row0[-1]=f"{mar}_0"
                    mh_amplicon[mar].loc[0]=row0
                    row1=micro_microhap_df_empty_row[:]
                    row1[:2]=(sample,mar)
                    row1[2]=1
                    row1[-1]=f"{mar}_1"
                    mh_amplicon[mar].loc[1]=row1
                else:
                    #pdb.set_trace()
                    tmp = tmp.reset_index(drop=True)
                    tmp = tmp.pipe(lambda df : df.assign(id=df['locus'] + '_' + df.index.astype(str)))
                    # if 'numreads' in tmp.columns:
                    #     tmp['numreads'] = pd.to_numeric(tmp['numreads'], errors='coerce')
                    #totsnpstr = ""
                    snpstr_ref0 = ""
                    snpstr_ref1 = ""
                    #snpstr_ref2=""
                    ref1 = tmp.at[0, 'seq']
                    ref2 = tmp.at[1, 'seq'] if tmp.shape[0] > 1 else ""
                    _, _, snpstr_ref0 = do_pairwise_alignment(ref1, ref_seq, mar_ref.get_triml(), True)
                    if ref2 != "":
                        _, _, snpstr_ref1 = do_pairwise_alignment(ref2, ref_seq, mar_ref.get_triml(), True)
                        # _, newsnppos, _ = do_pairwise_alignment(ref1, ref2, mar_ref.get_triml(), True)
                        # self._sam_mar_snp_dict.setdefault(sample, {}).setdefault(mar, {})['new_snp_pos'] = newsnppos

                        #totsnpstr = snpstr_ref0 + ";" + snpstr_ref1 + ";" + snpstr_ref2
                    tmp.at[0, 'baseChange'] = snpstr_ref0
                    if tmp.shape[0] > 1 and ref2 != "":
                        tmp.at[1, 'baseChange'] = snpstr_ref1
                        
                    ml_tmp = None
                    if parameter_class.is_mlmodel():
                        if machine_learning_class.get_mh_training_model_clf_dict() and mar in machine_learning_class.get_mh_training_model_clf_dict():
                            ml_tmp = self.get_sam_mar_ml_dict().get(sample, {}).get(mar, None)
                            if ml_tmp is not None:
                                predict = machine_learning_class.predict_zygosity(parameter_class, mar, ml_tmp)
                                if predict is not None:
                                    if predict[0] == 1:
                                        tmp['zygosity'] = "homo"
                                    elif predict[0] == 2:
                                        tmp['zygosity'] = "heter"
                                    else:
                                        tmp['zygosity'] = "inconclusive"
                                    ml_tmp['zygosity'] = predict
                                    self._sam_mar_ml_dict.setdefault(sample, {})[mar] = ml_tmp
                    mh_amplicon[mar] = tmp
            else:
                mh_amplicon[mar] = pd.DataFrame(columns=micro_microhap_df_columns)
                row0=micro_microhap_df_empty_row[:]
                row0[:2]=(sample,mar)
                row0[-1]=f"{mar}_0"
                mh_amplicon[mar].loc[0]=row0
                row1=micro_microhap_df_empty_row[:]
                row1[:2]=(sample,mar)
                row1[2]=1
                row1[-1]=f"{mar}_1"
                mh_amplicon[mar].loc[1]=row1
        print_time(f"finished to read sample {sample} mh file")
        return mh_amplicon
    
    def read_ml_file(self, file, mars, sample):
        print_time(f"starting to read ml file for sample: {sample}")
        ml_mar_dict = {}
        tmp_df = pd.DataFrame()
        if os.path.isfile(file):
            tmp_df = pd.read_csv(
                file,
                delimiter='\t',
                dtype={
                    'sample': str,
                    'locus': str,
                    'readt': int,
                    'read1': int,
                    'read2': int,
                    'read3': int,
                    'rprop1': float,
                    'rprop2': float,
                    'rprop3': float,
                    'mprop1': float,
                    'mprop2': float,
                    'sprop': float,
                    'mut': int,
                    'indel': int,
                    'zygosity': int,
                },
            )
        else:
            print_time(f"Warning: {sample} ml file is not found!")
            return ml_mar_dict
        
        for mar in mars:
            tmp_mar_df = tmp_df[tmp_df['locus'] == mar]
            if not tmp_mar_df.empty:
                ml_mar_dict[mar] = tmp_mar_df.head(1)
        print_time(f"finished to read ml file for sample: {sample}")
        return ml_mar_dict
    
    def read_snp_file(self, file, mars, sample):
        print_time(f"starting to read snp file for sample: {sample}")
        mar_snp_dict = {}
        tmp_df = pd.DataFrame()
        if os.path.isfile(file):
            tmp_df = pd.read_csv(
                file,
                delimiter='\t',
                dtype={
                    'sample': str,
                    'locus': str,
                    'position': int,
                    'allele1': str,
                    'allele2': str,
                    'allele3': str,
                    'reads': str,
                    'proportion': float,
                    'totHapReads': int,
                    'new': str,
                    'conclusive': str
                },
            )
        else:
            print_time(f"Warning: {sample} snp file is not found!")
            return mar_snp_dict
        
        for mar in mars:
            tmp_mar_df = tmp_df[tmp_df['locus'] == mar]
            if not tmp_mar_df.empty:
                mar_snp_dict[mar] = tmp_mar_df
        print_time(f"finished to read snp file for sample: {sample}")
        return mar_snp_dict
    
    def read_sam_genotype(self,sample,markers,fpath,anal_type, post_microhap_class, machine_learning_class, parameter_class):
        print_time(f"starting to read geno output file for sample: {sample}")
        if anal_type == "snp":
            print_time(f"starting to read ml output file for sample: {sample}")
            ml_path = os.path.join(fpath, sample + "_sample_ml.txt")
            ml_dict = self.read_ml_file(ml_path, markers, sample)
            self._sam_mar_ml_dict[sample] = ml_dict
            
            print_time(f"starting to read microhap output file for sample: {sample}")
            microhap_path = os.path.join(fpath, sample + "_sample_haplotype.txt")
            microhap_dir = self.read_mh_file(microhap_path, markers, sample, post_microhap_class, machine_learning_class, parameter_class)
            self._sam_microhaps_dir[sample]=microhap_dir
            
            print_time(f"starting to read amplicon output file for sample: {sample}")
            amplicon_path = os.path.join(fpath, sample + "_sample_amplicon.txt")
            amplicon_dir = self.read_amplicon_file(amplicon_path, markers, sample, post_microhap_class)
            self._sam_amplicons_dir[sample]=amplicon_dir
            
            print_time(f"starting to read snp file for sample: {sample}")
            snp_path = os.path.join(fpath, sample + "_sample_snp.txt")
            snp_dict = self.read_snp_file(snp_path, markers, sample)
            self._sam_mar_snp_dict[sample] = snp_dict
            
        print_time(f"finished to read geno output file for sample: {sample}")

    def init_sam_mar_dicts(self,genotype_class):
        anal_type = genotype_class.get_parameter().get_analtype()
        samples=genotype_class.get_metadata().get_samples_list()
        markers=genotype_class.get_metadata().get_ref_markers_list()
        n_threads=genotype_class.get_parameter().get_thread() # this is not intiated yet, should the default one is set to maximum cpu number???
        print_time(f"begain to initiate sam_mar_dict")
        if anal_type == "snp":
            print_time(f"begain to initiate dicts")
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = {executor.submit(init_assigned_reads, markers, samples) : "assigned_reads_dict"}
                futures.update({executor.submit(init_sam_microhaps, markers, samples) : "sam_micro_dir"})
                futures.update({executor.submit(init_sam_amplicons, markers, samples) : "sam_amp_dir"})
                futures.update({executor.submit(init_sam_mar_ml, markers, samples) : "sam_mar_ml_dir"})
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        if futures[future] == "assigned_reads_dict":
                            self.set_assigned_reads_dict(result)
                            print_time(f"finished to initiate assigned_reads_dict")
                        elif futures[future] == "sam_micro_dir":
                            self.set_sam_microhaps_dir(result)
                            print_time(f"finished to initiate sam_micro_dir")
                        elif futures[future] == "sam_amp_dir":
                            self.set_sam_amplicons_dir(result)
                            print_time(f"finished to initiate sam_amp_dir")
                        elif futures[future] == "sam_mar_ml_dir":
                            self.set_sam_mar_ml_dict(result)
                            print_time(f"finished to initiate sam_mar_ml_dir")
                    except Exception as exc:
                        print(f"Error initializing {futures[future]}: {exc}")
            print_time(f"finished to initiate dicts")
        else:
            pass
        print_time(f"finished to initiate sam_mar_dict")

    def pro_mar_sam_reads_distri_fig(self,mar, samples, fpath,anal_type):
        data_dict = {}
        for sam in samples:
            df = self.get_sam_amplicons_dir().get(sam).get(mar)
            data_dict[sam] = df['readt'].iloc[0]
        sorted_data={k:v for k,v in sorted(data_dict.items(),
                                           key=lambda item:item[1],
                                           reverse=True)}
        pdf_file=os.path.join(fpath,f"{mar}_locus_reads_distribution.pdf")
        with PdfPages(pdf_file) as pdf:
            bars_per_subplot=10
            num_subplots_per_page=4
            bars_per_page=bars_per_subplot*num_subplots_per_page
            num_pages=len(sorted_data)/bars_per_page
            if num_pages%1 == 0:
                num_pages=int(num_pages)
            else:
                num_pages=int(num_pages)+1
            n_page=0
            fig, axs = None, None
            for i in range(num_pages):
                fig,axs=produce_reads_dis_fig(i,num_pages,sorted_data,bars_per_page,bars_per_subplot,num_subplots_per_page)
                if fig is not None:
                    fig.suptitle(f"Reads distribution of locus: {mar}",fontsize=16,x=0.5,y=0.95,horizontalalignment='center')
                    fig.text(0.08,0.5,'n. of reads',va='center',rotation='vertical')
                    fig.text(0.5,0.01,f'page{n_page+1}',ha='center',fontsize=8)
                    n_page+=1
                    pdf.savefig(fig)
                    plt.close(fig)

    def pro_sam_mar_reads_distri_fig(self,sample,fpath,anal_type):
        data_dict=self.get_assigned_reads_dict().get(sample)
        sorted_data={k:v for k,v in sorted(data_dict.items(),
                                           key=lambda item:item[1],
                                           reverse=True)}
        pdf_file=os.path.join(fpath,f"{sample}_sample_reads_distribution.pdf")
        with PdfPages(pdf_file) as pdf:
            bars_per_subplot=10
            num_subplots_per_page=4
            bars_per_page=bars_per_subplot*num_subplots_per_page
            num_pages=len(sorted_data)/bars_per_page
            if num_pages%1 == 0:
                num_pages=int(num_pages)
            else:
                num_pages=int(num_pages)+1
            n_page=0
            fig, axs = None, None
            for i in range(num_pages):
                fig,axs=produce_reads_dis_fig(i,num_pages,sorted_data,bars_per_page,bars_per_subplot,num_subplots_per_page)
                if fig is not None:
                    fig.suptitle(f"Reads distribution of sample: {sample}",fontsize=16,x=0.5,y=0.95,horizontalalignment='center')
                    fig.text(0.08,0.5,'n. of reads',va='center',rotation='vertical')
                    fig.text(0.5,0.01,f'page{n_page+1}',ha='center',fontsize=8)
                    n_page+=1
                    pdf.savefig(fig)
                    plt.close(fig)

    def pro_all_sample_read_distri_fig_pdf(self, fpath, output_queue, n_threads=4):
        print_time(f"starting to produce sample read distribution fig")
        output_queue.put(f'starting to produce sample read distribution fig!\n')
        data_dict=self.get_assigned_sam_reads_dict()
        sorted_data={k:v for k,v in sorted(data_dict.items(),
                                           key=lambda item:item[1],
                                           reverse=True)}
        pdf_file=os.path.join(fpath,f"All_sample_read_distribution.pdf")
        
        bars_per_subplot=10
        num_subplots_per_page=4
        bars_per_page=bars_per_subplot*num_subplots_per_page
        num_pages=len(sorted_data)/bars_per_page
        if num_pages%1 == 0:
            num_pages=int(num_pages)
        else:
            num_pages=int(num_pages)+1
        
        # Generate pages in parallel and collect results
        page_figures = {}
        with ProcessPoolExecutor(max_workers=n_threads) as executor:
            futures = {executor.submit(
                generate_page, i, num_pages, sorted_data, bars_per_page, bars_per_subplot, num_subplots_per_page
                ): i for i in range(num_pages)}
            for future in as_completed(futures):
                try:
                    page_num, fig = future.result()
                    if fig is not None:
                        page_figures[page_num] = fig
                except Exception as exc:
                    print(f"Error generating page {futures[future]}: {exc}")
        
        # Save pages in correct order to PDF
        with PdfPages(pdf_file) as pdf:
            for i in range(num_pages):
                if i in page_figures:
                    pdf.savefig(page_figures[i])
                    plt.close(page_figures[i])
        
        print_time(f"finish to produce sample read distribution fig")
        output_queue.put(f'finished to produce sample read distribution fig!\n')
  