import os

class ParameterClass:
    def __init__(self):
        self._analtype = "snp"
        self._seqtype="pe"
        self._sexfile = ""
        self._locifile = ""
        self._inputdir = ""
        self._outputdir = ""
        self._samplefile = ""
        self._mlinputfile = ""
        self._mloutputdir = ""
        self._mlmodelinputfile = ""
        self._mlmodel = False
        self._num_samples = 0
        
        self._project_genotype_model = False
        self._project_microtype_model = False
        self._outputgenotypeproject = "project_genotype_session.dill"
        self._outputmicrotypeproject = "project_microtype_session.dill"
        
        self._maxMismatchesPSeq = 2
        self._minSeqs = 5
        self._htJetter = 20
        self._hmPerH = 90
        self._hmPerL = 80
        self._minSeqsPerSnp = 10
        self._minReads4Filter = 10
        
        self._nanopore_default = False
        
        self._revcomloci = False
        self._revcomsex = False
        
        self._average_qual = 20
        self._length_required = 30
        
        self._thread = 10
        
        self._cur_microhap_input_file = "" #for microhap module, the whole folder contain all the microhap files
        self._pre_microhap_input_file = "" #for premicrohap file
        self._post_microhap_output_dir = "" #for microhap output folder
        
        self._include_pre_mh = True
        self._has_pre_mh = False
        self._pro_figure = True
    
    def is_mlmodel(self):
        return self._mlmodel
    def set_mlmodel(self, mlmodel):
        self._mlmodel = mlmodel
    
    def set_mlinputfile(self, mlinputfile):
        self._mlinputfile = mlinputfile
    def get_mlinputfile(self):
        return self._mlinputfile
    
    def set_mloutputdir(self, mloutputdir):
        self._mloutputdir = mloutputdir
    def get_mloutputdir(self):
        return self._mloutputdir
    
    def set_mlmodelinputfile(self, mlmodelinputfile):
        self._mlmodelinputfile = mlmodelinputfile
    def get_mlmodelinputfile(self):
        return self._mlmodelinputfile
    
    def is_pro_figure(self):
        return self._pro_figure
    def set_pro_figure(self, pro_figure):
        self._pro_figure = pro_figure if isinstance(pro_figure, bool) else bool(pro_figure)
        
    def get_has_pre_mh(self):
        return self._has_pre_mh
    def set_has_pre_mh(self, has_pre_mh):
        self._has_pre_mh = has_pre_mh if isinstance(has_pre_mh, bool) else bool(has_pre_mh)
        
    def get_include_pre_mh(self):
        return self._include_pre_mh
    
    def set_include_pre_mh(self, include_pre_mh):
        self._include_pre_mh = include_pre_mh if isinstance(include_pre_mh, bool) else bool(include_pre_mh)
    
    def get_cur_microhap_input_file(self):
        return self._cur_microhap_input_file
    
    def set_cur_microhap_input_file(self, cur_microhap_input_file):
        self._cur_microhap_input_file = cur_microhap_input_file if isinstance(cur_microhap_input_file, str) else str(cur_microhap_input_file)
        if not os.path.isfile(self._cur_microhap_input_file):
            raise ValueError("Invalid post-microhap input file path does not exist.")
    
    def get_pre_microhap_input_file(self):
        return self._pre_microhap_input_file
    def set_pre_microhap_input_file(self, pre_microhap_input_file):
        self._pre_microhap_input_file = pre_microhap_input_file if isinstance(pre_microhap_input_file, str) else str(pre_microhap_input_file)
        if not os.path.isfile(self._pre_microhap_input_file):
            raise ValueError("Invalid pre-microhap input file")
    def get_post_microhap_output_dir(self):
        return self._post_microhap_output_dir
    def set_post_microhap_output_dir(self, post_microhap_output_dir):
        self._post_microhap_output_dir = post_microhap_output_dir if isinstance(post_microhap_output_dir, str) else str(post_microhap_output_dir)
        if not os.path.isdir(self._post_microhap_output_dir):
            raise ValueError("Invalid microhap output directory path. Directory does not exist.")
        
    def get_thread(self):
        return self._thread
    def set_thread(self, thread):
        self._thread = thread if isinstance(thread, int) else int(thread)
        if self._thread < 1 or self._thread > 100:
            raise ValueError("Invalid number of threads. Must be between 1 and 100")
    
    def get_nanopore_default(self):
        return self._nanopore_default
    def set_nanopore_default(self, nanopore_default):
        self._nanopore_default = nanopore_default
    
    def get_length_required(self):
        return self._length_required
    def set_length_required(self, length_required):
        self._length_required = length_required if isinstance(length_required, int) else int(length_required)
        if self._length_required < 10 or self._length_required > 1000:
            raise ValueError("Invalid length required. Must be between 10 and 1000")
    
    def get_average_qual(self):
        return self._average_qual
    def set_average_qual(self, average_qual):
        self._average_qual = average_qual if isinstance(average_qual, int) else int(average_qual)
        if self._average_qual < 0 or self._average_qual > 30:
            raise ValueError("Invalid average quality score. Must be between 0 and 40")
    
    def get_revcomsex(self):
        return self._revcomsex
    def set_revcomsex(self, revcomsex):
        self._revcomsex = revcomsex
        
    def get_revcomloci(self):
        return self._revcomloci
    def set_revcomloci(self, revcomloci):
        self._revcomloci = revcomloci
        
    def get_minReads4Filter(self):
         return self._minReads4Filter
    def set_minReads4Filter(self, minReads4Filter):
         self._minReads4Filter = minReads4Filter if isinstance(minReads4Filter, int) else int(minReads4Filter)
         if self._minReads4Filter < 1 or self._minReads4Filter > 1000:
             raise ValueError("Invalid minimum number of reads for filtering. Must be between 1 and 1000")
     
    def get_minSeqsPerSnp(self):
         return self._minSeqsPerSnp
    def set_minSeqsPerSnp(self, minSeqsPerSnp):
         self._minSeqsPerSnp = minSeqsPerSnp if isinstance(minSeqsPerSnp, int) else int(minSeqsPerSnp)
         if self._minSeqsPerSnp < 1 or self._minSeqsPerSnp > 1000:
             raise ValueError("Invalid minimum number of sequences per SNP. Must be between 1 and 1000")
     
    def get_hmPerL(self):
         return self._hmPerL
    def set_hmPerL(self, hmPerL):
         self._hmPerL = hmPerL
         if self._hmPerL > 90:
             raise ValueError("Invalid hmPerL threshold. Must be between 1 and 90")
         
    def get_hmPerH(self):
        return self._hmPerH
    
    def set_mPerH(self, hmPerH):
        self._hmPerH = hmPerH
        if self._hmPerH > 100:
            raise ValueError("Invalid mPerH threshold. Must be between 1 and 90")
        
    def get_htJetter(self):
        return self._htJetter
    
    def set_htJetter(self, htJetter):
        self._htJetter = htJetter
        if self._htJetter < 1 or self._htJetter > 20:
            raise ValueError("Invalid HtJetter threshold. Must be between 1 and 50")
    
    def get_minSeqs(self):
        return self._minSeqs
    
    def set_minSeqs(self, minSeqs):
        self._minSeqs = minSeqs if isinstance(minSeqs, int) else int(minSeqs)
        if self._minSeqs < 1:
            raise ValueError("Invalid minimum number of sequences. Must be between 1 and 1000")    
    
    def get_maxMismatchesPSeq(self):
        return self._maxMismatchesPSeq
    
    def set_maxMismatchesPSeq(self, maxMismatchesPSeq):
        self._maxMismatchesPSeq = maxMismatchesPSeq if isinstance(maxMismatchesPSeq, int) else int(maxMismatchesPSeq)
        if self._maxMismatchesPSeq < 0 or self._maxMismatchesPSeq > 5:
            raise ValueError("Invalid maximum mismatches percentage. Must be between 0 and 5")
    
    def get_analtype(self):
        return self._analtype
    
    def set_analtype(self, analtype):
        self._analtype = analtype
        if self._analtype not in ["sat", "snp"]:
            raise ValueError("Invalid analysis type. Must be 'sat' or 'snp'")
    
    def get_seqtype(self):
        return self._seqtype
    
    def set_seqtype(self, seqtype):
        self._seqtype = seqtype
        if self._seqtype not in ["pe", "se"]:
            raise ValueError("Invalid sequence type. Must be 'pe' or'se'")
    
    def get_sexfile(self):
        return self._sexfile
    
    def set_sexfile(self, sexfile):
        self._sexfile = sexfile
        if not os.path.isfile(self._sexfile):
            raise ValueError(f"Sex file '{self._sexfile}' does not exist")
        
    def get_locifile(self):
        return self._locifile
    def set_locifile(self, locifile):
        self._locifile = locifile
        if not os.path.isfile(self._locifile):
            raise ValueError(f"Loc file '{self._locifile}' does not exist")

    def get_inputdir(self):
        return self._inputdir
    def set_inputdir(self, inputdir):
        self._inputdir = inputdir
        if not os.path.isdir(self._inputdir):
            raise ValueError(f"Input directory '{self._inputdir}' does not exist")
        
    def get_outputdir(self):
        return self._outputdir
    def set_outputdir(self, outputdir):
        self._outputdir = outputdir
        if not os.path.isdir(self._outputdir):
            raise ValueError(f"Output directory '{self._outputdir}' does not exist")

    def is_project_genotype_model(self):
        return self._project_genotype_model
    def set_project_genotype_model(self, gmodel):
        self._project_genotype_model = gmodel
    
    def is_project_microtype_model(self):
        return self._project_microtype_model
    def set_project_microtype_model(self, mmodel):
        self._project_microtype_model = mmodel
        
    def get_outputgenotypeproject(self):
        return os.path.join(self._outputdir, self._outputgenotypeproject)
    
    def get_outputmicrotypeproject(self):
        return os.path.join(self._outputdir, self._outputmicrotypeproject)
    
    def get_samplefile(self):
        return self._samplefile
    def set_samplefile(self, samplefile):
        self._samplefile = samplefile
        if not os.path.isfile(self._samplefile):
            raise ValueError(f"Sample file '{self._samplefile}' does not exist")
    def get_num_samples(self):
        return self._num_samples
    
    def set_num_samples(self, num_samples):
        self._num_samples = num_samples
        if self._num_samples <= 0:
            raise ValueError("Number of samples must be a positive integer")