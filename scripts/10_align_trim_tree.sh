#!/usr/bin/env bash
set -euo pipefail
[[ $# -eq 1 ]] || { echo "Usage: $0 PHYLOGENY_DIRECTORY" >&2; exit 1; }
PHYLO=$(realpath "$1"); THREADS=${THREADS:-24}
mafft --auto --thread "$THREADS" "$PHYLO/mcrA_phylogeny_input.fasta" > "$PHYLO/mcrA_phylogeny.aln.fasta"
python - "$PHYLO/mcrA_phylogeny.aln.fasta" "$PHYLO/mcrA_phylogeny.core.aln.fasta" <<'PY'
import sys
inp,out=sys.argv[1:]; seqs={}; name=None; buf=[]
for line in open(inp):
    line=line.strip()
    if line.startswith('>'):
        if name is not None: seqs[name]=''.join(buf)
        name=line[1:]; buf=[]
    else: buf.append(line)
if name is not None: seqs[name]=''.join(buf)
names=list(seqs); L=len(seqs[names[0]]); N=len(names); occ=[sum(seqs[x][i] not in '-.' for x in names)/N for i in range(L)]
left=next(i for i,x in enumerate(occ) if x>=0.80); right=max(i for i,x in enumerate(occ) if x>=0.80)+1
with open(out,'w') as fh:
    for name in names: fh.write(f'>{name}\n{seqs[name][left:right]}\n')
print('sequences',N,'original columns',L,'left removed',left,'right removed',L-right,'core columns',right-left)
PY
iqtree2 -s "$PHYLO/mcrA_phylogeny.core.aln.fasta" -m GTR+F+G4 -B 1000 --alrt 1000 -T AUTO --prefix "$PHYLO/mcrA_GTR"
