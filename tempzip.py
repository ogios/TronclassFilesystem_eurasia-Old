import tempfile
import os
import traceback

# from Tools import ok, fatal

PATH = os.path.dirname(__file__) + "/Temp"
if not os.path.exists(PATH):
    os.mkdir(PATH)

tmp=tempfile.mkdtemp(prefix='tmp',dir=PATH)


def _compress(name,path):
    res=os.popen(f'7z.exe a {name} {path}')
    if 'Everything is Ok' in res.read():
        return 1
    else:
        return 0


def compress(dirpath):
    if os.path.exists(dirpath):
        name=tmp+'\\'+os.path.basename(dirpath)+'.zip'
        try:
            res=_compress(name,dirpath)
            if res:
                return name
            else:
                return 0
        except:
            traceback.print_exc()
            return 0
    else:
        return 2

if __name__=='__main__':
    # _dir=r'C:\Users\moiiii\Desktop\test'
    # tmp=tempfile.mkdtemp(prefix='tmp',dir=__file__ + '/Temp/')
    print(tmp)
