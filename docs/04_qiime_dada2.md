# QIIME 2 processing and DADA2

## Biological primers

```text
MLf: GGTGGTGTMGGATTCACACARTAYGCWACAGC
MLr: TTCATTGCRTAGTTWGGRTAGTT
```

Library tails used in the sequencing design included:

```text
sIDTP5: CTACACGACGCTCTTCCGATCT
sIDTP7: CAGACGTGTGCTCTTCCGATCT
```

We trim the **biological primers** rather than matching the complete tail+primer oligo. With cutadapt front matching, sequence upstream of the matched biological primer is removed as well.

## Why the two sequencing batches are denoised separately

DADA2 learns run-specific error rates. The September/January and April/July libraries came from separate sequencing batches, so they receive separate DADA2 error models.

Correct order:

```text
Sep/Jan raw -> trim -> DADA2 ----\
                                  -> merge ASV tables/sequences
Apr/Jul raw -> trim -> DADA2 ----/
```

Incorrect approach:

```text
merge raw reads from separate runs -> one DADA2 model
```

## Final DADA2 settings used

```text
trim-left-f       0
trim-left-r       0
trunc-len-f       0
trunc-len-r       0
max-ee-f          2
max-ee-r          2
min-overlap       12
pooling-method    pseudo
chimera-method    consensus
threads           24
```

No fixed 3' truncation was necessary.

QIIME 2 2026.1 also requires the DADA2 base transition output, hence:

```text
--o-base-transition-stats
```

## Observed run-level QC

Approximate final DADA2 retention:

```text
Sep-Jan: ~13.58 million input -> ~10.08 million non-chimeric (~74.2%)
Apr-Jul:  ~6.66 million input ->  ~5.76 million non-chimeric (~86.5%)
```

These values were judged acceptable and DADA2 was not rerun.

## Low-depth biological libraries

Five biological samples ended with fewer than 1,000 reads and were excluded from downstream ecology:

```text
Sep24-EA3-TD   12
Jul25-EA3-1    89
Jan25-EA3-3    208
Sep24-EA3-5    804
Jul25-EA4-6    859
```

Samples retained despite relatively low depth included:

```text
Apr25-EA4-2    1100
Apr25-EA2-10   1527
Jan25-EA1-7    4887
```

The 1,000-read threshold is a pragmatic ecology filter, not a statement that an ASV below 1,000 total reads is biologically invalid.

## QIIME 2 2026.1 syntax note

`feature-table summarize` uses:

```bash
--o-summary table.qzv
--o-feature-frequencies feature-frequencies.qza
--o-sample-frequencies sample-frequencies.qza
```

Do not use an older `--o-visualization` syntax for this command.
