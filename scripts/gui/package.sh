slug=fitgirl-ddl-ng

cd deploy-gui || exit 1
mkdir -p ${slug}

if [ -d "python-embed-amd64" ]; then
    rm -rf ${slug}/* || exit 1
    mv python-embed-amd64 *.exe ${slug}/
fi

7z a -sfx7z.sfx -t7z -mx=9 -m0=lzma2 -md=256m -ms=on ${slug}.exe ${slug}/
