# -*- mode: python -*-
a = Analysis(['main.py'],
             pathex=['.'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries + [('xmppvox.cmd', 'scripts/xmppvox.cmd', 'DATA')],
          a.zipfiles,
          a.datas,
          name='xmppvox.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True , version='version')
