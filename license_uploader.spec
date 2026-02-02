# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for License Uploader
This packages the Flask application into a standalone executable
"""

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all Flask template and static files
datas = [
    ('templates', 'templates'),
    ('static', 'static'),
    ('.env.example', '.'),
]

# Collect hidden imports that PyInstaller might miss
hiddenimports = [
    # Local modules (explicitly include)
    'config',
    'document_parser',
    'llm_extractor',
    'alma_api',
    'license_terms_data',
    # Flask and extensions
    'flask',
    'flask_wtf',
    'flask_wtf.csrf',
    'flask_talisman',
    'flask_limiter',
    'flask_limiter.util',
    'werkzeug',
    'werkzeug.security',
    'werkzeug.utils',
    'jinja2',
    # AI/LLM
    'openai',
    'httpx',
    # Document processing
    'pypdf',
    'docx',
    'bs4',
    'lxml',
    'lxml.etree',
    'lxml._elementpath',
    # HTTP and utilities
    'requests',
    'dotenv',
    'cryptography',
    'magic',
    # Standard library (sometimes needs explicit inclusion)
    'pathlib',
    'tempfile',
    'logging.handlers',
    'json',
    'datetime',
    're',
]

# Platform-specific imports
if sys.platform == 'win32':
    hiddenimports.extend(['waitress', 'magic.compat'])
else:
    hiddenimports.extend(['gunicorn'])

# Collect submodules for complex packages
hiddenimports.extend(collect_submodules('flask'))
hiddenimports.extend(collect_submodules('werkzeug'))
hiddenimports.extend(collect_submodules('jinja2'))

# Collect data files for packages that need them
datas.extend(collect_data_files('flask'))
datas.extend(collect_data_files('jinja2'))

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='license_uploader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Set to False for no console window (Windows only)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you have one: 'icon.ico' or 'icon.icns'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='license_uploader',
)
