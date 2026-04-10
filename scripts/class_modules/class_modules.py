from tkinter import messagebox
from ..utils import modern_messagebox
from concurrent.futures import ProcessPoolExecutor, as_completed
import dill, os
from ..utils.utils_func import output_all_fig_tab, output_all_geno_table, produce_fig_mar_sam_pdf_pool, produce_micro_fig_mar_sam_pdf_pool, produce_micro_fig_sam_mar_pdf_pool
from ..utils.utils_common import print_time
from .snp_class import SnpClass
from .microhap_class import MicroHapClass
from .post_microhap_class import PostMicrohapClass
from .sat_class import SatClass
from .sex_class import SexClass
from .parameter_class import ParameterClass
from .result_parameter_class import ResultParameter
from .read_class import ReadsClass
from .metadata_class import MetaDataClass
from .machine_learning_class import MachineLearningClass
import pandas as pd

class GenotypeClass:
    def __init__(self):
        self._snp = SnpClass()
        self._microhap = MicroHapClass()
        self._post_microhap=PostMicrohapClass()
        self._sat = SatClass()
        self._sex = SexClass()
        self._parameter = ParameterClass()
        self._res_param = ResultParameter()
        self._reads_res=ReadsClass()
        self._metadata=MetaDataClass()
        self._machine_learning = MachineLearningClass()
        self._data_changed=False
    
    def get_machine_learning(self):
        return self._machine_learning
    def set_machine_learning(self, machine_learning):
        self._machine_learning = machine_learning
        
    def get_metadata(self):
        return self._metadata
    def set_metadata(self, metadata):
        self._metadata = metadata
        
    def get_post_microhap(self):
        return self._post_microhap
    def set_post_microhap(self, post_microhap):
        self._post_microhap = post_microhap
    
    def get_data_changed(self):
        return self._data_changed
    def set_data_changed(self, data_changed):
        self._data_changed = data_changed
    
    def get_reads_res(self):
        return self._reads_res
    def set_reads_res(self, reads_res):
        self._reads_res = reads_res
        
    def get_res_param(self):
        return self._res_param
    def set_res_param(self, res_param):
        self._res_param = res_param
        
    def get_snp(self):
        return self._snp

    def set_snp(self, snp):
        try:
            if isinstance(snp, SnpClass):
                self._snp = snp
            else:
                raise ValueError("snp must be an instance of SnpClass")
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))

    # Getter and Setter for microhap
    def get_microhap(self):
        return self._microhap

    def set_microhap(self, microhap):
        try:
            if isinstance(microhap, MicroHapClass):
                self._microhap = microhap
            else:
                raise ValueError("microhap must be an instance of MicroHapClass")
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))

    # Getter and Setter for sat (assuming SatClass is similar)
    def get_sat(self):
        return self._sat

    def set_sat(self, sat):
        try:
            if isinstance(sat, SatClass):
                self._sat = sat
            else:
                raise ValueError("sat must be an instance of SatClass")
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))
    
    def get_sex(self):
        return self._sex
    
    def set_sex(self, sex):
        try:
            if isinstance(sex, SexClass):
                self._sex = sex
            else:
                raise ValueError("sex must be an instance of SexClass")
        except ValueError as e:
            modern_messagebox.showerror(None, "Invalid Input", str(e))

    def get_parameter(self):
        return self._parameter

    def set_parameter(self, parameter):
        try:
            if isinstance(parameter, ParameterClass):
                self._parameter = parameter
            else:
                raise ValueError("parameter must be an instance of ParameterClass")
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))

    def read_sam_outputs(self,sample, run_frame):
        anal_type = self.get_parameter().get_analtype()
        markers = self.get_metadata().get_ref_markers_list()
        fpath = self.get_parameter().get_outputdir()
        print(f"starting to read output of sample: {sample}")
        self.get_microhap().read_sam_genotype(sample,markers, fpath,anal_type, self.get_post_microhap(), self.get_machine_learning(), self.get_parameter())
        run_frame.output_queue.put(f'reading sample {sample} genotype done!\n')
        self.get_microhap().pro_sam_mar_reads_distri_fig(sample,fpath,anal_type)
        run_frame.output_queue.put(f'reading sample {sample} reads done!\n')
        self.get_reads_res().process_json_file(sample,self.get_parameter().get_outputdir())
        run_frame.output_queue.put(f'reading sample {sample} jason file done!\n')
        self.get_reads_res().produce_reads_qual_pdf(sample,self.get_parameter().get_outputdir())
        run_frame.output_queue.put(f'ploting sample {sample} reads quality done!\n')
        print(f"finished to read output of sample: {sample}")

    def pro_all_sample_figs(self, output_queue):
        n_threads = self.get_parameter().get_thread()
        output_queue.put(f'starting to generate quality fig for all samples with {n_threads} threads\n')
        self.get_reads_res().pro_all_sample_qual_fig(self.get_parameter().get_outputdir(), output_queue, n_threads)
        output_queue.put(f'finished to generate quality fig for all samples\n')
        output_queue.put(f'starting to generate reads distributions fig for all samples with {n_threads} threads\n')
        self.get_microhap().pro_all_sample_read_distri_fig_pdf(self.get_parameter().get_outputdir(), output_queue, n_threads)
        output_queue.put(f'finished to generate all reads distributions fig for all samples\n')
    
    def generate_all_sam_microhaps_fig(self, log_func = None)->bool: # to generate figures with with mh names
        print_time('starting to generate microhaps figs for each sample!')
        if log_func is not None:
            log_func(f'starting to generate microhaps figs for each sample!')
        
        n_threads = self.get_parameter().get_thread()
        num_sam = 0
        ouput_folder_path = self.get_parameter().get_post_microhap_output_dir()
        samples=self.get_metadata().get_cur_mh_samples_list()
        markers = self.get_metadata().get_cur_mh_markers_list()
        with ProcessPoolExecutor(max_workers=n_threads) as executor:
            futures = {}
            futures_mp = {}
            for sam in samples:
                sam_mh_dict = {}
                sam_mp_dict = {}
                for mar in markers:
                    mar_mh_ref = self.get_post_microhap().get_loc_ref_dict().get(mar, None)
                    if mar_mh_ref is not None:
                        sam_mh_df = mar_mh_ref.get_final_mar_cur_microhap_nested_dict().get(sam, None)
                        if sam_mh_df is None:
                            sam_mh_df =  pd.DataFrame(
                                {
                                    "id": [f"-9", f"-99"],
                                    "NumReads": [0, 0],
                                    "Allele": ["mh_-9", "mh_-99"],
                                    "Zygosity": ["nan", "nan"]
                                }
                            )
                        sam_mh_dict[mar] = sam_mh_df
                        
                        if mar_mh_ref.get_has_exon():
                            sam_mp_df = mar_mh_ref.get_final_mar_cur_micropep_nested_dict().get(sam, None)
                            if sam_mp_df is None:
                                sam_mp_df =  pd.DataFrame(
                                    {
                                        "id": [f"-9", f"-99"],
                                        "NumReads": [0, 0],
                                        "Allele": ["mp_-9", "mp_-99"],
                                        "Zygosity": ["nan", "nan"]
                                    }
                                )
                            sam_mp_dict[mar] = sam_mp_df
                future = executor.submit(produce_micro_fig_sam_mar_pdf_pool,
                                                    ouput_folder_path,
                                                    markers,
                                                    sam_mh_dict,
                                                    sam)
                futures[future] = sam
                
                if len(sam_mp_dict) > 0:
                    future_mp = executor.submit(produce_micro_fig_sam_mar_pdf_pool,
                                                    ouput_folder_path,
                                                    markers,
                                                    sam_mp_dict,
                                                    sam, 'micropep')
                    futures_mp[future_mp] = sam
            for future in as_completed(futures):
                sam = futures[future]
                try:
                    res = future.result()
                    if not res:
                        print(f'Failed to process sample: {sam}')
                        if log_func is not None:
                            log_func(f'Failed to process sample: {sam}!')
                    num_sam += 1
                    if num_sam % 10 == 0:
                        print(f'Finished processing {num_sam} out of {len(samples)} samples!')
                        if log_func is not None:
                            log_func(f'Finished processing {num_sam} out of {len(samples)} samples for microhap ploting...')
                except Exception as e:
                    print_time(f'Error processing sample: {sam}: {e}')
                    if log_func is not None:
                        log_func(f'Error processing sample: {sam}: {e}')
            for future_mp in as_completed(futures_mp):
                sam = futures_mp[future_mp]
                try:
                    res = future_mp.result()
                    if not res:
                        print(f'Failed to process sample: {sam} for micropep')
                        if log_func is not None:
                            log_func(f'Failed to process sample: {sam} for micropep!')
                except Exception as e:
                    print_time(f'Error processing sample: {sam} for micropep: {e}')
                    if log_func is not None:
                        log_func(f'Error processing sample: {sam} for micropep: {e}')
        print_time('finished to generate microtypes figs for each sample!')
        if log_func is not None:
            log_func(f'finished to generate microtypes figs for each sample!')
        return True
                        
    def generate_all_mar_microhaps_fig(self, log_func = None)->bool: # to generate figures with with mh names
        print_time('starting to generate microhaps figs for each marker')
        if log_func is not None:
            log_func(f'starting to generate microhaps figs for each marker!')
        n_threads = self.get_parameter().get_thread()
        num_mar = 1
        output_folder_path = self.get_parameter().get_post_microhap_output_dir()
        samples=self.get_metadata().get_cur_mh_samples_list()
        markers = self.get_metadata().get_cur_mh_markers_list()
        
        with ProcessPoolExecutor(max_workers=n_threads) as executor:
            futures = {}
            futures_mp = {}
            for mar in markers:
                mar_mh_dict = self.get_post_microhap().get_loc_ref_dict().get(mar, None)
                if mar_mh_dict is not None:
                    mar_mh_final_dict = mar_mh_dict.get_final_mar_cur_microhap_nested_dict() # this is a dict contain all samples for each marker
                    future = executor.submit(produce_micro_fig_mar_sam_pdf_pool,
                                             output_folder_path,
                                             samples,
                                             mar_mh_final_dict,
                                             mar)
                    futures[future] = mar
                    if mar_mh_dict.get_has_exon():
                        mar_mp_final_dict = mar_mh_dict.get_final_mar_cur_micropep_nested_dict()
                        if mar_mp_final_dict is not None or len(mar_mp_final_dict) > 0:
                            future_mp = executor.submit(produce_micro_fig_mar_sam_pdf_pool,
                                                output_folder_path,
                                                samples,
                                                mar_mp_final_dict,
                                                mar, 'micropep')
                            futures_mp[future_mp] = mar
            for future in as_completed(futures):
                mar = futures[future]
                try:
                    res = future.result()
                    if not res:
                        print(f'Failed to process marker: {mar}')
                        if log_func is not None:
                            log_func(f'Failed to process marker: {mar}!')
                    num_mar += 1
                    if num_mar % 10 == 0:
                        print(f'Finished processing {num_mar} out of {len(markers)} markers!')
                        if log_func is not None:
                            log_func(f'Finished processing {num_mar} out of {len(markers)} markers for microhap ploting....')
                except Exception as e:
                    print_time(f'Error processing marker: {mar}: {e}')
                    if log_func is not None:
                        log_func(f'Error processing marker: {mar}: {e}')
            
            if mar_mh_dict.get_has_exon():
                for future_mp in as_completed(futures_mp):
                    mar = futures_mp[future_mp]
                    try:
                        res = future_mp.result()
                        if not res:
                            print(f'Failed to process marker: {mar} for micropep')
                            if log_func is not None:
                                log_func(f'Failed to process marker: {mar} for micropep!')
                    except Exception as e:
                        print_time(f'Error processing marker: {mar} for micropep: {e}')
                        if log_func is not None:
                            log_func(f'Error processing marker: {mar} for micropep: {e}')
        
        print_time('finished to generate microtypes figs for each marker!')
        if log_func is not None:
            log_func(f'finished to generate microtypes figs for each marker!')
        return True                   
                
    def generate_all(self, log_func = None)->bool:
        print_time('starting to process each sample')
        if log_func is not None:
            log_func(f"starting to process each sample!")
        samples=self.get_metadata().get_samples_list()
        anal_type = self.get_parameter().get_analtype()
        markers = self.get_metadata().get_ref_markers_list()
        is_pro_fig = self.get_parameter().is_pro_figure()
        output_folder_path = self.get_parameter().get_outputdir()
        sam_microhap_dict = self.get_microhap().get_sam_microhaps_dir()
        sam_ml_dict = self.get_microhap().get_sam_mar_ml_dict()
        sam_mar_snp_dict = self.get_microhap().get_sam_mar_snp_dict()
        n_threads = self.get_parameter().get_thread()
        #n_threads = self.get_parameter().get_thread()
        num_sam = 0
        with ProcessPoolExecutor(max_workers=n_threads) as executor:
            futures = {executor.submit(output_all_fig_tab, 
                                       is_pro_fig,
                                       output_folder_path,
                                       markers,
                                       sam,
                                       sam_microhap_dict.get(sam, {}), 
                                       sam_ml_dict.get(sam, {}), 
                                       sam_mar_snp_dict.get(sam, {}),
                                       'snp'): sam for sam in samples}
            for future in as_completed(futures):
                sam = futures[future]
                try:
                    res = future.result()
                    if res:
                        #sam_ml_dict[sam] = res
                        num_sam += 1
                        if num_sam % 10 == 0:
                            print(f'Finished processing {num_sam} out of {len(samples)} samples...')
                            if log_func is not None:
                                log_func(f'Finished processing {num_sam} out of {len(samples)} samples...')
                    else:
                        # if sam in sam_ml_dict:
                        #     del sam_ml_dict[sam]
                        print(f'Failed to process sample: {sam}')
                        if log_func is not None:
                            log_func(f"Failed to process sample: {sam}!")
                except Exception as e:
                    modern_messagebox.showerror(None, "Error", f"Error processing sample: {sam}: {e}")
                    print_time(f'Error processing sample: {sam}: {e}')
                    if log_func is not None:
                        log_func(f'Error processing sample: {sam}: {e}')
                    raise
        print(f"finished each sample")
        if log_func is not None:
            log_func(f'Finished samples: {num_sam} out of {len(samples)}')

        if is_pro_fig:
            mar_sam_df_dict = {}
            for mar in markers:
                sam_df_dict = {}
                for sam in samples:
                    if sam in self.get_microhap().get_sam_microhaps_dir():
                        sam_df_dict[sam] = self.get_microhap().get_sam_microhaps_dir()[sam].get(mar, None)
                mar_sam_df_dict[mar] = sam_df_dict
            futures=list()
            print(f'starting to process all the markers')
            if log_func is not None:
                log_func(f'starting to process all the markers!')
            num_mar = 0
            with ProcessPoolExecutor(max_workers=n_threads) as executor:
                futures = {executor.submit(produce_fig_mar_sam_pdf_pool, 
                                           output_folder_path, 
                                           samples,
                                           mar_sam_df_dict.get(mar, {}),
                                           mar, 'snp'):mar for mar in markers}
                for future in as_completed(futures):
                    mar = futures[future]
                    try:
                        res=future.result()
                        if res:
                            num_mar += 1
                            if num_mar % 10 == 0:
                                if log_func is not None:
                                    log_func(f'Finished {num_mar} out of {len(markers)} markers...')
                        else:
                            print(f'Failed to process marker: {mar}')
                            if log_func is not None:
                                    log_func(f'Failed marker {mar}!')
                    except Exception as e:
                        modern_messagebox.showerror(None, "Error", f"Error processing marker: {mar}: {e}")
                        print(f'Error processing marker: {mar}: {e}')
                        if log_func is not None:
                                    log_func(f'Error processing marker: {mar}: {e}')
            print(f'finished to process all the markers')
            if log_func is not None:
                log_func(f'finished to process all the markers')
            del mar_sam_df_dict
        print(f"begin to process all_sample geno table")
        if log_func is not None:
            log_func(f'begin to process all_sample geno table!')
        output_all_geno_table(self, anal_type)
        print(f'finished to process all the sample geno table')
        if log_func is not None:
            log_func(f'begin to process all_sample geno table!')
        return True

    def dump_session(self, project, log_func = None)->bool:
        try:
            output_path = ""
            print_time(f"Starting to dump session for project: {project}")
            if log_func is not None:
                log_func(f"Starting to dump session for project: {project}")
            if project == "genotype":
                output_path = self.get_parameter().get_outputgenotypeproject()
                self.get_parameter().set_project_genotype_model(True)
                self.get_parameter().set_project_microtype_model(False)
            elif project == "microtype":
                output_path = self.get_parameter().get_outputmicrotypeproject()
                self.get_parameter().set_project_microtype_model(True)
                self.get_parameter().set_project_genotype_model(False)
            else:
                modern_messagebox.showerror(None, "Invalid Project Output", f"Unknown project type: {project}")
                if log_func is not None:
                    log_func(f"Unknown project type: {project}")
                return False
            with open(output_path, 'wb') as f:
                dill.dump(self, f)
                if log_func is not None:
                    log_func(f"Session successfully saved to: {output_path}")
            print_time(f"Session successfully saved to: {output_path}")
            return True
        except Exception as e:
            modern_messagebox.showerror(None, "Error Saving Session", str(e))
            print_time(f"Error saving session: {e}")
            if log_func is not None:
                log_func(f"Error saving session: {e}")
            return False

    def check_project_files(self, parent=None) -> bool:
        output_path = self.get_parameter().get_projectdir()
        if not os.path.exists(output_path) or not os.path.isdir(output_path):
            print(f"Output directory does not exist: {output_path}")
            modern_messagebox.showerror(parent, "Directory Not Found", f"Output directory does not exist: {output_path}")
            return False
        
        genotype_project_file = os.path.join(output_path, 'project_genotype_session.dill')
        microtype_project_file = os.path.join(output_path, 'project_microtype_session.dill')
        
        go_genotype = False
        go_microtype = False
        if os.path.isfile(genotype_project_file):
            go_genotype = True
        if os.path.isfile(microtype_project_file):
            go_microtype = True
        
        if not go_genotype and not go_microtype:
            print(f"No project file found in output directory: {output_path}")
            modern_messagebox.showerror(parent, "Project File Not Found", f"No project file found in output directory: {output_path}")
            return False
        
        if go_genotype and go_microtype:
            print(f"Both genotype and microtype project files found in output directory: {output_path}")
            modern_messagebox.showerror(parent, "Multiple Project Files Found", f"Both genotype 'project_genotype_session.dill' and microtype 'project_microtype_session.dill' project files found in output directory: {output_path}. Please ensure only one project file is present.")
            return False
        
        if go_genotype and not go_microtype:
            print(f"Genotype project file found: {genotype_project_file}")
            self.get_parameter().set_outputdir(output_path)
            self.get_parameter().set_project_genotype_model(True)
            self.get_parameter().set_project_microtype_model(False)
        elif go_microtype and not go_genotype:
            print(f"Microtype project file found: {microtype_project_file}")
            self.get_parameter().set_post_microhap_output_dir(output_path)
            self.get_parameter().set_project_microtype_model(True)
            self.get_parameter().set_project_genotype_model(False)
        
        if self.get_parameter().is_project_genotype_model() and self.get_parameter().is_project_microtype_model():
            print(f"Project parameter indicates both genotype and microtype projects are selected, which is invalid.")
            modern_messagebox.showerror(parent, "Invalid Project File", f"Project parameter indicates both genotype and microtype projects are selected, which is invalid. Please check the project settings.")
            return False
        
        if not self.get_parameter().is_project_genotype_model() and not self.get_parameter().is_project_microtype_model():
            print(f"Project parameter indicates neither genotype nor microtype projects are selected, which is invalid.")
            modern_messagebox.showerror(parent, "Invalid Project File", f"Project parameter indicates neither genotype nor microtype projects are selected, which is invalid. Please check the project settings.")
            return False
        return True
    
    def load_session(self, parent=None) -> bool:
        try:        
            input_path = ""
            project = ""
            if self.get_parameter().is_project_genotype_model() and not self.get_parameter().is_project_microtype_model():
                print(f"Found genotype project file: {self.get_parameter().get_outputgenotypeproject()}")
                input_path = self.get_parameter().get_outputgenotypeproject()
                project = "genotyping"
            elif self.get_parameter().is_project_microtype_model() and not self.get_parameter().is_project_genotype_model():
                print(f"Found microtype project file: {self.get_parameter().get_outputmicrotypeproject()}")
                input_path = self.get_parameter().get_outputmicrotypeproject()
                project = "microtyping"
            else:
                print(f"No valid project file found in output directory:")
                modern_messagebox.showerror(parent, "Project File Not Found", f"No valid project file found in output directory.")
                return False
            
            print_time(f"Starting to load session from: {input_path}")
            # Load the saved object
            with open(input_path, 'rb') as f:
                print_time(f"File opened successfully, loading session...")
                loaded_obj = dill.load(f)
                print_time(f"Session loaded, verifying type...")
            # Optional: verify type (optional but safe)
            if not isinstance(loaded_obj, self.__class__):
                modern_messagebox.showerror(parent, "Type Mismatch", f"Loaded object is not a {self.__class__.__name__} instance.")
                return False
            # Update current instance with loaded data
            self.__dict__.update(loaded_obj.__dict__)
            
            if project == "genotyping":
                self.get_parameter().set_project_genotype_model(True)
                self.get_parameter().set_project_microtype_model(False)
                self.get_res_param().set_res_type("sample")
                self.get_parameter().set_outputdir(os.path.dirname(input_path))
            elif project == "microtyping":
                self.get_parameter().set_project_microtype_model(True)
                self.get_parameter().set_project_genotype_model(False)
                self.get_parameter().set_post_microhap_output_dir(os.path.dirname(input_path))
            else:
                modern_messagebox.showerror(parent, "Invalid Project File", f"Unknown project type in loaded session: {project}")
                print_time(f"Unknown project type in loaded session: {project}")
                return False
            print_time(f"Session successfully loaded")
            return True
        except FileNotFoundError:
            modern_messagebox.showerror(parent, "File Not Found", f"No file found at: {input_path}")
            return False
        except Exception as e:
            modern_messagebox.showerror(parent, "Error Loading Session", f"Failed to load session from {input_path}\n\n{str(e)}")
            return False