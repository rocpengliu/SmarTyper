# SmarTyper

## Description

**SmarTyper** is a novel, smart, comprehensive and interfaced-based platform for microtype (microhaplotype & micropeptype) genotyping from targeted sequencing data.

## Key features of SmarTyper

* **Multifunctional**: conducts genotyping for SNPs, microhaplotypes, and micropeptypes.

* **Smart**: supports smart genotyping powered by AI.

* **Interactive**: supports both automated and manual genotyping with interactive plotting.

* **Ultra-fast**: about 5 seconds per sample using a single thread.

* **All-in-one**: SmarTyper takes raw targeted sequencing reads as input and outputs genotype tables.

* **Reads-to-report files**: generates genotype tables, figures for report.

## Getting started
### Step 1. Pre-installations
SmarTyper is implemented in Python/Cython and C/C++11, and is designed to run on Linux.
We have tested SmarTyper on Windows Subsystem for Linux 2 (WSL2) and on Linux systems using XFCE.

#### Install system dependencies:
```bash
sudo apt update
sudo apt install python3-full python3-tk python3-pip mafft
python3 -m pip install --upgrade pip
python3 -m pip install --break-system-packages setuptools Cython customtkinter biopython pillow matplotlib dill logomaker seaborn joblib scikit-learn
```
Note: `--break-system-packages` may be required on newer Ubuntu releases when installing into the system Python environment.

### Step 2. Clone and set up SmarTyper

```bash
git clone https://github.com/rocpengliu/SmarTyper.git
cd SmarTyper
```

### Step 3. Compile the C++ extension

```bash
python3 setup.py clean --all && python3 setup.py build_ext --inplace
```

### Step 4. Launch SmarTyper

```bash
python3 smartyper.py
```

### Step 6. Process your data

Please try the example data in folder example_data and follow the tutorial.


## Seq2Type as a standalone software tool
run seq2type

```bash
cd example_data;
python3 ../seq2type.py -i raw_data/sample_1_R1.fastq.gz -I raw_data/sample_1_R2.fastq.gz --loc loc_combined.txt --var snp --prefix sample_1 -w 12 -V

```

