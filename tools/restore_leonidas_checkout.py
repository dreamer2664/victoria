"""Recover this sandbox's cached Git metadata without replacing working files.

Only needed if .git points at an expired /home/user/.cache/victoria.git.
A normal GitHub clone does NOT need this tool. No credentials, reset --hard,
clean, checkout --force, remote writes or force-pushes are used.

The sandbox's 128 MiB saved-file budget cannot hold redundant Git history,
reference clones AND the editable/exported deliverables. Git objects live in
an excluded cache, and unchanged inherited binary assets are sparsely checked
out. This does NOT delete/change those assets in the commit or on GitHub.
"""
from pathlib import Path
import os,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
BASE='75bf4ac5770b803919b36c8dbdb5374df82d88ac'
BRANCH='agent/leonidas-ii'
URL='https://github.com/dreamer2664/victoria.git'
CACHE=Path.home()/'.cache'/'victoria.git'
SPARSE=['/*','!/models/*.blend','!/exports/glb/','!/exports/fbx/','!/renders/exterior/','!/renders/interiors/','!/renders/machinery/','!/renders/check/','!/renders/structure/','!/reference/reference_board.*','!/drawings/*.png','!/drawings/*.pdf']

def git(*args,**kw):
 return subprocess.run(['git',*args],cwd=ROOT,check=True,text=True,**kw)

def output(*args):return git(*args,capture_output=True).stdout.strip()

p=subprocess.run(['git','rev-parse','--verify','HEAD'],cwd=ROOT,text=True,capture_output=True)
if p.returncode==0:
 print('Git metadata is present; no changes made. HEAD',p.stdout.strip());sys.exit(0)
pointer=ROOT/'.git'
if pointer.exists():
 if not pointer.is_file() or pointer.read_text().strip()!=f'gitdir: {CACHE}':
  sys.exit('Refusing to replace unknown Git metadata. Recover this checkout manually.')
 pointer.unlink()  # only our own dangling cache-pointer file, never user history
if CACHE.exists():sys.exit('Cache directory exists but HEAD was not valid. Inspect it manually; nothing overwritten.')
CACHE.parent.mkdir(parents=True,exist_ok=True)
git('init','--initial-branch='+BRANCH,'--separate-git-dir='+str(CACHE),'.')
git('remote','add','origin',URL)
git('fetch','--depth=1','origin',BASE)
git('reset','--mixed','FETCH_HEAD')  # index/ref only; never replaces worktree files
git('sparse-checkout','init','--no-cone')
git('sparse-checkout','set','--no-cone',*SPARSE)
record=ROOT/'docs'/'leonidas_ii'/'PUBLICATION.json'
if not record.exists():
 print('Base metadata restored. New work is still uncommitted; review git status.');sys.exit(0)
r=json.loads(record.read_text())
assert r['parent']==BASE and r['branch']==BRANCH
# Reconstitute exactly the recorded own-change tree, not everything in the
# workspace. Missing/edited deliverables fail the tree check, rather than
# inventing a replacement commit or overwriting the user's working files.
for file in r['changed_paths']:
 if not (ROOT/file).is_file():sys.exit('Missing deliverable: '+file+'; regenerate/recover it before reconstructing the commit.')
git('add','--sparse','--',*r['changed_paths'])
tree=output('write-tree')
if tree!=r['tree']:sys.exit('Working files differ from the recorded tree. Kept as staged changes; review manually.')
env=os.environ.copy()
for role in ('author','committer'):
 for key in ('name','email','date'):env['GIT_'+role.upper()+'_'+key.upper()]=r[role][key]
p=git('commit-tree',tree,'-p',BASE,input=r['message'],capture_output=True,env=env)
commit=p.stdout.strip()
assert commit==r['commit'],(commit,r['commit'])
git('update-ref','refs/heads/'+BRANCH,commit,BASE)
print('Recreated exact recorded local commit',commit)
print('No remote write occurred. Publish only after reviewing with: git push -u origin '+BRANCH)
