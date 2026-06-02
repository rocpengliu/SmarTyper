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
SmarTyper is written in Python/Cython and C/C++11, and can be installed on Linux.
We tested SmarTyper on Ubuntu 24.04.4 LTS.
If you use Windows, installing and running SmarTyper through Windows Subsystem for Linux 2 (WSL2) is recommended.

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

## Seq2Type as a standalone software tool


## To do list

TBD