```
seq2type for genotyping

options:
  --var VAR             genetic variance, must be either microsatellite/ssr or snp
  -i IN1, --in1 IN1     read1 input file name
  -I IN2, --in2 IN2     read2 input file name
  -X PREFIX, --prefix PREFIX
                        prefix name for output files, eg: sample01
  --outFReads           If specified, off-target reads will be outputed in a file
  -o OUT1, --out1 OUT1  file name to store read1 with on-target sequences
  -O OUT2, --out2 OUT2  file name to store read2 with on-target sequences
  --nanopore_default    If specified, use the default settings (mainly about Q score) of nanopore sequencing
  --loc LOC             loci file containing loci names, primers, flanking regions, etc.
  --revCom              if your reverse primer sequence in the loc file is not reverse complentary, please specify it
  --minReads4Locus MINREADS4LOCUS
                        minimum number of reads for a locus, default: 30
  --maxMismatchesPSeq MAXMISMATCHESPSEQ
                        maximum mismatches for primer sequences 4, default: 4
  --noPlot              If specified, do not plot
  --mode MODE           specify the sequence alignment mode: NW (default) | HW | SHW
  --maxScore MAXSCORE   maximum score of sequence alignment, sequences with score > maxScore will be discarded
  --numBestSeqs NUMBESTSEQS
                        Score will be calculated only for N best sequences
  --notFindAlignment    If specified, alignment path will be not found and printed
  --findStartLocation   If specified, start locations will be found and printed
  --format FORMAT       Format for alignment path: NICE|CIG_STD|CIG_EXT
  --core CORE           Core part of calculation will be repeated N times
  --silentAlignment     If specified, there will be no score or alignment output
  --printResults        If specified, alignment results will be printed but with only 1 thread
  --maxMismatchesPer4FR MAXMISMATCHESPER4FR
                        maximum percentage mismatches for flanking regions, default 0.3 (30%)
  --minSeqsPercentage MINSEQSPERCENTAGE
                        minimum percentage reads against largest peak for a genotype, default: 5 (5%)
  --minWarningSeqs MINWARNINGSEQS
                        minimum number of reads for warning a genotype, default: 50
  --hlRatio1 HLRATIO1   ratio of loci sizes when length difference = 1 ssr unit, default: 0.4
  --hlRatio2 HLRATIO2   ratio of loci sizes when length difference = 2 ssr unit, default: 0.2
  --maxVarRatio MAXVARRATIO
                        ratio of two heter alleles, default: 1.5
  --smProp1H SMPROP1H   homo threshold when one true SNP, default: 0.80
  --smProp1L SMPROP1L   heter threshold when one true SNP, default: 0.72
  --mmProp1H MMPROP1H   homo threshold when >= two true SNPs, default: 0.78
  --mmProp1L MMPROP1L   heter threshold when >= two true SNPs, default: 0.80
  --mProp2 MPROP2       heter threshold for read2/read3 proportion, default: 0.7
  --minReads4Allele MINREADS4ALLELE
                        minimum reads for filtering an allele, read1 for homo and read2 for heter, default: 10
  --maxRVs4Align MAXRVS4ALIGN
                        maximum number of read variants for alignment table, must be > 2 rows. default: 6
  --noSnpPlot           If specified, do not plot SNPs
  --noErrorPlot         If specified, do not plot error rate
  --sex SEX             sex loci file containing sex locus names, primers, reference sequences
  --maxMismatchesSexPSeq MAXMISMATCHESSEXPSEQ
                        maximum number of mismatches for sex primers, default: 2
  --maxMismatchesSexRefSeq MAXMISMATCHESSEXREFSEQ
                        maximum number of mismatches for sex reference sequences, default: 2
  --yxRatio YXRATIO     minimum ratio of numbers of reads Y/X to W/Z, default: 0.001
  --minReadsSexAllele MINREADSSEXALLELE
                        minimum number of reads assigned to each sex allele of X or Y; default: 10
  --minReadsSexVariant MINREADSSEXVARIANT
                        minimum number of reads assigned to each sex variant of X or Y; default: 5
  --debug               If specified, print debug
  -j JSON, --json JSON  the json format report file name
  --html HTML           the html format report file name
  -R REPORT_TITLE, --report_title REPORT_TITLE
                        report title
  --help                show this help message and exit
  -w THREAD, --thread THREAD
                        worker thread number, default is 4
  -6, --phred64         indicate the input is using phred64 scoring
  -z COMPRESSION, --compression COMPRESSION
                        compression level for gzip output (1 ~ 9)
  --stdin               input from STDIN
  --stdout              stream passing-filters reads to STDOUT
  --interleaved_in      indicate that <in1> is an interleaved FASTQ
  --reads_to_process READS_TO_PROCESS
                        specify how many reads/pairs to be processed. Default 0 means process all reads
  --dont_overwrite      don't overwrite existing files
  -V, --verbose         output verbose log information
  -A, --disable_adapter_trimming
                        adapter trimming is enabled by default. If this option is specified, adapter trimming is disabled
  -a ADAPTER_SEQUENCE, --adapter_sequence ADAPTER_SEQUENCE
                        the adapter for read1
  --adapter_sequence_r2 ADAPTER_SEQUENCE_R2
                        the adapter for read2
  --adapter_fasta ADAPTER_FASTA
                        specify a FASTA file to trim both read1 and read2
  --detect_adapter_for_pe
                        enable auto-detection for adapter for PE data
  -f TRIM_FRONT1, --trim_front1 TRIM_FRONT1
                        trimming how many bases in front for read1, default is 0
  -t TRIM_TAIL1, --trim_tail1 TRIM_TAIL1
                        trimming how many bases in tail for read1, default is 0
  -b MAX_LEN1, --max_len1 MAX_LEN1
                        if read1 is longer than max_len1, then trim read1 at its tail
  -F TRIM_FRONT2, --trim_front2 TRIM_FRONT2
                        trimming how many bases in front for read2
  -T TRIM_TAIL2, --trim_tail2 TRIM_TAIL2
                        trimming how many bases in tail for read2
  -B MAX_LEN2, --max_len2 MAX_LEN2
                        if read2 is longer than max_len2, then trim read2 at its tail
  --poly_g_min_len POLY_G_MIN_LEN
                        the minimum length to detect polyG in the read tail. 10 by default
  -G, --disable_trim_poly_g
                        disable polyG tail trimming
  -x, --trim_poly_x     enable polyX trimming in 3' ends
  --poly_x_min_len POLY_X_MIN_LEN
                        the minimum length to detect polyX in the read tail. 10 by default
  -5, --cut_front       move a sliding window from front (5') to tail, drop the bases in the window if its mean quality < threshold
  -3, --cut_tail        move a sliding window from tail (3') to front, drop the bases in the window if its mean quality < threshold
  -r, --cut_right       move a sliding window from front to tail, if meet one window with mean quality < threshold, drop the bases
  -W CUT_WINDOW_SIZE, --cut_window_size CUT_WINDOW_SIZE
                        the window size option shared by cut_front, cut_tail or cut_sliding. Range: 1~1000, default: 4
  -M CUT_MEAN_QUALITY, --cut_mean_quality CUT_MEAN_QUALITY
                        the mean quality requirement option shared by cut_front, cut_tail or cut_sliding. Range: 1~36 default: 20
  --cut_front_window_size CUT_FRONT_WINDOW_SIZE
                        the window size option of cut_front
  --cut_front_mean_quality CUT_FRONT_MEAN_QUALITY
                        the mean quality requirement option for cut_front
  --cut_tail_window_size CUT_TAIL_WINDOW_SIZE
                        the window size option of cut_tail
  --cut_tail_mean_quality CUT_TAIL_MEAN_QUALITY
                        the mean quality requirement option for cut_tail
  --cut_right_window_size CUT_RIGHT_WINDOW_SIZE
                        the window size option of cut_right
  --cut_right_mean_quality CUT_RIGHT_MEAN_QUALITY
                        the mean quality requirement option for cut_right
  -Q, --disable_quality_filtering
                        quality filtering is enabled by default. If this option is specified, quality filtering is disabled
  -q QUALIFIED_QUALITY_PHRED, --qualified_quality_phred QUALIFIED_QUALITY_PHRED
                        the quality value that a base is qualified. Default 20 means phred quality >=Q20 is qualified
  -u UNQUALIFIED_PERCENT_LIMIT, --unqualified_percent_limit UNQUALIFIED_PERCENT_LIMIT
                        how many percents of bases are allowed to be unqualified (0~100). Default 40 means 40%
  -n N_BASE_LIMIT, --n_base_limit N_BASE_LIMIT
                        if one read's number of N base is >n_base_limit, then this read/pair is discarded. Default is 5
  -e AVERAGE_QUAL, --average_qual AVERAGE_QUAL
                        if one read's average quality score <avg_qual, then this read/pair is discarded. Default 0 means no requirement
  -L, --disable_length_filtering
                        length filtering is enabled by default. If this option is specified, length filtering is disabled
  -l LENGTH_REQUIRED, --length_required LENGTH_REQUIRED
                        reads shorter than length_required will be discarded, default is 30
  --length_limit LENGTH_LIMIT
                        reads longer than length_limit will be discarded, default 0 means no limitation
  -y, --low_complexity_filter
                        enable low complexity filter
  -Y COMPLEXITY_THRESHOLD, --complexity_threshold COMPLEXITY_THRESHOLD
                        the threshold for low complexity filter (0~100). Default is 30
  --filter_by_index1 FILTER_BY_INDEX1
                        specify a file contains a list of barcodes of index1 to be filtered out
  --filter_by_index2 FILTER_BY_INDEX2
                        specify a file contains a list of barcodes of index2 to be filtered out
  --filter_by_index_threshold FILTER_BY_INDEX_THRESHOLD
                        the allowed difference of index barcode for index filtering, default 0 means completely identical
  -C, --no_correction   disable base correction in overlapped regions (only for PE data)
  --overlap_len_require OVERLAP_LEN_REQUIRE
                        the minimum length to detect overlapped region of PE reads. 30 by default
  --overlap_diff_limit OVERLAP_DIFF_LIMIT
                        the maximum number of mismatched bases to detect overlapped region of PE reads. 5 by default
  --overlap_diff_percent_limit OVERLAP_DIFF_PERCENT_LIMIT
                        the maximum percentage of mismatched bases to detect overlapped region of PE reads. Default 20 means 20%
  -U, --umi             enable unique molecular identifier (UMI) preprocessing
  --umi_loc UMI_LOC     specify the location of UMI (index1/index2/read1/read2/per_index/per_read)
  --umi_len UMI_LEN     if the UMI is in read1/read2, its length should be provided
  --umi_prefix UMI_PREFIX
                        prefix for UMI
  --umi_skip UMI_SKIP   if the UMI is in read1/read2, seq2type can skip several bases following UMI, default is 0
```

## To do list

TBD