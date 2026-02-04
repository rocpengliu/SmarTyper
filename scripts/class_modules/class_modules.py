from tkinter import messagebox
from ..utils import modern_messagebox
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor, as_completed
import dill
from ..utils.utils_func import output_all_fig_tab, produce_fig_mar_sam_pdf, output_all_geno_table, produce_fig_mar_sam_pdf_pool
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
    
    def generate_all(self):
        print_time('starting to process each the sample')
        samples=self.get_metadata().get_samples_list()
        anal_type = self.get_parameter().get_analtype()
        markers = self.get_metadata().get_ref_markers_list()
        is_pro_fig = self.get_parameter().is_pro_figure()
        output_folder_path = self.get_parameter().get_outputdir()
        sam_microhap_dict = self.get_microhap().get_sam_microhaps_dir()
        n_threads = self.get_parameter().get_thread() // 2 if self.get_parameter().get_thread() >= 2 else 1
        #n_threads = self.get_parameter().get_thread()
        with ProcessPoolExecutor(max_workers=n_threads) as executor:
            sam_ml_dict = self.get_microhap().get_sam_mar_ml_dir()
            futures = {executor.submit(output_all_fig_tab, 
                                       is_pro_fig,
                                       output_folder_path,
                                       markers,
                                       sam,
                                       sam_microhap_dict.get(sam, {}), 
                                       sam_ml_dict.get(sam, {}), 
                                       'snp'): sam for sam in samples}
            for future in as_completed(futures):
                sam = futures[future]
                try:
                    res = future.result()
                    if res:
                        sam_ml_dict[sam] = res
                        print(f'Finished processing sample: {sam}')
                    else:
                        if sam in sam_ml_dict:
                            del sam_ml_dict[sam]
                        print(f'Failed to process sample: {sam}')
                except Exception as e:
                    modern_messagebox.showerror(None, "Error", f"Error processing sample: {sam}: {e}")
                    print_time(f'Error processing sample: {sam}: {e}')
        print(f"finished each sample")

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
                        if not res:
                            print(f'Failed to process marker: {mar}')
                    except Exception as e:
                        modern_messagebox.showerror(None, "Error", f"Error processing marker: {mar}: {e}")
                        print(f'Error processing marker: {mar}: {e}')
            print(f'finished to process all the markers')
            del mar_sam_df_dict
        print(f"begin to process all_sample geno table")
        output_all_geno_table(self, anal_type)
        print(f'finished to process all the sample geno table')

    def dump_session(self, project):
        try:
            print_time(f"Starting to dump session for project: {project}")
            if project == "genotype":
                output_path = self.get_parameter().get_outputgenotypeproject()
            elif project == "microtype":
                output_path = self.get_parameter().get_outputmicrotypeproject()
            else:
                modern_messagebox.showerror(None, "Invalid Project Output", f"Unknown project type: {project}")
                return
            with open(output_path, 'wb') as f:
                dill.dump(self, f)
            print_time(f"Session successfully saved to: {output_path}")
        except Exception as e:
            modern_messagebox.showerror(None, "Error Saving Session", str(e))

    def load_session(self, project, parent=None):
        try:
            # Determine input path based on project type
            print_time(f"Starting to load session from: {input_path}")
            if project == "genotype":
                input_path = self.get_parameter().get_outputgenotypeproject()
            elif project == "microtype":
                input_path = self.get_parameter().get_outputmicrotypeproject()
            else:
                modern_messagebox.showerror(parent, "Invalid Project Input", f"Unknown project type: {project}")
                return False
            # Load the saved object
            with open(input_path, 'rb') as f:
                loaded_obj = dill.load(f)
            # Optional: verify type (optional but safe)
            if not isinstance(loaded_obj, self.__class__):
                modern_messagebox.showerror(parent, "Type Mismatch", f"Loaded object is not a {self.__class__.__name__} instance.")
                return False
            # Update current instance with loaded data
            self.__dict__.update(loaded_obj.__dict__)
            if project == "genotype":
                self.get_parameter().set_project_genotype_model(True)
                self.get_res_param().set_res_type("sample")
            elif project == "microtype":
                self.get_parameter().set_project_microtype_model(True)
            else:
                modern_messagebox.showerror(parent, "Invalid Project Input", f"Unknown project type: {project}")
                return False
            print_time(f"Session successfully loaded")
            return True
        except FileNotFoundError:
            modern_messagebox.showerror(parent, "File Not Found", f"No file found at: {input_path}")
            return False
        except Exception as e:
            modern_messagebox.showerror(parent, "Error Loading Session", f"Failed to load session from {input_path}\n\n{str(e)}")
            return False