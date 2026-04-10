import argparse
import threading
import time
from seqtyper_core import run_seqtyper_wrapper, get_seqtyper_output

def main():
    print(f"seq2type python version")
    # disable_help=True because -h is used for --html in seqtyper, not help
    parser = argparse.ArgumentParser(description='seq2type for genotyping', add_help=False)

    # Basic I/O
    parser.add_argument('--var', type=str, default='', help='genetic variance, must be either microsatellite/ssr or snp')
    parser.add_argument('-i', '--in1', type=str, default='', help='read1 input file name')
    parser.add_argument('-I', '--in2', type=str, default='', help='read2 input file name')
    parser.add_argument('-X', '--prefix', type=str, default='', help='prefix name for output files, eg: sample01')
    parser.add_argument('--outFReads', action='store_true', help='If specified, off-target reads will be outputed in a file')
    parser.add_argument('-o', '--out1', type=str, default='', help='file name to store read1 with on-target sequences')
    parser.add_argument('-O', '--out2', type=str, default='', help='file name to store read2 with on-target sequences')
    parser.add_argument('--nanopore_default', action='store_true', help='If specified, use the default settings (mainly about Q score) of nanopore sequencing')

    # Loci file
    parser.add_argument('--loc', type=str, default='', help='loci file containing loci names, primers, flanking regions, etc.')
    parser.add_argument('--revCom', action='store_true', help='if your reverse primer sequence in the loc file is not reverse complentary, please specify it')
    parser.add_argument('--minReads4Locus', type=int, default=30, help='minimum number of reads for a locus, default: 30')
    parser.add_argument('--maxMismatchesPSeq', type=int, default=2, help='maximum mismatches for primer sequences 2, default: 2')
    parser.add_argument('--noPlot', action='store_true', help='If specified, do not plot')
    
    # Sequence alignment
    parser.add_argument('--mode', type=str, default='NW', help='specify the sequence alignment mode: NW (default) | HW | SHW')
    parser.add_argument('--maxScore', type=int, default=-1, help='maximum score of sequence alignment, sequences with score > maxScore will be discarded')
    parser.add_argument('--numBestSeqs', type=int, default=0, help='Score will be calculated only for N best sequences')
    parser.add_argument('--notFindAlignment', action='store_true', help='If specified, alignment path will be not found and printed')
    parser.add_argument('--findStartLocation', action='store_true', help='If specified, start locations will be found and printed')
    parser.add_argument('--format', type=str, default='NICE', help='Format for alignment path: NICE|CIG_STD|CIG_EXT')
    parser.add_argument('--core', type=int, default=1, help='Core part of calculation will be repeated N times')
    parser.add_argument('--silentAlignment', action='store_true', help='If specified, there will be no score or alignment output')
    parser.add_argument('--printResults', action='store_true', help='If specified, alignment results will be printed but with only 1 thread')
    
    # SSR parameters
    parser.add_argument('--maxMismatchesPer4FR', type=float, default=0.3, help='maximum percentage mismatches for flanking regions, default 0.3 (30%%)')
    parser.add_argument('--minSeqsPercentage', type=int, default=5, help='minimum percentage reads against largest peak for a genotype, default: 5 (5%%)')
    parser.add_argument('--minWarningSeqs', type=int, default=50, help='minimum number of reads for warning a genotype, default: 50')
    parser.add_argument('--hlRatio1', type=float, default=0.4, help='ratio of loci sizes when length difference = 1 ssr unit, default: 0.4')
    parser.add_argument('--hlRatio2', type=float, default=0.2, help='ratio of loci sizes when length difference = 2 ssr unit, default: 0.2')
    parser.add_argument('--maxVarRatio', type=float, default=1.5, help='ratio of two heter alleles, default: 1.5')
    
    # SNP parameters
    parser.add_argument('--smProp1H', type=float, default=0.84, help='homo threshold when one true SNP, default: 0.84')
    parser.add_argument('--smProp1L', type=float, default=0.78, help='heter threshold when one true SNP, default: 0.78')
    parser.add_argument('--mmProp1H', type=float, default=0.83, help='homo threshold when >= two true SNPs, default: 0.83')
    parser.add_argument('--mmProp1L', type=float, default=0.79, help='heter threshold when >= two true SNPs, default: 0.79')
    parser.add_argument('--mProp2', type=float, default=0.50, help='heter threshold for read2/read3 proportion, default: 0.50')
    #parser.add_argument('--sProp3', type=float, default=0.8, help='heter threshold for read2/read3 proportion, default: 0.8')
    #parser.add_argument('--minSeqsProSnp', type=float, default=0.10, help='minimum proportion reads against largest peak for SNP genotype, default: 0.1 (10%%)')
    parser.add_argument('--minReads4Allele', type=int, default=10, help='minimum reads for filtering an allele, read1 for homo and read2 for heter, default: 10')
    parser.add_argument('--maxRVs4Align', type=int, default=6, help='maximum number of read variants for alignment table, must be > 2 rows. default: 6')
    parser.add_argument('--noSnpPlot', action='store_true', help='If specified, do not plot SNPs')
    parser.add_argument('--noErrorPlot', action='store_true', help='If specified, do not plot error rate')
    
    # Sex parameters
    parser.add_argument('--sex', type=str, default='', help='sex loci file containing sex locus names, primers, reference sequences')
    parser.add_argument('--maxMismatchesSexPSeq', type=int, default=2, help='maximum number of mismatches for sex primers, default: 2')
    parser.add_argument('--maxMismatchesSexRefSeq', type=int, default=2, help='maximum number of mismatches for sex reference sequences, default: 2')
    parser.add_argument('--yxRatio', type=float, default=0.001, help='minimum ratio of numbers of reads Y/X to W/Z, default: 0.001')
    parser.add_argument('--minReadsSexAllele', type=int, default=10, help='minimum number of reads assigned to each sex allele of X or Y; default: 10')
    parser.add_argument('--minReadsSexVariant', type=int, default=5, help='minimum number of reads assigned to each sex variant of X or Y; default: 5')
    
    parser.add_argument('--debug', action='store_true', help='If specified, print debug')
    
    # Reporting
    parser.add_argument('-j', '--json', type=str, default='seq2sat.json', help='the json format report file name')
    parser.add_argument('--html', type=str, default='seq2sat.html', help='the html format report file name')
    parser.add_argument('-R', '--report_title', type=str, default='seq2type report', help='report title')
    parser.add_argument('--help', action='store_true', help='show this help message and exit')

    # Threading
    parser.add_argument('-w', '--thread', type=int, default=4, help='worker thread number, default is 4')

    # Other I/O
    parser.add_argument('-6', '--phred64', action='store_true', help='indicate the input is using phred64 scoring')
    parser.add_argument('-z', '--compression', type=int, default=4, help='compression level for gzip output (1 ~ 9)')
    parser.add_argument('--stdin', action='store_true', help='input from STDIN')
    parser.add_argument('--stdout', action='store_true', help='stream passing-filters reads to STDOUT')
    parser.add_argument('--interleaved_in', action='store_true', help='indicate that <in1> is an interleaved FASTQ')
    parser.add_argument('--reads_to_process', type=int, default=0, help='specify how many reads/pairs to be processed. Default 0 means process all reads')
    parser.add_argument('--dont_overwrite', action='store_true', help="don't overwrite existing files")
    parser.add_argument('-V', '--verbose', action='store_true', help='output verbose log information')

    # Adapter trimming
    parser.add_argument('-A', '--disable_adapter_trimming', action='store_true', help='adapter trimming is enabled by default. If this option is specified, adapter trimming is disabled')
    parser.add_argument('-a', '--adapter_sequence', type=str, default='auto', help='the adapter for read1')
    parser.add_argument('--adapter_sequence_r2', type=str, default='auto', help='the adapter for read2')
    parser.add_argument('--adapter_fasta', type=str, default='', help='specify a FASTA file to trim both read1 and read2')
    parser.add_argument('--detect_adapter_for_pe', action='store_true', help='enable auto-detection for adapter for PE data')

    # Trimming
    parser.add_argument('-f', '--trim_front1', type=int, default=0, help='trimming how many bases in front for read1, default is 0')
    parser.add_argument('-t', '--trim_tail1', type=int, default=0, help='trimming how many bases in tail for read1, default is 0')
    parser.add_argument('-b', '--max_len1', type=int, default=0, help='if read1 is longer than max_len1, then trim read1 at its tail')
    parser.add_argument('-F', '--trim_front2', type=int, default=0, help='trimming how many bases in front for read2')
    parser.add_argument('-T', '--trim_tail2', type=int, default=0, help='trimming how many bases in tail for read2')
    parser.add_argument('-B', '--max_len2', type=int, default=0, help='if read2 is longer than max_len2, then trim read2 at its tail')

    # PolyG tail trimming
    parser.add_argument('--poly_g_min_len', type=int, default=10, help='the minimum length to detect polyG in the read tail. 10 by default')
    parser.add_argument('-G', '--disable_trim_poly_g', action='store_true', help='disable polyG tail trimming')
    
    # PolyX tail trimming
    parser.add_argument('-x', '--trim_poly_x', action='store_true', help='enable polyX trimming in 3\' ends')
    parser.add_argument('--poly_x_min_len', type=int, default=10, help='the minimum length to detect polyX in the read tail. 10 by default')

    # Cutting by quality
    parser.add_argument('-5', '--cut_front', action='store_true', help='move a sliding window from front (5\') to tail, drop the bases in the window if its mean quality < threshold')
    parser.add_argument('-3', '--cut_tail', action='store_true', help='move a sliding window from tail (3\') to front, drop the bases in the window if its mean quality < threshold')
    parser.add_argument('-r', '--cut_right', action='store_true', help='move a sliding window from front to tail, if meet one window with mean quality < threshold, drop the bases')
    parser.add_argument('-W', '--cut_window_size', type=int, default=4, help='the window size option shared by cut_front, cut_tail or cut_sliding. Range: 1~1000, default: 4')
    parser.add_argument('-M', '--cut_mean_quality', type=int, default=20, help='the mean quality requirement option shared by cut_front, cut_tail or cut_sliding. Range: 1~36 default: 20')
    parser.add_argument('--cut_front_window_size', type=int, default=4, help='the window size option of cut_front')
    parser.add_argument('--cut_front_mean_quality', type=int, default=20, help='the mean quality requirement option for cut_front')
    parser.add_argument('--cut_tail_window_size', type=int, default=4, help='the window size option of cut_tail')
    parser.add_argument('--cut_tail_mean_quality', type=int, default=20, help='the mean quality requirement option for cut_tail')
    parser.add_argument('--cut_right_window_size', type=int, default=4, help='the window size option of cut_right')
    parser.add_argument('--cut_right_mean_quality', type=int, default=20, help='the mean quality requirement option for cut_right')

    # Quality filtering
    parser.add_argument('-Q', '--disable_quality_filtering', action='store_true', help='quality filtering is enabled by default. If this option is specified, quality filtering is disabled')
    parser.add_argument('-q', '--qualified_quality_phred', type=int, default=20, help='the quality value that a base is qualified. Default 20 means phred quality >=Q20 is qualified')
    parser.add_argument('-u', '--unqualified_percent_limit', type=int, default=40, help='how many percents of bases are allowed to be unqualified (0~100). Default 40 means 40%%')
    parser.add_argument('-n', '--n_base_limit', type=int, default=5, help='if one read\'s number of N base is >n_base_limit, then this read/pair is discarded. Default is 5')
    parser.add_argument('-e', '--average_qual', type=int, default=0, help='if one read\'s average quality score <avg_qual, then this read/pair is discarded. Default 0 means no requirement')

    # Length filtering
    parser.add_argument('-L', '--disable_length_filtering', action='store_true', help='length filtering is enabled by default. If this option is specified, length filtering is disabled')
    parser.add_argument('-l', '--length_required', type=int, default=30, help='reads shorter than length_required will be discarded, default is 30')
    parser.add_argument('--length_limit', type=int, default=0, help='reads longer than length_limit will be discarded, default 0 means no limitation')

    # Low complexity filtering
    parser.add_argument('-y', '--low_complexity_filter', action='store_true', help='enable low complexity filter')
    parser.add_argument('-Y', '--complexity_threshold', type=int, default=30, help='the threshold for low complexity filter (0~100). Default is 30')

    # Filter by indexes
    parser.add_argument('--filter_by_index1', type=str, default='', help='specify a file contains a list of barcodes of index1 to be filtered out')
    parser.add_argument('--filter_by_index2', type=str, default='', help='specify a file contains a list of barcodes of index2 to be filtered out')
    parser.add_argument('--filter_by_index_threshold', type=int, default=0, help='the allowed difference of index barcode for index filtering, default 0 means completely identical')
    
    # Base correction
    parser.add_argument('-C', '--no_correction', action='store_true', help='disable base correction in overlapped regions (only for PE data)')
    parser.add_argument('--overlap_len_require', type=int, default=30, help='the minimum length to detect overlapped region of PE reads. 30 by default')
    parser.add_argument('--overlap_diff_limit', type=int, default=5, help='the maximum number of mismatched bases to detect overlapped region of PE reads. 5 by default')
    parser.add_argument('--overlap_diff_percent_limit', type=int, default=20, help='the maximum percentage of mismatched bases to detect overlapped region of PE reads. Default 20 means 20%%')

    # UMI
    parser.add_argument('-U', '--umi', action='store_true', help='enable unique molecular identifier (UMI) preprocessing')
    parser.add_argument('--umi_loc', type=str, default='', help='specify the location of UMI (index1/index2/read1/read2/per_index/per_read)')
    parser.add_argument('--umi_len', type=int, default=0, help='if the UMI is in read1/read2, its length should be provided')
    parser.add_argument('--umi_prefix', type=str, default='', help='prefix for UMI')
    parser.add_argument('--umi_skip', type=int, default=0, help='if the UMI is in read1/read2, seq2sat can skip several bases following UMI, default is 0')

    args = parser.parse_args()

    # Show help if requested
    if args.help:
        parser.print_help()
        return

    # Convert argparse.Namespace to a list of arguments
    # Map between attribute names and their command-line flags
    arg_map = {
        'var': '--var',
        'in1': '-i',
        'in2': '-I',
        'prefix': '-X',
        'outFReads': '--outFReads',
        'out1': '-o',
        'out2': '-O',
        'nanopore_default': '--nanopore_default',
        'loc': '--loc',
        'revCom': '--revCom',
        'minReads4Locus': '--minReads4Locus',
        'maxMismatchesPSeq': '--maxMismatchesPSeq',
        'noPlot': '--noPlot',
        'mode': '--mode',
        'maxScore': '--maxScore',
        'numBestSeqs': '--numBestSeqs',
        'notFindAlignment': '--notFindAlignment',
        'findStartLocation': '--findStartLocation',
        'format': '--format',
        'core': '--core',
        'silentAlignment': '--silentAlignment',
        'printResults': '--printResults',
        'maxMismatchesPer4FR': '--maxMismatchesPer4FR',
        'minSeqsPercentage': '--minSeqsPercentage',
        'minWarningSeqs': '--minWarningSeqs',
        'hlRatio1': '--hlRatio1',
        'hlRatio2': '--hlRatio2',
        'maxVarRatio': '--maxVarRatio',
        'smProp1H': '--smProp1H',
        'smProp1L': '--smProp1L',
        'mmProp1H': '--mmProp1H',
        'mmProp1L': '--mmProp1L',
        'mProp2': '--mProp2',
        #'sProp3': '--sProp3',
        #'minSeqsProSnp': '--minSeqsProSnp',
        'minReads4Allele': '--minReads4Allele',
        'maxRVs4Align': '--maxRVs4Align',
        'noSnpPlot': '--noSnpPlot',
        'noErrorPlot': '--noErrorPlot',
        'sex': '--sex',
        'maxMismatchesSexPSeq': '--maxMismatchesSexPSeq',
        'maxMismatchesSexRefSeq': '--maxMismatchesSexRefSeq',
        'yxRatio': '--yxRatio',
        'minReadsSexAllele': '--minReadsSexAllele',
        'minReadsSexVariant': '--minReadsSexVariant',
        'debug': '--debug',
        'json': '-j',
        'html': '--html',
        'report_title': '-R',
        'thread': '-w',
        'phred64': '-6',
        'compression': '-z',
        'stdin': '--stdin',
        'stdout': '--stdout',
        'interleaved_in': '--interleaved_in',
        'reads_to_process': '--reads_to_process',
        'dont_overwrite': '--dont_overwrite',
        'verbose': '-V',
        'disable_adapter_trimming': '-A',
        'adapter_sequence': '-a',
        'adapter_sequence_r2': '--adapter_sequence_r2',
        'adapter_fasta': '--adapter_fasta',
        'detect_adapter_for_pe': '--detect_adapter_for_pe',
        'trim_front1': '-f',
        'trim_tail1': '-t',
        'max_len1': '-b',
        'trim_front2': '-F',
        'trim_tail2': '-T',
        'max_len2': '-B',
        'poly_g_min_len': '--poly_g_min_len',
        'disable_trim_poly_g': '-G',
        'trim_poly_x': '-x',
        'poly_x_min_len': '--poly_x_min_len',
        'cut_front': '-5',
        'cut_tail': '-3',
        'cut_right': '-r',
        'cut_window_size': '-W',
        'cut_mean_quality': '-M',
        'cut_front_window_size': '--cut_front_window_size',
        'cut_front_mean_quality': '--cut_front_mean_quality',
        'cut_tail_window_size': '--cut_tail_window_size',
        'cut_tail_mean_quality': '--cut_tail_mean_quality',
        'cut_right_window_size': '--cut_right_window_size',
        'cut_right_mean_quality': '--cut_right_mean_quality',
        'disable_quality_filtering': '-Q',
        'qualified_quality_phred': '-q',
        'unqualified_percent_limit': '-u',
        'n_base_limit': '-n',
        'average_qual': '-e',
        'disable_length_filtering': '-L',
        'length_required': '-l',
        'length_limit': '--length_limit',
        'low_complexity_filter': '-y',
        'complexity_threshold': '-Y',
        'filter_by_index1': '--filter_by_index1',
        'filter_by_index2': '--filter_by_index2',
        'filter_by_index_threshold': '--filter_by_index_threshold',
        'no_correction': '-C',
        'overlap_len_require': '--overlap_len_require',
        'overlap_diff_limit': '--overlap_diff_limit',
        'overlap_diff_percent_limit': '--overlap_diff_percent_limit',
        'umi': '-U',
        'umi_loc': '--umi_loc',
        'umi_len': '--umi_len',
        'umi_prefix': '--umi_prefix',
        'umi_skip': '--umi_skip',
    }

    args_list = []
    for key, value in vars(args).items():
        if key == 'help':
            continue  # Skip help flag
        
        flag = arg_map.get(key)
        if flag is None:
            continue  # Skip unmapped arguments
        
        if isinstance(value, bool):
            # For boolean flags, only add the flag if True
            if value:
                args_list.append(flag)
        elif value is not None and value != '':
            # For non-boolean arguments, add flag and value
            # Skip default empty strings and None values to avoid cluttering command line
            if isinstance(value, (int, float)):
                # Always include numeric values even if they're defaults
                # Check if they differ from defaults to avoid redundancy
                args_list.append(flag)
                args_list.append(str(value))
            elif value:  # Non-empty string
                args_list.append(flag)
                args_list.append(str(value))

    # Prepend the script name to match the C++ command-line interface
    args_list.insert(0, 'seqtyper')

    # Print the argument list for debugging
    print(f"Arguments passed to C++ function: {args_list}\n")

    try:
        # Event to signal when execution is complete
        execution_complete = threading.Event()
        
        # Thread to run the C++ function
        def run_cpp():
            run_seqtyper_wrapper(args_list)
            execution_complete.set()
        
        # Start the C++ execution in a separate thread
        cpp_thread = threading.Thread(target=run_cpp, daemon=False)
        cpp_thread.start()
        
        # Thread to capture and display output
        def capture_output_thread():
            while not execution_complete.is_set():
                output = get_seqtyper_output()
                if output:
                    print(output, end='', flush=True)
                else:
                    time.sleep(0.05)
        
        output_thread = threading.Thread(target=capture_output_thread, daemon=True)
        output_thread.start()
        
        # Wait for the C++ execution to complete
        cpp_thread.join()
        
        # Ensure all remaining output is captured and printed
        time.sleep(0.1)  # Brief delay to allow final output
        while True:
            output = get_seqtyper_output()
            if output:
                print(output, end='', flush=True)
            else:
                break
                
    except Exception as e:
        print(f"Error running seq2type: {e}")

if __name__ == '__main__':
    main()
