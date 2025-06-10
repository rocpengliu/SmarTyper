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

```
sudo apt install python3 python3-pip
sudo apt install cython3
sudo apt install python3-tk
pip3 install customtkinter
pip3 install biopython
pip3 install pillow
pip3 install matplotlib
pip3 install typing
pip3 install dill
```

### Step 2. Install smartyper

```
git clone https://github.com/rocpengliu/SmarTyper.git
cd SmarTyper
python setup.py clean --all && python setup.py build_ext --inplace #compile seq2type
```

### Step 3. Launch smartyper

```
python smartyper
```

## To do list

```
1. add microtype looking up table
```