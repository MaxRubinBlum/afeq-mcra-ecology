# Environment setup

## QIIME 2

The completed run used QIIME 2 amplicon 2026.1:

```bash
conda activate qiime2-amplicon-2026.1
qiime info
```

Save `qiime info` output with every important run.

The workflow requires at least:

```text
q2-cutadapt
q2-dada2
q2-feature-table
q2-feature-classifier
q2-metadata
```

## External programs

Check availability:

```bash
cutadapt --version
mafft --version
which iqtree2
```

The original phylogeny run used IQ-TREE 2.0.6. A newer IQ-TREE 2 is preferable for future reruns, but the documented tree was successfully produced with the older installation.

## Python

Core processing scripts intentionally use Python's standard library where possible so they can run inside the QIIME environment without installing Biopython.

For ecological analysis, a separate environment with pandas/openpyxl is convenient:

```bash
conda create -n mcra-ecology python=3.12 pandas openpyxl scipy matplotlib biopython
conda activate mcra-ecology
```

Add other statistical packages only when the analysis requires them.

## Configuration

Copy:

```bash
cp config/config.example.sh config/config.sh
```

Edit paths in `config/config.sh`, then:

```bash
source config/config.sh
```

Do not commit your local `config/config.sh` if it contains private paths.
