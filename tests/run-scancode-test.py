"""Run the real interrpt.c key-table functions with Emscripten and Node.

Set EMSDK to an installed SDK root. Optional --baseline REF confirms that an
unpatched Git revision fails the non-aliasing assertion before running the fix.
The unused game/event-loop functions are removed by linker garbage collection.
"""
from pathlib import Path
import argparse, os, shutil, subprocess, sys, tempfile

root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--baseline');args=parser.parse_args()
if not os.environ.get('EMSDK'): raise SystemExit('Set EMSDK to the SDK root.')
sdk=Path(os.environ['EMSDK'])
node=os.environ.get('JNB_NODE') or shutil.which('node')
if not node: raise SystemExit('Install Node.js or set JNB_NODE.')
with tempfile.TemporaryDirectory(prefix='jumpnbump-scancode-') as tmp:
    tmp=Path(tmp)
    (tmp/'globals.h').write_text((root/'globals.pre').read_text().replace('%%DATADIR%%','assets'))
    env=dict(os.environ,EM_CONFIG=str(sdk/'.emscripten'),EMSDK_PYTHON=sys.executable)
    def run(source,label):
        output=tmp/(label+'.js')
        subprocess.run([sys.executable,str(sdk/'upstream/emscripten/emcc.py'),
            str(root/'tests/scancode-bounds.c'),str(source),'-I'+str(tmp),'-I'+str(root),
            '-O2','-DUSE_SDL','-sUSE_SDL=2','-ffunction-sections','-Wl,--gc-sections',
            '-sENVIRONMENT=node','-sASSERTIONS=1','-o',str(output)],env=env,check=True)
        result=subprocess.run([node,str(output)],capture_output=True,text=True)
        print(label+': '+('PASS' if result.returncode==0 else 'FAIL'))
        if result.returncode: print(result.stderr.splitlines()[0][:250])
        return result.returncode
    if args.baseline:
        original=tmp/'interrpt-baseline.c'
        original.write_bytes(subprocess.check_output(['git','show',args.baseline+':sdl/interrpt.c'],cwd=root))
        if run(original,'baseline')==0: raise SystemExit('Expected the unpatched alias regression to fail.')
    if run(root/'sdl/interrpt.c','fixed')!=0: raise SystemExit('Fixed regression failed.')
