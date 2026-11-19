"""Recover excluded Git metadata WITHOUT checking out/resetting working files.

Only for this sandbox's expired .cache/victoria.git pointer, not normal clones.
Fetch the exact recorded published commit read-only; if not yet published,
reconstruct its exact tree/commit from the recorded parent and retained files.
Missing inherited binaries must be unchanged from BASE. Missing superseded
inspection JSONs must match BOTH the indexed lossless archive and fetched Git
blob. Any other missing/changed deliverable fails closed. No checkout, reset,
clean, credential storage or remote write is used.
"""
from pathlib import Path, PurePosixPath
import hashlib
import json
import os
import subprocess
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[1]
BASE = '75bf4ac5770b803919b36c8dbdb5374df82d88ac'
BRANCH = 'agent/leonidas-ii'
URL = 'https://github.com/dreamer2664/victoria.git'
CACHE = Path.home() / '.cache' / 'victoria.git'
ARCHIVE_INDEX = 'docs/leonidas_ii/inspection/MICRO_INTERMEDIATE_HISTORY_INDEX.json'
SHA = lambda blob: hashlib.sha256(blob).hexdigest()


def main(root=ROOT, cache=CACHE, base=BASE, branch=BRANCH, url=URL):
    root, cache = Path(root), Path(cache)
    env = os.environ.copy()
    env['GIT_TERMINAL_PROMPT'] = '0'

    def git(*args, check=True, **kw):
        return subprocess.run(['git', *args], cwd=root, env=kw.pop('env', env),
                              check=check, capture_output=True, **kw)

    def output(*args):
        return git(*args).stdout.decode().strip()

    def oid(value):
        return isinstance(value, str) and len(value) == 40 and all(c in '0123456789abcdef' for c in value)

    def safe_path(value):
        p = PurePosixPath(value)
        return value == str(p) and not p.is_absolute() and '..' not in p.parts and '.git' not in p.parts

    present = git('rev-parse', '--verify', 'HEAD', check=False)
    if present.returncode == 0:
        print('Git metadata is present; no changes made. HEAD', present.stdout.decode().strip())
        return 0
    pointer = root / '.git'
    if pointer.exists() and (not pointer.is_file() or pointer.read_text().strip() != f'gitdir: {cache}'):
        raise RuntimeError('Unknown Git metadata/pointer; nothing replaced. Recover manually.')
    if cache.exists():
        raise RuntimeError('Cache exists but HEAD is invalid; nothing replaced. Inspect manually.')
    record = root / 'docs/leonidas_ii/PUBLICATION.json'
    r = json.loads(record.read_text()) if record.is_file() else None
    parent = r.get('parent', base) if r else base
    if r and (r.get('base', base) != base or r.get('branch') != branch or
              not all(oid(r.get(k)) for k in ('commit', 'tree')) or not oid(parent) or
              not all(safe_path(p) for p in r.get('changed_paths', []))):
        raise RuntimeError('Invalid publication receipt; nothing replaced.')
    cache.parent.mkdir(parents=True, exist_ok=True)
    if pointer.exists():
        pointer.unlink()  # only the verified dangling pointer, never working assets
    git('init', '--initial-branch=' + branch, '--separate-git-dir=' + str(cache), '.')
    git('remote', 'add', 'origin', url)
    git('fetch', '--no-tags', '--depth=1', 'origin', base)
    if parent != base:
        git('fetch', '--no-tags', '--depth=1', 'origin', parent)
    fetched = bool(r) and git('fetch', '--no-tags', '--depth=1', 'origin', r['commit'], check=False).returncode == 0
    ref = r['commit'] if fetched else parent
    if fetched and output('show', '-s', '--format=%T', ref) != r['tree']:
        raise RuntimeError('Fetched commit tree differs from receipt; working files untouched.')
    # read-tree without -u changes ONLY the index. Never use sparse-checkout set,
    # checkout or reset to recover metadata over a modified working directory.
    git('read-tree', ref)
    tree_rows = {}
    for row in git('ls-tree', '-rz', ref).stdout.split(b'\0'):
        if row:
            meta, name = row.split(b'\t', 1)
            tree_rows[name.decode()] = meta.decode()
    base_rows = {}
    for row in git('ls-tree', '-rz', base).stdout.split(b'\0'):
        if row:
            meta, name = row.split(b'\t', 1)
            base_rows[name.decode()] = meta.decode()
    missing = [p for p in tree_rows if not (root / p).is_file()]
    archived = {}
    index = root / ARCHIVE_INDEX
    if index.is_file():
        a = json.loads(index.read_text())
        archive = root / a['archive']
        if not safe_path(a['archive']) or SHA(archive.read_bytes()) != a['archive_sha256']:
            raise RuntimeError('Historical archive identity mismatch; working files untouched.')
        with tarfile.open(archive, 'r:xz') as t:
            for v in a['files']:
                if v['file'] in missing and v['file'].startswith('docs/leonidas_ii/inspection/'):
                    blob = t.extractfile(v['file']).read()
                    if len(blob) != v['bytes'] or SHA(blob) != v['sha256']:
                        raise RuntimeError('Archived inspection identity mismatch: ' + v['file'])
                    archived[v['file']] = blob
    for p in missing:
        parts = PurePosixPath(p).parts
        inherited = ((len(parts) == 2 and parts[0] == 'models' and p.endswith('.blend')) or
                     p.startswith(('exports/glb/', 'exports/fbx/', 'renders/exterior/', 'renders/interiors/',
                                   'renders/machinery/', 'renders/check/', 'renders/structure/')) or
                     p in ('reference/reference_board.png', 'reference/reference_board.pdf') or
                     (len(parts) == 2 and parts[0] == 'drawings' and p.endswith(('.png', '.pdf'))))
        if inherited and tree_rows[p] == base_rows.get(p):
            continue
        if p in archived and git('show', ref + ':' + p).stdout == archived[p]:
            continue
        raise RuntimeError('Missing deliverable is NOT an unchanged inherited/verified archived omission: ' + p)
    if missing:
        git('update-index', '--skip-worktree', '--stdin', input=('\n'.join(missing) + '\n').encode())
    git('config', 'core.sparseCheckout', 'true')
    git('config', 'core.sparseCheckoutCone', 'false')
    sparse = cache / 'info/sparse-checkout'
    sparse.parent.mkdir(parents=True, exist_ok=True)
    sparse.write_text('/*\n' + ''.join('!/' + p + '\n' for p in missing))
    if r and not fetched:
        paths = r['changed_paths']
        for p in paths:
            if not (root / p).is_file():
                raise RuntimeError('Missing changed deliverable: ' + p)
        if paths:
            git('add', '--sparse', '--', *paths)
        tree = output('write-tree')
        if tree != r['tree']:
            raise RuntimeError('Retained files differ from recorded tree. Index kept for inspection; no working file replaced.')
        replay = env.copy()
        for role in ('author', 'committer'):
            for key in ('name', 'email', 'date'):
                replay['GIT_' + role.upper() + '_' + key.upper()] = r[role][key]
        commit = git('commit-tree', tree, '-p', parent, input=r['message'].encode(), env=replay).stdout.decode().strip()
        if commit != r['commit']:
            raise RuntimeError('Reconstructed commit differs from receipt; branch not replaced.')
        ref = commit
    git('update-ref', 'refs/heads/' + branch, ref)
    print('Recovered exact Git metadata at', ref, '; verified sparse omissions:', len(missing))
    print('No working file was checked out/reset/deleted. No credential stored or remote write occurred.')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (RuntimeError, subprocess.CalledProcessError) as exc:
        raise SystemExit(str(exc))
