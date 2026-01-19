# SmarTyper

## Description

**SmarTyper** is a novel, smart, multifunctional platform for genetic variation identification from target sequencing data.

## Key features of SmarTyper

* **Multifunctional**: conducts genotyping for microsatellite/SSR and SNPs, as well as microhaplotype and micropeptype identification.

* **Smart**: supports smart genotyping powered by AI.

* **Interative**: supports both auto and manual-genotyping with interactive plotting.

* **Ultra-fast**: ~ 1 second/sample using single thread.

* **Extremely low memory cost**: negligible ~ 0.1 MB RAM.

* **All-in-one**: SmarTyper directly takes raw target sequencing reads as input and output genotype table without any intermediate file writing and loading, making I/O very efficient.

* **Reads-to-report files**: it generates genotype table, a htlm report containging figures and tables for genotype, sex identification, SNPs.

## Getting started
### Step 1. Pre-installations
SmarTyper  is written in Python/Cython, C/C++11 and can be installed on Linux or Mac OS X (with Xcode and Xcode Command Line Tools installed).
We have tested SmarTyper on Ubuntu (Ubuntu 22.04.3 LTS)

#### Install system dependencies:
```bash
sudo apt install python3 python3-pip python3-venv python3-full
sudo apt install cython3
sudo apt install python3-tk
sudo apt-get install mafft
```

### Step 2. Clone and set up SmarTyper

```bash
git clone https://github.com/rocpengliu/SmarTyper.git
cd SmarTyper

pip3 install setuptools Cython
pip3 install customtkinter biopython pillow matplotlib typing dill logomaker seaborn joblib scikit-learn
pip3 install --break-system-packages setuptools Cython
pip3 install --break-system-packages customtkinter biopython pillow matplotlib typing dill logomaker seaborn joblib scikit-learn
```

### Step 3. Compile the C++ extension

```bash
python3 setup.py clean --all && python3 setup.py build_ext --inplace
```

### Step 4. Launch SmarTyper

```bash
python3 smartyper.py
```

## To do list

```

```