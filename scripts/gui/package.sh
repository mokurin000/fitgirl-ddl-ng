slug=fitgirl-ddl-ng

cd deploy-gui || exit 1
mkdir -p ${slug}

if [ -d "Lib" ]; then
    rm -rf ${slug}/* || exit 1
    mv Lib fitgirl_ddl_ngui.exe python*.dll python*._pth ${slug}/
fi

7z a -sfx7z.sfx -t7z -mx=9 -m0=lzma2 -md=256m -ms=on ${slug}.exe ${slug}/
