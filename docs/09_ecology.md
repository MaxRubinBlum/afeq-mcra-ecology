# From ASVs to ecological analysis

## Do not analyse raw GTDB genus labels directly

Before ecological analysis, propagate the phylogenetic refinements into an ecology label column. Keep the original GTDB and environmental annotations as separate columns so nothing is lost.

Recommended columns:

```text
ASV
final_ecology_label
label_source
label_confidence
GTDB_taxonomy
GTDB_best_identity
environmental_taxonomy
environmental_best_identity
phylogenetic_assignment
```

## Suggested methane-cycling labels

Examples:

```text
Methanosarcina
Methanoregula
Methanobacterium_D
Methanobacterium_B
UBA9949
Methanotrichaceae-related
ANME-2d / Methanoperedenaceae-related
ANME-3 / Methanovorans-related
ANME-2a-related / Methanocomedens
Unresolved environmental mcrA lineage
Other mcrA
```

Do not force every rare ASV to genus level.

## Sample filtering before ecology

Recommended project-specific rules:

```text
remove controls
remove control-exclusive ASVs
remove biological libraries with <1,000 reads
```

This leaves 145 biological mcrA libraries in the current analysis.

## Relative abundance

For descriptive composition plots:

```text
relative abundance = lineage reads / total retained reads in that sample
```

Always retain the raw counts separately for methods that require counts.

## Initial ecological patterns observed

Current exploratory results indicate strong spatial structure:

- EA2 is consistently enriched in `Methanoregula`.
- EA3 is strongly `Methanosarcina` dominated.
- EA1 contains the strongest recurrent ANME-2d signal among the EA sites.
- At EA1, ANME-2d forms narrow depth horizons rather than a monotonic increase with depth.
- P1 in April also contains a strong ANME-2d signal.

These patterns should be treated as current descriptive results, not final inferential statistics.

## Recommended next statistical workflow

1. Build sample × lineage and sample × ASV count matrices.
2. Join only metadata fields with validated sample IDs.
3. Inspect sequencing depth and zero inflation.
4. Visualize composition by site × season × depth.
5. Calculate Bray-Curtis dissimilarity after a justified transformation/normalization.
6. Test site, season, depth, and their interactions with a design that respects repeated spatial profiles.
7. Analyse geochemistry with site-stratified models rather than only pooled correlations.
8. Treat mcrA as a relative/compositional marker unless absolute gene copy measurements are available.

## Interpretation caution

Amplicon relative abundance does not equal metabolic rate. A lineage can be abundant without being active, and primer biases/gene-copy differences can influence relative abundance. Phrase conclusions as community composition unless independent activity measurements support stronger claims.
