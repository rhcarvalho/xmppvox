# -*- mode: python -*-
a = Analysis([os.path.join(HOMEPATH,'support\\_mountzlib.py'), os.path.join(CONFIGDIR,'support\\useUnicode.py'), 'xmppvox.py'],
             pathex=[os.getcwd()],           # Assume we are running from the XMPPVOX project root.
             hookspath=None)
pyz = PYZ(a.pure)
exe = EXE( pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=os.path.join('dist', 'xmppvox.exe'),
          debug=False,
          strip=None,
          upx=True,
          console=True )
