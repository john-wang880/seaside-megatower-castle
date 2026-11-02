"""Root SHA256SUMS inventory using NUL-delimited Git paths, including Unicode/spaces."""
import argparse,hashlib,os,subprocess
from pathlib import Path

def manifest_for_paths(root,names):
 root=Path(root).resolve();lines=[]
 for name in sorted(set(names)):
  if name=='SHA256SUMS.txt':continue
  p=Path(name)
  if p.is_absolute()or '..'in p.parts or any(c in name for c in '\n\r\\\0'):raise ValueError('Unsupported or unsafe checksum path')
  f=root/p
  if f.is_symlink():raise ValueError('Symlink checksum target refused')
  if not f.is_file():continue # Intentional deleted paths are absent from the next current tree.
  if not f.resolve().is_relative_to(root):raise ValueError('Checksum path escaped repository')
  h=hashlib.sha256()
  with f.open('rb')as stream:
   for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
  lines.append(h.hexdigest()+'  '+name+'\n')
 return ''.join(lines)

def expected(root):
 top=Path(subprocess.check_output(['git','rev-parse','--show-toplevel'],cwd=root,text=True).strip()).resolve()
 if top!=Path(root).resolve():raise ValueError('Run from an actual repository root, not a nested archive')
 raw=subprocess.check_output(['git','ls-files','-z','--cached','--others','--exclude-standard'],cwd=root)
 return manifest_for_paths(root,[os.fsdecode(n)for n in raw.split(b'\0')if n])

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);g=ap.add_mutually_exclusive_group(required=True);g.add_argument('--check',action='store_true');g.add_argument('--write',action='store_true');a=ap.parse_args();root=a.root.resolve();target=root/'SHA256SUMS.txt'
 if target.is_symlink():raise ValueError('Symlink checksum output refused')
 text=expected(root)
 if a.check:
  if not target.is_file()or target.read_text()!=text:raise SystemExit('Root checksum inventory differs; review paths before --write')
  print('Complete root checksum inventory matches Git paths.')
 else:target.write_text(text);print('Wrote complete root checksum inventory.')
if __name__=='__main__':main()
