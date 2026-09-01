#!/usr/bin/env python3
import importlib.util
from pathlib import Path
p=Path(__file__).parents[1]/'scripts'/'01_make_manifests.py'; spec=importlib.util.spec_from_file_location('manifest',p); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

def test_sepjan_biological():
    x=m.parse_sepjan('2860mcrA-01-63-Sep24mcrA-EN1-1_S1322_L002_R1.fastq.gz'); assert x[:4]==('Sep24-EN1-1','63','Sep24','EN1-1') and x[4] is False
def test_sepjan_control():
    x=m.parse_sepjan('2860mcrA-63-blank1a_S1384_L002_R1.fastq.gz'); assert x[0]=='SepJan-blank1a' and x[4] is True
def test_aprjul_biological():
    x=m.parse_aprjul('3744b_01_501-Apr25-P1-3_S1_L001_R1_001.fastq.gz'); assert x[:4]==('Apr25-P1-3','501','Apr25','P1-3')
def test_aprjul_control():
    x=m.parse_aprjul('3744b_89_NTC1_S89_L001_R1_001.fastq.gz'); assert x[0]=='AprJul-NTC1' and x[4] is True
if __name__=='__main__':
    test_sepjan_biological(); test_sepjan_control(); test_aprjul_biological(); test_aprjul_control(); print('manifest parser tests passed')
