"""Retrieve provider-hosted inputs and reject changes to the studied releases."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
from urllib.request import Request,urlopen
import hashlib
import json
import subprocess
import tarfile
import tempfile
import time

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data/raw'


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for b in iter(lambda:stream.read(1024*1024),b''):h.update(b)
    return h.hexdigest()


def ranged(url,path,workers=8):
    with urlopen(Request(url,method='HEAD'),timeout=60) as response:
        size=int(response.headers['Content-Length'])
    chunk=2_000_000
    with path.open('wb') as stream:stream.truncate(size)
    def part(start):
        end=min(start+chunk,size)-1
        for attempt in range(4):
            try:
                with urlopen(Request(url,headers={'Range':f'bytes={start}-{end}'}),timeout=120) as response:
                    expected=f'bytes {start}-{end}/{size}'
                    if response.status!=206 or response.headers.get('Content-Range')!=expected:
                        raise IOError('Server did not honor the requested byte range')
                    content=response.read()
                if len(content)!=end-start+1:raise IOError('Incomplete range')
                with path.open('r+b') as stream:stream.seek(start);stream.write(content)
                return
            except Exception:
                if attempt==3:raise
                time.sleep(attempt+1)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for future in as_completed([pool.submit(part,start) for start in range(0,size,chunk)]):future.result()


def main():
    RAW.mkdir(parents=True,exist_ok=True)
    sources=json.loads((ROOT/'data/sources.json').read_text())['files']
    for item in sources:
        path=RAW/item['filename']
        if path.exists() and sha(path)==item['sha256']:
            print('Verified existing',path.name,flush=True);continue
        with tempfile.TemporaryDirectory(prefix='map-expiry-',dir=RAW) as scratch:
            scratch=Path(scratch);download=scratch/'download'
            if item.get('archive_url'):
                ranged(item['archive_url'],download)
                with tarfile.open(download,'r:gz') as archive:
                    member=archive.getmember('Restatement_Matrices/Restatement_Matrices.dta')
                    if not member.isfile():raise IOError('Unexpected archive member')
                    with archive.extractfile(member) as stream, (scratch/'ready').open('wb') as dest:
                        for b in iter(lambda:stream.read(1024*1024),b''):dest.write(b)
                ready=scratch/'ready'
            elif item['provider']=='Federal Reserve Board':
                subprocess.run(['curl','-L','--fail','--retry','3','--max-time','180','-o',str(download),item['url']],check=True)
                ready=download
            else:
                ranged(item['url'],download);ready=download
            digest=sha(ready)
            if digest!=item['sha256']:
                raise IOError(f'Upstream input changed: {item["filename"]}; expected {item["sha256"]}, got {digest}. Do not silently replace the studied release.')
            ready.replace(path)
        print('Downloaded and verified',path.name,flush=True)


if __name__=='__main__':main()
