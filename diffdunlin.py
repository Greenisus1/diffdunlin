#!/usr/bin/env python3
"""Diffdunlin: bounded read-only UTF-8 text comparison and JSON change ranges."""
import argparse,difflib,json,os,stat,sys
from pathlib import Path
MAX_BYTES=1024*1024
MAX_LINES=5000

def safe(s):return ''.join(c if c.isprintable() else f'\\u{ord(c):04x}' for c in str(s))[:500]
def read(path):
    fd=os.open(Path(path).expanduser(),os.O_RDONLY|getattr(os,'O_NONBLOCK',0))
    with os.fdopen(fd,'rb') as f:
        if not stat.S_ISREG(os.fstat(f.fileno()).st_mode):raise ValueError('Choose a regular file.')
        raw=f.read(MAX_BYTES+1)
    if len(raw)>MAX_BYTES:raise ValueError('File exceeds 1 MiB.')
    text=raw.decode('utf-8')
    if '\x00' in text:raise ValueError('NUL bytes found; expected UTF-8 text.')
    if len(text.splitlines())>MAX_LINES:raise ValueError('More than 5000 lines. Narrow the input.')
    return text

def compare(a,b,ignore_trailing=False):
    # Keep terminators, including CRLF, and missing final newline as exact data.
    old=a.splitlines(keepends=True);new=b.splitlines(keepends=True)
    def normalized(line):
        if not ignore_trailing:return line
        tail='\r\n' if line.endswith('\r\n') else line[-1:] if line.endswith(('\r','\n')) else ''
        body=line[:-len(tail)] if tail else line
        return body.rstrip(' \t')+tail
    left=list(map(normalized,old));right=list(map(normalized,new));matcher=difflib.SequenceMatcher(None,left,right,autojunk=False)
    changes=[]
    for kind,i,j,k,l in matcher.get_opcodes():
        if kind=='equal':continue
        changes.append({'kind':kind,'old_range_zero_based_half_open':[i,j],'new_range_zero_based_half_open':[k,l],'old_lines':old[i:j],'new_lines':new[k:l]})
    return {'format':'diffdunlin-1','raw_equal':a==b,'comparison_equal':not changes,'ignore_trailing_spaces_tabs':ignore_trailing,'old_line_count':len(old),'new_line_count':len(new),'old_final_newline':a.endswith(('\r','\n')),'new_final_newline':b.endswith(('\r','\n')),'changes':changes}

def show(report,limit=100):
    print('\nDIFFDUNLIN | UTF-8 comparison')
    print('Raw equal:',report['raw_equal'],'| Comparison equal:',report['comparison_equal'],'| Change groups:',len(report['changes']))
    print('Old/new lines:',report['old_line_count'],'/',report['new_line_count'],'| Final newline:',report['old_final_newline'],'/',report['new_final_newline'])
    shown=0
    for ch in report['changes']:
        if shown>=limit:break
        print(ch['kind'].upper(),'old',ch['old_range_zero_based_half_open'],'new',ch['new_range_zero_based_half_open'])
        for sign,key in (('-','old_lines'),('+','new_lines')):
            for line in ch[key]:
                if shown>=limit:break
                # repr-like escaping preserves line endings and terminal safety.
                print(sign,safe(line));shown+=1
    if sum(len(c['old_lines'])+len(c['new_lines']) for c in report['changes'])>shown:print('Display capped. JSON keeps full change groups.')
    print('Ranges are zero-based, end-exclusive. No files were edited; no patch applied.')

def save(report,path):
    with open(Path(path).expanduser(),'x',encoding='utf-8') as f:json.dump(report,f,indent=2,ensure_ascii=False);f.write('\n')

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('before',nargs='?');p.add_argument('after',nargs='?');p.add_argument('--ignore-trailing',action='store_true');p.add_argument('--output');a=p.parse_args(argv)
    try:
        if a.before or a.after:
            if not a.before or not a.after:raise ValueError('Supply both before and after filenames.')
            report=compare(read(a.before),read(a.after),a.ignore_trailing);show(report)
            if a.output:save(report,a.output)
            return 0 if report['comparison_equal'] else 1
        while True:
            print('\nDIFFDUNLIN\n1 Compare two text files  0 Exit');c=input('> ').strip()
            if c=='0':return 0
            if c!='1':continue
            try:
                before=input('Before filename: ');after=input('After filename: ');ignore=input('Ignore trailing spaces/tabs only? y/N: ').strip().lower()=='y';report=compare(read(before),read(after),ignore);show(report);out=input('New JSON filename (blank skips): ').strip()
                if out:save(report,out)
            except (ValueError,OSError) as exc:print('Error:',safe(exc))
    except (EOFError,KeyboardInterrupt):print('\nBye.')
    except (ValueError,OSError) as exc:print('Error:',safe(exc),file=sys.stderr);return 2
    return 0
if __name__=='__main__':raise SystemExit(main())
