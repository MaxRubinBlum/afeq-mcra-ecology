#!/usr/bin/env bash
set -euo pipefail
: "${GTDB_WORK:?source config/config.sh first}"
FULL="$GTDB_WORK/mcrA_genome_GTDB_R232_full.fasta"
TAX="$GTDB_WORK/mcrA_genome_GTDB_R232_taxonomy.tsv"
AMP="$GTDB_WORK/mcrA_genome_GTDB_R232_MLf_MLr.fasta"
AMPTAX="$GTDB_WORK/mcrA_genome_GTDB_R232_MLf_MLr_taxonomy.tsv"

cutadapt -g 'GGTGGTGTMGGATTCACACARTAYGCWACAGC...AACTAYCCWAACTAYGCAATGAA' -e 0.15 \
  --discard-untrimmed --minimum-length 350 --maximum-length 500 \
  -o "$AMP" "$FULL" > "$GTDB_WORK/cutadapt_MLf_MLr.log"

python - "$AMP" "$TAX" "$AMPTAX" <<'PY'
import sys
fasta,taxin,taxout=sys.argv[1:]; ids={l[1:].strip().split()[0] for l in open(fasta) if l.startswith('>')}; n=0
with open(taxin) as inp, open(taxout,'w') as out:
    for line in inp:
        if line.split('\t',1)[0] in ids: out.write(line); n+=1
print('Amplicon sequences:',len(ids)); print('Taxonomy records:',n)
if n!=len(ids): raise SystemExit('ERROR: FASTA/taxonomy count mismatch')
PY

python - "$AMP" <<'PY'
import sys
from collections import Counter
lengths=[]; seq=[]
for line in open(sys.argv[1]):
    line=line.strip()
    if line.startswith('>'):
        if seq: lengths.append(len(''.join(seq))); seq=[]
    else: seq.append(line)
if seq: lengths.append(len(''.join(seq)))
lengths.sort(); print('n:',len(lengths),'min:',min(lengths),'median:',lengths[len(lengths)//2],'max:',max(lengths))
print('common lengths:',Counter(lengths).most_common(10))
PY
