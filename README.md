# SmarTyper

## Description 

**SmarTyper** is a novel, multifunctional, ultra-fast, all-in-one and reads-to-report platform smart genetic variations(microsatellites, SNP, microhaplotype) identification from target sequencing.

## Key features of Seq2Type

* **Multifunctional**: SmarTyper can conduct genotyping for both microsatellite/SSR and SNPs from both target sequencing.


* **Ultra-fast**: ~ 1 second/sample using single thread.

* **Extremely low memory cost**: negligible ~ 0.1 MB RAM.

* **All-in-one**: SmarTyper directly takes raw target sequencing reads as input and output genotype table without any intermediate file writing and loading, making I/O very efficient.

* **Reads-to-report files**: it generates genotype table, a htlm report containging figures and tables for genotype, sex identification, SNPs.

* **Easy to use**: requires minimal programing skills.


## Getting started
### Step 1. Pre-install the software
SmarTyper  is written in Python/Cython, C/C++11 and can be installed on Linux or Mac OS X (with Xcode and Xcode Command Line Tools installed). 
We have tested SmarTyper on Ubuntu (16.04 LTS and above) 

```
sudo apt install python3 python3-pip
sudo apt install cython3
sudo apt install python3-tk
pip3 install customtkinter
pip install biopython
pip install pillow
pip install matplotlib
pip install typing
```

### Step 2. Install smartyper 

```
git clone https://github.com/rocpengliu/SmarTyper.git
cd SmarTyper
python setup.py clean --all && python setup.py build_ext --inplace #compile seq2type
python smartyper
```
