"""Refresh a reviewable file manifest or validate and create a clean local ZIP.

With Git, the candidate manifest is tracked files plus unignored new files.
Without Git, an existing SHA256SUMS.txt remains the release inventory.
Caches, source downloads, node_modules, reports and previous ZIPs are excluded.
"""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import os
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'SHA256SUMS.txt'
EXCLUDED = {'work','outputs','releases','validation','dist','build','node_modules','.git',
            '.idea','.vscode','.agents','.codex','__pycache__','.venv','venv'}


def eligible(rel):
    parts = PurePosixPath(rel).parts
    return (bool(parts) and not any(x in EXCLUDED for x in parts)
            and rel != 'SHA256SUMS.txt' and not rel.startswith('.env')
            and not rel.endswith(('.zip','.7z','.log','.tmp','.pyc')))


def safe_path(rel):
    path = (ROOT / rel).resolve()
    if not path.is_relative_to(ROOT) or not path.is_file():
        raise ValueError('Missing or out-of-tree release file: ' + rel)
    return path


def candidates():
    if (ROOT / '.git').exists():
        names = set()
        for args in (['ls-files','-z'], ['ls-files','--others','--exclude-standard','-z']):
            out = subprocess.check_output(['git',*args],cwd=ROOT)
            names.update(x for x in out.decode('utf-8').split('\0') if x)
        return sorted(n for n in names if eligible(n))
    if MANIFEST.exists():
        return sorted(line.split('  ',1)[1] for line in MANIFEST.read_text(encoding='utf-8').splitlines())
    raise ValueError('A Git checkout or existing SHA256SUMS.txt is required.')


def refresh():
    rows = [hashlib.sha256(safe_path(rel).read_bytes()).hexdigest() + '  ' + rel for rel in candidates()]
    MANIFEST.write_bytes(('\n'.join(rows)+'\n').encode('utf-8'))
    print(f'Refreshed {len(rows)} manifest entries.')


def package():
    if not MANIFEST.exists():
        raise ValueError('Create SHA256SUMS.txt first with --refresh-checksums.')
    inventory = [line.split('  ',1)[1] for line in MANIFEST.read_text(encoding='utf-8').splitlines()]
    if inventory != candidates():
        raise ValueError('File inventory changed; review it and use --refresh-checksums before packaging.')
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1')
    subprocess.run([sys.executable,'-B','-X','utf8',str(ROOT/'tools/check_all.py')],cwd=ROOT,env=env,check=True)
    kb = json.loads((ROOT/'data/kb.json').read_text(encoding='utf-8'))
    version = kb['metadata']['version']
    directory = ROOT / 'releases'
    directory.mkdir(exist_ok=True)
    target = directory / f'丰川祥子_标准版结构化知识库_v{version}.zip'
    # Preserve prior archives by refusing to overwrite an existing release.
    if target.exists():
        raise FileExistsError('Release already exists: ' + str(target))
    prefix = f'sakiko-knowledge-base-v{version}/'
    payload = inventory + ['SHA256SUMS.txt']
    with zipfile.ZipFile(target,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for rel in payload:
            z.write(safe_path(rel),prefix+rel)
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None, 'ZIP CRC failed'
        assert z.namelist() == [prefix+rel for rel in payload], 'ZIP inventory mismatch'
        assert all(z.read(prefix+rel) == safe_path(rel).read_bytes() for rel in payload), 'ZIP byte mismatch'
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    target.with_suffix('.zip.sha256').write_bytes((digest+'  '+target.name+'\n').encode('utf-8'))
    print(json.dumps(dict(zip=str(target),files=len(payload),sha256=digest,
                          checks='all validation tools, ZIP CRC, inventory and byte comparison passed'),ensure_ascii=False,indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh-checksums',action='store_true')
    parser.add_argument('--zip',action='store_true',help='Validate and package the reviewed manifest.')
    args = parser.parse_args()
    if not args.refresh_checksums and not args.zip:
        parser.error('Choose --refresh-checksums and/or --zip.')
    if args.refresh_checksums:
        refresh()
    if args.zip:
        package()


if __name__ == '__main__':
    main()
