# distutils: language = c++
# cython: linetrace=True
# cython: binding=True

from libc.stdlib cimport malloc, free
from libc.string cimport strcpy
from cpython.pycapsule cimport PyCapsule_Import

# Include necessary header files
cdef extern from "src/seqtyper.h":
    void c_run_seqtyper(int argc, char* argv[]) nogil
    const char* c_get_captured_cout() nogil
    void c_free_captured_cout(const char* str) nogil

def run_seqtyper_wrapper(list args):
    cdef int argc = len(args)
    cdef char** argv = <char**>malloc(argc * sizeof(char*))
    try:
        for i in range(argc):
            argv[i] = <char*>malloc((len(args[i]) + 1) * sizeof(char))
            if argv[i] == NULL:
                raise MemoryError("Unable to allocate memory for argument")
            strcpy(argv[i], args[i].encode('utf-8'))
        with nogil:
            c_run_seqtyper(argc, argv)
    finally:
        for i in range(argc):
            if argv[i] != NULL:
                free(argv[i])
        free(argv)

def get_seqtyper_output():
    cdef const char* output = c_get_captured_cout()
    if output:
        try:
            return output.decode('utf-8', errors='replace')
        finally:
            c_free_captured_cout(output)
    return ""