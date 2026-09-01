# Targeted phylogenetic refinement

## Why a tree was needed

A nearest genome hit at 82–88% identity can indicate broad relatedness without justifying a genus-level name. This problem was particularly important for the abundant GTDB `Methanoperedens`-like ASVs.

Rather than putting all 14,260 ASVs into a large tree, the analysis selected the 287 HIGH/MEDIUM low-identity ASVs.

## Tree contents

The targeted nucleotide tree contained:

```text
287 candidate ASVs
1021 GTDB MLf/MLr references
383 selected environmental references
1691 total sequences
```

For each candidate ASV, up to three close environmental reference hits were included. Duplicate environmental references across candidates were included only once.

## Alignment

MAFFT was used for alignment.

The initial alignment was 526 columns because some environmental references extended beyond the common amplicon boundaries. A trimmed alignment of 417 columns was used for the final tree.

## Tree inference

The original ModelFinder run was very slow, so the final tree used a fixed nucleotide model:

```text
GTR+F+G4
```

with:

```text
1000 ultrafast bootstrap replicates
1000 SH-aLRT replicates
```

Command:

```bash
iqtree2 \
  -s mcrA_phylogeny.trimmed.aln.fasta \
  -m GTR+F+G4 \
  -B 1000 \
  --alrt 1000 \
  -T AUTO \
  --prefix mcrA_GTR
```

The run analysed 1,691 sequences and a 417-bp alignment. IQ-TREE temporarily collapsed identical sequences during some calculations; this did not mean they were removed from the final tree.

## Limitation

The amplicon is short and many sequences show compositional heterogeneity. Therefore this tree is used for **local placement relative to known references**, not for strong claims about deep archaeal evolutionary relationships.

## Key phylogenetic outcome

The tree confirmed a coherent ANME-2d / Methanoperedenaceae-related lineage among the abundant low-identity ASVs. In the 287-ASV candidate set:

```text
ANME-2d / Methanoperedenaceae-related: 107 ASVs; 613,317 reads
ANME-3 / Methanovorans-related:           3 ASVs;  11,083 reads
ANME-2a-related / Methanocomedens:        1 ASV;    4,763 reads
other/unresolved:                        176 ASVs; 1,412,853 reads
```

The ANME-2d clade had strong local support (SH-aLRT 99.8 / UFBoot 97).

## Examples illustrating why the tree matters

An abundant ASV assigned to `Methanoperedens` had only ~83% identity to the nearest GTDB genome but was identical over the amplicon to an environmental reference and placed within the supported ANME-2d clade.

Conversely, two very abundant ASVs with no stable GTDB classification had ~98.6–98.8% environmental matches. These were retained as unresolved environmental mcrA lineages rather than forced into an incorrect genome genus.
