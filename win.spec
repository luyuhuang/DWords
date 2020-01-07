# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['win.py',
              'DWords/__init__.py',
              'DWords/__main__.py',
              'DWords/app.py',
              'DWords/async_thread.py',
              'DWords/danmaku.py',
              'DWords/db.py',
              'DWords/home.py',
              'DWords/launcher.py',
              'DWords/mail.py',
              'DWords/migrate.py',
              'DWords/setting.py',
              'DWords/synchronizer.py',
              'DWords/utils.py',
              'DWords/version.py'
             ],
             binaries=[],
             datas=[('DWords/data/dictionary.db', 'DWords/data/'), ('DWords/img/logo.svg', 'DWords/img/')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='DWords',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False , icon='logo.ico')
