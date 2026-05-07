# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['/home/rm/ssddrive/claudecode/markitdown-tool/src/markitdown_gui/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[('/home/rm/ssddrive/claudecode/markitdown-tool/src/markitdown_gui/static', 'markitdown_gui/static'), ('/home/rm/.local/lib/python3.10/site-packages/magika/models', 'magika/models'), ('/home/rm/.local/lib/python3.10/site-packages/magika/config', 'magika/config')],
    hiddenimports=['markitdown.converters', 'markitdown.converters._pdf_converter', 'markitdown.converters._docx_converter', 'markitdown.converters._xlsx_converter', 'markitdown.converters._pptx_converter', 'markitdown.converters._html_converter', 'markitdown.converters._plain_text_converter', 'markitdown.converters._image_converter', 'markitdown.converters._audio_converter', 'markitdown.converters._csv_converter', 'markitdown.converters._epub_converter', 'markitdown.converters._zip_converter', 'markitdown.converters._ipynb_converter', 'markitdown.converters._rss_converter', 'markitdown.converters._wikipedia_converter', 'markitdown.converters._youtube_converter', 'markitdown.converters._bing_serp_converter', 'markitdown.converters._outlook_msg_converter', 'markitdown.converters._doc_intel_converter', 'uvicorn.logging', 'uvicorn.loops', 'uvicorn.loops.auto', 'uvicorn.protocols', 'uvicorn.protocols.http', 'uvicorn.protocols.http.auto', 'uvicorn.protocols.websockets', 'uvicorn.protocols.websockets.auto', 'uvicorn.lifespan', 'uvicorn.lifespan.on'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='markitdown-gui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
