# Controls and the master ASV annotation table

## Controls are retained until after DADA2

The dataset contained 10 blank/NTC libraries. They were carried through primer trimming, denoising, merging, and taxonomy.

Observed control signal:

```text
10 controls
685 total control reads
5 controls with zero reads
15 ASVs detected in any control
5 ASVs control-exclusive
482 reads in those 5 control-exclusive ASVs
```

This is extremely low contamination relative to approximately 15.84 million biological reads.

## Important rule: do not delete every ASV detected in a blank

One ASV occurred with only 32 reads in a blank but 234,861 reads across 129 biological samples. Removing that feature because it appeared in one blank would delete a clearly genuine biological lineage.

Interpretation: low-level carryover or index leakage can introduce tiny numbers of genuine high-abundance sequences into controls.

Final control policy:

1. remove control samples from ecological analyses;
2. remove the five control-exclusive ASVs;
3. retain biological ASVs that merely have a few reads in controls;
4. remove biological libraries with <1,000 reads from ecology.

## Master annotation table

`scripts/07_build_master_annotation.py` produces one row per ASV with:

```text
ASV
biological read abundance
control read abundance
biological prevalence
control prevalence
GTDB consensus taxonomy
GTDB best hit and identity
environmental-database consensus taxonomy
environmental best hit and identity
identity category
phylogeny priority
```

## Phylogeny triage used in the completed analysis

ASVs with GTDB identity below 90% were prioritized according to biological abundance:

```text
HIGH:    >=10,000 biological reads
MEDIUM:  >=1,000 and <10,000 biological reads
LOW:     <1,000 biological reads
```

Result:

```text
HIGH:    46 ASVs; 1,317,895 reads
MEDIUM: 241 ASVs;   724,121 reads
LOW:   3900 ASVs;   268,113 reads
```

The HIGH + MEDIUM set (287 ASVs) was small enough for targeted phylogenetic refinement while representing about 2.04 million reads.
