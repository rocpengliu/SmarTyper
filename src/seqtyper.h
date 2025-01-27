#ifndef SEQTYPER_H
#define SEQTYPER_H

#include <string>

void run_seqtyper(int argc, char* argv[]);

void setup_cout_capture();
void release_cout_capture();
const char* get_captured_cout();
void free_captured_cout(const char* str);

extern "C" {
    void c_run_seqtyper(int argc, char* argv[]);
    const char* c_get_captured_cout();
    void c_free_captured_cout(const char *str);
}

#endif