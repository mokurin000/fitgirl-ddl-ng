# -*- mode: python -*-

from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT


a = Analysis(
    ['src/fitgirl_ddl_ng/refresh_cookies/__main__.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[],
    noarchive=False,
)

b = Analysis(
    ['src/fitgirl_ddl_ng/scrape_links/__main__.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[],
    noarchive=False,
)

c = Analysis(
    ['src/fitgirl_ddl_ng/extract_ddl/__main__.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[],
    noarchive=False,
)


pyz_a = PYZ(a.pure)
pyz_b = PYZ(b.pure)
pyz_c = PYZ(c.pure)


exe_a = EXE(
    pyz_a,
    a.scripts,
    [],
    name='refresh-cookies',
    console=True,
)

exe_b = EXE(
    pyz_b,
    b.scripts,
    [],
    name='scrape-fitgirl',
    console=True,
)

exe_c = EXE(
    pyz_c,
    c.scripts,
    [],
    name='extract-ddl',
    console=True,
)


dist = COLLECT(
    exe_a,
    exe_b,
    exe_c,

    a.binaries,
    a.datas,
    a.zipfiles,

    b.binaries,
    b.datas,
    b.zipfiles,

    c.binaries,
    c.datas,
    c.zipfiles,

    name='fitgirl-tools',
)