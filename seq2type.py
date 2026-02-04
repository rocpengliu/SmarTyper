import argparse
from seqtyper_core import run_seqtyper_wrapper

def main():
    print(f"let's go")
    parser = argparse.ArgumentParser(description='seqtyper for genotyping')

    parser.add_argument('-f', '--prefix', required=True, help='output sample prefix')
    parser.add_argument('-i', '--in1', help='input file name for read1')
    parser.add_argument('-I', '--in2', help='input file name for read2')
    parser.add_argument('--loc', required=True, help='for loci file')
    parser.add_argument('--var', help='var must be ssr or snp')
    parser.add_argument('--thread', help='number thread')
    parser.add_argument('--debug', action='store_true', help='enable special feature, defaults to False')
    parser.add_argument('--verbose', action='store_true', help='enable special feature, defaults to False')

    args = parser.parse_args()

    # Convert argparse.Namespace to a list of arguments
    args_list = []
    for key, value in vars(args).items():
        if isinstance(value, bool):
            if value:
                args_list.append(f'--{key}')
        elif value is not None:
            args_list.append(f'--{key}' if len(key) > 1 else f'-{key[0]}')
            args_list.append(str(value))

    # Prepend the script name to match the C++ command-line interface
    args_list.insert(0, 'seqtyper')

    # Print the argument list for debugging
    print(f"Arguments passed to C++ function: {args_list}")

    try:
        # Call the Cython-wrapped function
        run_seqtyper_wrapper(args_list)
    except Exception as e:
        print(f"Error running seq2type: {e}")

if __name__ == '__main__':
    main()
