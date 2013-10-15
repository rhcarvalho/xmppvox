# -*- mode: python -*-
import glob
import os.path
a = Analysis(['main.py'],
             pathex=['.'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries + [(os.path.basename(s), s, 'DATA') for s in glob.iglob('scripts/*.cmd')],
          a.zipfiles,
          a.datas,
          name='xmppvox.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True , version='version')
