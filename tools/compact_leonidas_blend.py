"""Losslessly compact Blender's native Zstandard stream, not mesh decimation.
Requires Python zstandard. The decompressed .blend must be BYTE-IDENTICAL.
Run before source-hash-bound exports/renders. Normal Blender 4.2 opens it.
"""
from pathlib import Path
import hashlib,json,os,sys
import zstandard as zstd
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'models/leonidas_ii/Aurelian_1889.blend'
if len(sys.argv)>1:source=Path(sys.argv[1]).resolve()
assert source.read_bytes()[:4]==b'\x28\xb5\x2f\xfd', 'Expected Blender native Zstandard stream.'
scratch=ROOT/'exports/leonidas_ii/build';scratch.mkdir(parents=True,exist_ok=True)
output=scratch/'lossless_compacted.blend';before=source.stat().st_size;old_sha=hashlib.sha256(source.read_bytes()).hexdigest();h=hashlib.sha256();size=0
params=zstd.ZstdCompressionParameters.from_level(16,window_log=23,threads=2)
with source.open('rb') as f, zstd.ZstdDecompressor().stream_reader(f,read_across_frames=True) as reader, output.open('wb') as g, zstd.ZstdCompressor(compression_params=params).stream_writer(g) as writer:
 while chunk:=reader.read(1024*1024):h.update(chunk);size+=len(chunk);writer.write(chunk)
verify=hashlib.sha256()
with output.open('rb') as f,zstd.ZstdDecompressor().stream_reader(f,read_across_frames=True) as reader:
 while chunk:=reader.read(1024*1024):verify.update(chunk)
assert verify.hexdigest()==h.hexdigest(), 'Decompressed Blender bytes changed; refusing replacement.'
after=output.stat().st_size
if after<before:os.replace(output,source)
else:output.unlink();after=before
r=dict(method='Lossless native Zstandard recompression, level 16 / 8MiB window; no mesh/material/data edits',before_bytes=before,after_bytes=after,uncompressed_bytes=size,before_sha256=old_sha,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),decompressed_sha256=h.hexdigest(),decompressed_bytes_equal=True)
(ROOT/'docs/leonidas_ii/BLEND_COMPACTION.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
