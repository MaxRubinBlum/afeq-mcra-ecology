#!/usr/bin/env python3
"""Summarize controls and identify control-exclusive ASVs / low-depth samples."""
import argparse,csv,re

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('feature_table'); ap.add_argument('--min-sample-reads',type=int,default=1000)
    ap.add_argument('--control-exclusive-out',default='control_exclusive_asvs.txt'); ap.add_argument('--low-samples-out',default='low_depth_samples.tsv'); a=ap.parse_args()
    with open(a.feature_table) as fh:
        first=fh.readline()
        if not first.startswith('# Constructed from biom'): fh.seek(0)
        head=fh.readline().rstrip().split('\t'); samples=head[1:]
        ctrl=[i for i,s in enumerate(samples) if re.search(r'blank|ntc',s,re.I)]; bio=[i for i in range(len(samples)) if i not in ctrl]
        totals=[0]*len(samples); ctrl_ex=[]; control_asvs=0
        for line in fh:
            p=line.rstrip().split('\t'); asv=p[0]; vals=[int(float(x)) for x in p[1:]]
            for i,v in enumerate(vals): totals[i]+=v
            bc=sum(vals[i] for i in bio); cc=sum(vals[i] for i in ctrl)
            if cc>0: control_asvs+=1
            if cc>0 and bc==0: ctrl_ex.append((asv,cc))
    open(a.control_exclusive_out,'w').write(''.join(x[0]+'\n' for x in ctrl_ex))
    low=[(samples[i],totals[i]) for i in bio if totals[i]<a.min_sample_reads]
    with open(a.low_samples_out,'w',newline='') as out:
        wr=csv.writer(out,delimiter='\t'); wr.writerow(['sample-id','reads']); wr.writerows(sorted(low,key=lambda x:x[1]))
    print('biological samples:',len(bio),'controls:',len(ctrl)); print('biological reads:',sum(totals[i] for i in bio),'control reads:',sum(totals[i] for i in ctrl))
    print('ASVs in controls:',control_asvs); print('control-exclusive ASVs:',len(ctrl_ex),'reads:',sum(x[1] for x in ctrl_ex))
    print(f'biological samples <{a.min_sample_reads}:',len(low)); [print(' ',*x) for x in sorted(low,key=lambda x:x[1])]
if __name__=='__main__': main()
