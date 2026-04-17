import os
from scripts.utils.modern_messagebox import showerror

class ParameterClass:
    def __init__(self):
        self._analtype = "snp"
        self._seqtype="pe"
        self._sexfile = ""
        self._locifile = ""
        self._inputdir = ""
        self._outputdir = ""
        self._projectdir = ""
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
        
        self._maxMismatchesPSeq = 4
        self._minReads4Locus = 30
        self._minReads4Allele = 10
        self._smProp1H = 0.80
        self._smProp1L = 0.72
        self._mmProp1H = 0.80
        self._mmProp1L = 0.78
        self._mProp2 = 0.70
        #self._sProp3 = 0.80
        #self._minSeqsProSnp = 0.1
        self._maxRVs4Align = 6
        
        self._maxMismatchesPSeqSex = 4
        self._maxMismatchesRefSeqSex = 4
        self._yxRatio = 0.0001
        self._minReadsSexAllele = 10
        self._minReadsSexVariant = 5
        self._sex_analysis = False
        
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
    
    def get_sex_analysis(self):
        return self._sex_analysis
    def set_sex_analysis(self, sex_analysis):
        self._sex_analysis = sex_analysis if isinstance(sex_analysis, bool) else bool(sex_analysis)
    def get_maxMismatchesPSeqSex(self):
        return self._maxMismatchesPSeqSex
    def set_maxMismatchesPSeqSex(self, maxMismatchesPSeqSex):
        self._maxMismatchesPSeqSex = maxMismatchesPSeqSex if isinstance(maxMismatchesPSeqSex, int) else int(maxMismatchesPSeqSex)
        if self._maxMismatchesPSeqSex < 0 or self._maxMismatchesPSeqSex > 5:
            showerror("Invalid maximum mismatches percentage for sex typing", "Invalid maximum mismatches percentage for sex typing. Must be between 0 and 5.")
            raise ValueError("Invalid maximum mismatches percentage for sex typing. Must be between 0 and 5")
    def get_maxMismatchesRefSeqSex(self):
        return self._maxMismatchesRefSeqSex
    def set_maxMismatchesRefSeqSex(self, maxMismatchesRefSeqSex):
        self._maxMismatchesRefSeqSex = maxMismatchesRefSeqSex if isinstance(maxMismatchesRefSeqSex, int) else int(maxMismatchesRefSeqSex)
        if self._maxMismatchesRefSeqSex < 0 or self._maxMismatchesRefSeqSex > 5:
            showerror("Invalid maximum mismatches percentage for reference sequence typing", "Invalid maximum mismatches percentage for reference sequence typing. Must be between 0 and 5.")
            raise ValueError("Invalid maximum mismatches percentage for reference sequence typing. Must be between 0 and 5")
    def get_yxRatio(self):
        return self._yxRatio
    def set_yxRatio(self, yxRatio):
        self._yxRatio = yxRatio if isinstance(yxRatio, float) else float(yxRatio)
        if self._yxRatio < 0 or self._yxRatio > 1:
            showerror("Invalid Y/X ratio threshold for sex typing", "Invalid Y/X ratio threshold for sex typing. Must be between 0 and 1.")
            raise ValueError("Invalid Y/X ratio threshold for sex typing. Must be between 0 and 1")
    def get_minReadsSexAllele(self):
        return self._minReadsSexAllele
    def set_minReadsSexAllele(self, minReadsSexAllele):
        self._minReadsSexAllele = minReadsSexAllele if isinstance(minReadsSexAllele, int) else int(minReadsSexAllele)
        if self._minReadsSexAllele < 1 or self._minReadsSexAllele > 1000:
            showerror("Invalid minimum number of reads for sex allele", "Invalid minimum number of reads for sex allele. Must be between 1 and 1000.")
            raise ValueError("Invalid minimum number of reads for sex allele. Must be between 1 and 1000")
    def get_minReadsSexVariant(self):
        return self._minReadsSexVariant
    def set_minReadsSexVariant(self, minReadsSexVariant):
        self._minReadsSexVariant = minReadsSexVariant if isinstance(minReadsSexVariant, int) else int(minReadsSexVariant)
        if self._minReadsSexVariant < 1 or self._minReadsSexVariant > 1000:
            showerror("Invalid minimum number of reads for sex variant", "Invalid minimum number of reads for sex variant. Must be between 1 and 1000.")
            raise ValueError("Invalid minimum number of reads for sex variant. Must be between 1 and 1000")
        
        
    def get_minReads4Locus(self):
        return self._minReads4Locus
    def set_minReads4Locus(self, minReads4Locus):
        self._minReads4Locus = minReads4Locus if isinstance(minReads4Locus, int) else int(minReads4Locus)
        if self._minReads4Locus < 1:
            showerror("Invalid minimum number of reads for a locus", "Invalid minimum number of reads for a locus. Must be at least 1.")
            raise ValueError("Invalid minimum number of reads for a locus. Must be at least 1")
    
    def get_minReads4Allele(self):
        return self._minReads4Allele
    def set_minReads4Allele(self, minReads4Allele):
        self._minReads4Allele = minReads4Allele if isinstance(minReads4Allele, int) else int(minReads4Allele)
        if self._minReads4Allele < 1:
            showerror("Invalid minimum number of reads for an allele", "Invalid minimum number of reads for an allele. Must be at least 1.")
            raise ValueError("Invalid minimum number of reads for an allele. Must be at least 1")

    def get_maxRVs4Align(self):
        return self._maxRVs4Align
    def set_maxRVs4Align(self, maxRVs4Align):
        self._maxRVs4Align = maxRVs4Align if isinstance(maxRVs4Align, int) else int(maxRVs4Align)
        if self._maxRVs4Align < 3:
            showerror("Invalid maximum number of read variants for alignment", "Invalid maximum number of read variants for alignment. Must be at least 3.")
            raise ValueError("Invalid maximum number of read variants for alignment. Must be at least 3")
        
    def get_mProp2(self):
        return self._mProp2
    def set_mProp2(self, mProp2):
        if mProp2 < 0 or mProp2 > 1:
            showerror("Invalid mProp2 threshold", "Invalid mProp2 threshold. Must be between 0 and 1" )
            raise ValueError("Invalid mProp2 threshold. Must be between 0 and 1")
        self._mProp2 = mProp2
    # def get_sProp3(self):
    #     return self._sProp3
    
    # def set_sProp3(self, sProp3):
    #     if sProp3 < 0 or sProp3 > 1:
    #         showerror("Invalid sProp3 threshold", "Invalid sProp3 threshold. Must be between 0 and 1" )
    #         raise ValueError("Invalid sProp3 threshold. Must be between 0 and 1")
    #     self._sProp3 = sProp3
    
    def get_smProp1H(self):
        return self._smProp1H
    
    def set_smProp1H(self, smProp1H):
        if smProp1H < 0 or smProp1H > 1:
            showerror("Invalid sProH threshold", "Invalid sProH threshold. Must be between 0 and 1" )
            raise ValueError("Invalid sProH threshold. Must be between 0 and 1")
        self._smProp1H = smProp1H
    
    def get_smProp1L(self):
        return self._smProp1L
    
    def set_smProp1L(self, smProp1L):
        if smProp1L < 0 or smProp1L > 1:
            showerror("Invalid sProL threshold", "Invalid sProL threshold. Must be between 0 and 1" )
            raise ValueError("Invalid sProL threshold. Must be between 0 and 1")
        self._smProp1L = smProp1L
    
    def get_mmProp1H(self):
        return self._mmProp1H
    
    def set_mmProp1H(self, mmProp1H):
        if mmProp1H < 0 or mmProp1H > 1:
            showerror("Invalid mmProp1H threshold", "Invalid mmProp1H threshold. Must be between 0 and 1" )
            raise ValueError("Invalid mmProp1H threshold. Must be between 0 and 1")
        self._mmProp1H = mmProp1H
        
    def get_mmProp1L(self):
        return self._mmProp1L
    
    def set_mmProp1L(self, mmProp1L):
        if mmProp1L < 0 or mmProp1L > 1:
            showerror("Invalid mmProp1L threshold", "Invalid mmProp1L threshold. Must be between 0 and 1" )
            raise ValueError("Invalid mmProp1L threshold. Must be between 0 and 1")
        self._mmProp1L = mmProp1L
    
    
    def check_parameters_valid(self):
        if self._smProp1L > self._smProp1H:
            showerror("Invalid sPro thresholds", "Invalid sPro thresholds. sProL threshold cannot be greater than sProH threshold.")
            raise ValueError("Invalid sPro thresholds. sProL threshold cannot be greater than sProH threshold.")      
        if self._mmProp1L > self._mmProp1H:
            showerror("Invalid msPro thresholds", "Invalid msPro thresholds. mmProp1L threshold cannot be greater than mmProp1H threshold.")
            raise ValueError("Invalid msPro thresholds. mmProp1L threshold cannot be greater than mmProp1H threshold.")
    
    def set_projectdir(self, projectdir):
        self._projectdir = projectdir
        
    def get_projectdir(self):
        return self._projectdir
    
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
            showerror("Invalid microtype input file", "Invalid microtype input file. File does not exist.")
            raise ValueError("Invalid post-microtype input file path does not exist.")
    
    def get_pre_microhap_input_file(self):
        return self._pre_microhap_input_file
    def set_pre_microhap_input_file(self, pre_microhap_input_file):
        self._pre_microhap_input_file = pre_microhap_input_file if isinstance(pre_microhap_input_file, str) else str(pre_microhap_input_file)
        if not os.path.isfile(self._pre_microhap_input_file):
            showerror("Invalid pre-microtype input file", "Invalid pre-microtype input file. File does not exist.")
            raise ValueError("Invalid pre-microtype input file")
    def get_post_microhap_output_dir(self):
        return self._post_microhap_output_dir
    def set_post_microhap_output_dir(self, post_microhap_output_dir):
        self._post_microhap_output_dir = post_microhap_output_dir if isinstance(post_microhap_output_dir, str) else str(post_microhap_output_dir)
        if not os.path.isdir(self._post_microhap_output_dir):
            showerror("Invalid microtype output directory", "Invalid microtype output directory. Directory does not exist.")
            raise ValueError("Invalid microtype output directory path. Directory does not exist.")
        
    def get_thread(self):
        return self._thread
    def set_thread(self, thread):
        self._thread = thread if isinstance(thread, int) else int(thread)
        if self._thread < 1 or self._thread > 100:
            showerror("Invalid number of threads", "Invalid number of threads. Must be between 1 and 100.")
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
            showerror("Invalid length required", "Invalid length required. Must be between 10 and 1000.")
            raise ValueError("Invalid length required. Must be between 10 and 1000")
    
    def get_average_qual(self):
        return self._average_qual
    def set_average_qual(self, average_qual):
        self._average_qual = average_qual if isinstance(average_qual, int) else int(average_qual)
        if self._average_qual < 0 or self._average_qual > 30:
            showerror("Invalid average quality score", "Invalid average quality score. Must be between 0 and 30.")
            raise ValueError("Invalid average quality score. Must be between 0 and 30")
    
    def get_revcomsex(self):
        return self._revcomsex
    def set_revcomsex(self, revcomsex):
        self._revcomsex = revcomsex
        
    def get_revcomloci(self):
        return self._revcomloci
    def set_revcomloci(self, revcomloci):
        self._revcomloci = revcomloci
    
    def get_maxMismatchesPSeq(self):
        return self._maxMismatchesPSeq
    
    def set_maxMismatchesPSeq(self, maxMismatchesPSeq):
        self._maxMismatchesPSeq = maxMismatchesPSeq if isinstance(maxMismatchesPSeq, int) else int(maxMismatchesPSeq)
        if self._maxMismatchesPSeq < 0 or self._maxMismatchesPSeq > 5:
            showerror("Invalid maximum mismatches percentage", "Invalid maximum mismatches percentage. Must be between 0 and 5.")
            raise ValueError("Invalid maximum mismatches percentage. Must be between 0 and 5")
    
    def get_analtype(self):
        return self._analtype
    
    def set_analtype(self, analtype):
        self._analtype = analtype
        if self._analtype not in ["sat", "snp"]:
            showerror("Invalid analysis type", "Invalid analysis type. Must be 'sat' or 'snp'.")
            raise ValueError("Invalid analysis type. Must be 'sat' or 'snp'")
    
    def get_seqtype(self):
        return self._seqtype
    
    def set_seqtype(self, seqtype):
        self._seqtype = seqtype
        if self._seqtype not in ["pe", "se"]:
            showerror("Invalid sequence type", "Invalid sequence type. Must be 'pe' or 'se'.")
            raise ValueError("Invalid sequence type. Must be 'pe' or 'se'")
    
    def get_sexfile(self):
        return self._sexfile
    
    def set_sexfile(self, sexfile):
        self._sexfile = sexfile
        if not os.path.isfile(self._sexfile):
            showerror("Invalid sex file", "Invalid sex file. File does not exist.")
            raise ValueError(f"Sex file '{self._sexfile}' does not exist")
        
    def get_locifile(self):
        return self._locifile
    def set_locifile(self, locifile):
        self._locifile = locifile
        if not os.path.isfile(self._locifile):
            showerror("Invalid loci file", "Invalid loci file. File does not exist.")
            raise ValueError(f"Loc file '{self._locifile}' does not exist")

    def get_inputdir(self):
        return self._inputdir
    def set_inputdir(self, inputdir):
        self._inputdir = inputdir
        if not os.path.isdir(self._inputdir):
            showerror("Invalid input directory", "Invalid input directory. Directory does not exist.")
            raise ValueError(f"Input directory '{self._inputdir}' does not exist")
        
    def get_outputdir(self):
        return self._outputdir
    def set_outputdir(self, outputdir):
        self._outputdir = outputdir
        if not os.path.isdir(self._outputdir):
            showerror("Invalid output directory", "Invalid output directory. Directory does not exist.")
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
        return os.path.join(self._post_microhap_output_dir, self._outputmicrotypeproject)
    
    def get_samplefile(self):
        return self._samplefile
    def set_samplefile(self, samplefile):
        self._samplefile = samplefile
        if not os.path.isfile(self._samplefile):
            showerror("Invalid sample file", "Invalid sample file. File does not exist.")
            raise ValueError(f"Sample file '{self._samplefile}' does not exist")
    def get_num_samples(self):
        return self._num_samples
    
    def set_num_samples(self, num_samples):
        self._num_samples = num_samples
        if self._num_samples <= 0:
            showerror("Invalid number of samples", "Number of samples must be a positive integer")
            raise ValueError("Number of samples must be a positive integer")