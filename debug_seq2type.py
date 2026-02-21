#!/usr/bin/env python3
import faulthandler
import sys
import traceback

# Enable faulthandler to catch segfaults
faulthandler.enable()

# Add debug output
print("[DEBUG] Starting seq2type with faulthandler enabled", file=sys.stderr)
sys.stderr.flush()

try:
    from seqtyper_core import run_seqtyper_wrapper
    
    args = [
        'seqtyper',
        '-i', '/home/liup/project/data/grape/mn_bc/raw/SRR10717716_1.fastq.gz',
        '-I', '/home/liup/project/data/grape/mn_bc/raw/SRR10717716_2.fastq.gz',
        '--var', 'snp',
        '--loc', '/home/liup/project/data/grape/bc/bc_loci.txt',
        '--prefix', 'aa'
    ]
    
    print(f"[DEBUG] Arguments: {args}", file=sys.stderr)
    sys.stderr.flush()
    
    print("[DEBUG] About to call run_seqtyper_wrapper", file=sys.stderr)
    sys.stderr.flush()
    
    run_seqtyper_wrapper(args)
    
    print("[DEBUG] Completed successfully", file=sys.stderr)
    sys.stderr.flush()

except Exception as e:
    print(f"[ERROR] Exception caught: {e}", file=sys.stderr)
    traceback.print_exc()
    sys.exit(1)
except SystemExit as e:
    print(f"[DEBUG] SystemExit: {e}", file=sys.stderr)
    sys.exit(0)
