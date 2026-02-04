import os
import pandas as pd
from ..utils.utils_common import print_time
import json
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from ..utils.utils_func import process_sample_for_pool
class ReadsClass:
    def __init__(self):
        self._sam_reads_dict={}#nested dictionary with sam as the key, and each marker as the key
        self._sam_reads_qual_dict={}
    def get_sam_reads_qual_dict(self):
        return self._sam_reads_qual_dict
    def set_sam_reads_qual_dict(self,sam_reads_qual_dict):
        self._sam_reads_qual_dict=sam_reads_qual_dict
    def get_sam_reads_dict(self):
        return self._sam_reads_dict
    def set_sam_reads_dict(self,sam_reads_dict):
        self._sam_reads_dict=sam_reads_dict
    def process_json_file(self,sam,dir_path):
        print(f"starting to read json output file for sample: {sam}")
        json_file=os.path.join(dir_path,f"{sam}.json")
        if os.path.isfile(json_file):
            with open(json_file, 'r') as file:
                jdata = json.load(file)
                self.process_reads_qual(sam,jdata)
                self.process_reads_quat(sam,jdata)
        print(f"finished to read json output file for sample: {sam}")
    def process_reads_quat(self,sam,jdata):
        reads_dict={}
        reads_dict['total_reads']=jdata.get('summary').get('after_filtering').get('total_reads')
        reads_dict['clean_reads']=jdata.get('summary').get('after_filtering').get('total_reads')
        self._sam_reads_dict[sam]=reads_dict

    def process_reads_qual(self,sam,jdata):
        read_qual_dic={}
        read_qual_dic['qual1b']=self.extract_qual(jdata,1,'before',sam)
        read_qual_dic['qual1a']=self.extract_qual(jdata,1,'after',sam)
        if len(jdata.get('read2_before_filtering').get('quality_curves').get('A'))!=0:
            read_qual_dic['qual2b']=self.extract_qual(jdata,2,'before',sam)
            read_qual_dic['qual2a']=self.extract_qual(jdata,2,'after',sam)
        if len(read_qual_dic)==0:
            return
        self._sam_reads_qual_dict[sam]=read_qual_dic
    def produce_reads_qual_pdf(self,sam,dir_path):
        #combined_df=pd.concat(read_qual_dic.values(),axis=0,ignore_index=True)
        read_qual_dic=self._sam_reads_qual_dict[sam]
        combined_dfs = [df.dropna(axis=1, how='all') for df in read_qual_dic.values()]
        combined_df = pd.concat(combined_dfs, axis=0, ignore_index=True)
        gra=sns.FacetGrid(combined_df,col='filtering',row='read',hue='base',margin_titles=True)
        gra.map(sns.lineplot,'cycle','quality').add_legend()
        gra.set_axis_labels('Cycles','Quality score')
        fig = gra.figure
        fig.set_size_inches(16,10)
        fig.suptitle(f'Quality score of {sam}',fontsize=14)
        plt.subplots_adjust(top=0.95)
        gra.savefig(os.path.join(dir_path,f"{sam}_read_quality.pdf"))
        if fig is not None:
            plt.close()
            
    def extract_qual(self, jdata,idx,type,sam)->pd.DataFrame:
        filter_str=f"read{idx}_{type}_filtering"
        adata=jdata.get(filter_str).get('quality_curves').get('A')
        cdata=jdata.get(filter_str).get('quality_curves').get('C')  
        gdata=jdata.get(filter_str).get('quality_curves').get('G')
        tdata=jdata.get(filter_str).get('quality_curves').get('T')
        mean_quality=np.mean([adata,cdata,gdata,tdata],axis=0)
        qual_df=(pd.DataFrame({
                    'cycle':range(1,len(adata)+1),
                    'A':adata,
                    'G':gdata,
                    'T':tdata,
                    'C':cdata,
                    'mean':mean_quality,
                    'read':f"read{idx}",
                    'filtering':f"{type}",
                    'sample':f'{sam}'
                })).pipe(pd.melt, id_vars=['cycle','read','filtering', 'sample'],var_name='base',value_name='quality')
        return qual_df
    def pro_all_sample_qual_fig(self, dir_path, output_queue, n_threads=4):
        print_time(f"starting to produce sample quality fig")
        output_queue.put(f'starting to produce sample quality fig!\n')
        combined_dic = {}

        # Prepare arguments as a list of tuples
        sample_args = list(self._sam_reads_qual_dict.items())
        # Use ProcessPoolExecutor for parallel processing
        with ProcessPoolExecutor(max_workers=n_threads) as executor:
            futures = {executor.submit(process_sample_for_pool, arg): arg[0] for arg in sample_args}
            for future in as_completed(futures):
                try:
                    sam, result_df = future.result()
                    combined_dic[sam] = result_df
                except Exception as exc:
                    print(f"Error processing sample {futures[future]}: {exc}")

        output_queue.put(f'finished to combined_dic for quality fig!\n')
        combined_dfs = [df.dropna(axis=1, how='all') for df in combined_dic.values()]
        combined_df = pd.concat(combined_dfs, axis=0, ignore_index=True)
        output_queue.put(f'starting to facetgrid for quality fig!\n')
        # gra=sns.FacetGrid(combined_df,col='filtering',row='read',hue='sample',margin_titles=True)
        # output_queue.put(f'map line for quality fig, it is slow, please be patient!\n')
        # gra.map(sns.lineplot,'cycle','quality', alpha=0.5).add_legend()
        # output_queue.put(f'map line for quality fig!\n')
        # gra.set_axis_labels('Cycle','Quality score')
        # fig=gra.figure
        # output_queue.put(f'generate quality fig!\n')
        # fig.set_size_inches(16,10)
        # fig.suptitle("Quality score of all samples", fontsize=14)
        # plt.subplots_adjust(top=0.85)
        # output_queue.put(f'finished to draw quality fig!\n')
        # gra.savefig(os.path.join(dir_path,"all_sample_read_quality.pdf"))
        # if fig is not None:
        #     plt.close()
        # print_time("finished to produce sample quality fig")
        
        sns.relplot(
            data=combined_df,
            x="cycle",  # X-axis is cycle
            y="quality",  # Y-axis is quality score
            hue="sample",  # Color by sample
            kind="line",  # Line plot type
            col="filtering",  # Column-wise facet based on 'filtering'
            errorbar = None, 
            row="read",  # Row-wise facet based on 'read'
            height=5,  # Height of each facet
            aspect=1.5,  # Aspect ratio of each facet
            legend=False if len(self._sam_reads_qual_dict) > 20 else True
        )
    
        output_queue.put(f'finished plotting quality fig!\n')
        
        # Adjust the figure size and title
        plt.subplots_adjust(top=0.85)
        plt.suptitle("Quality score of all samples", fontsize=14)
        
        # Save the plot as a PDF
        output_file = os.path.join(dir_path, "All_sample_read_quality.pdf")
        plt.savefig(output_file)
        
        # Close the plot to release memory
        plt.close()
            
        print_time(f"finished to produce sample quality fig")
        output_queue.put(f'finished to produce sample quality fig!\n')
