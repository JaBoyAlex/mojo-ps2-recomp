"""Fail-closed source, Git object and release archive publication gate."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = set(json.loads((ROOT/'publication-files.json').read_text(encoding='utf-8')))
BINARY = {'MOJO.exe', 'chd_to_iso.exe'}
PATTERNS = [
    ('private-home-path', re.compile(rb'(?:[A-Za-z]:[/\\]Users[/\\](?!Public(?:[/\\]))[^\s\x00"<>]+|/ho' rb'me/[^/\s]+/|/Us' rb'ers/[^/\s]+/)')),
    ('private-key', re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')),
    ('credential', re.compile(rb'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|sk-proj-[A-Za-z0-9_-]{30,})')),
    ('game-data', re.compile(rb'(?:PS2 Memory ' rb'Card Format|\x7fELF\x01\x01\x01)')),
]

def check(name, data, release=False):
    failures=[]
    if name not in ALLOWED and not (release and name in BINARY):
        failures.append((name, 'not-allowlisted'))
    if len(data)>4*1024*1024:
        failures.append((name, 'unexpected-size'))
    if name in BINARY and not data.startswith(b'MZ'):
        failures.append((name, 'not-a-PE-helper'))
    scanned = data
    if name == 'MOJO.exe':
        # Exact assertion paths from the pinned public LLVM libc++abi CI build.
        prefix = b'/ho' b'me/runner/work/llvm-mingw/llvm-mingw/llvm-project/libcxxabi/src/'
        for suffix in (b'private_typeinfo.cpp', b'cxa_personality.cpp', b'fallback_malloc.cpp',
                       b'cxa_demangle.cpp', b'demangle/ItaniumDemangle.h', b'demangle/Utility.h'):
            scanned = scanned.replace(prefix+suffix, b'PUBLIC_LLVM_SOURCE')
    for kind, pattern in PATTERNS:
        if pattern.search(scanned) or pattern.search(scanned.replace(b'\x00',b'')):
            failures.append((name,kind))
    return failures

def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path)
    parser.add_argument('--git', action='store_true')
    args=parser.parse_args()
    failures=[]
    if args.archive:
        with zipfile.ZipFile(args.archive) as archive:
            names=archive.namelist()
            if len(names)!=len(set(names)): failures.append(('archive','duplicate-path'))
            for name in names:
                if not name.endswith('/'): failures+=check(name,archive.read(name),True)
            if not BINARY.issubset(names): failures.append(('archive','missing-helper'))
            if not ALLOWED.issubset(names): failures.append(('archive','missing-source-or-notice'))
    else:
        for name in sorted(ALLOWED):
            path=ROOT/name
            if not path.is_file() or path.is_symlink(): failures.append((name,'missing-or-link'))
            else: failures+=check(name,path.read_bytes())
    if args.git:
        for row in git('ls-files','-s').decode().splitlines():
            mode,oid,rest=row.split(' ',2); name=rest.split('\t',1)[1]
            if mode not in ('100644','100755'): failures.append((name,'unsafe-git-mode'))
            failures+=check(name,git('cat-file','blob',oid))
        for commit in git('rev-list','--all').decode().splitlines():
            meta=git('show','-s','--format=%ae%n%ce',commit).decode().splitlines()
            if any(not v.endswith('@users.noreply.github.com') for v in meta): failures.append(('git-metadata','non-noreply-email'))
            for row in git('ls-tree','-r',commit).decode().splitlines():
                left,name=row.split('\t',1); mode,kind,oid=left.split()
                if kind!='blob' or mode not in ('100644','100755'): failures.append((name,'unsafe-object')); continue
                failures+=check(name,git('cat-file','blob',oid))
    for name,kind in sorted(set(failures)):
        print(f'FAIL {kind}: {name}')  # Never print matched values.
    if failures: return 1
    print('PASS: explicit publication allowlist, privacy/proprietary patterns'+(', staged files and all Git history' if args.git else ''))
    return 0

if __name__=='__main__': sys.exit(main())
