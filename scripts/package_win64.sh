cd deploy || exit 1
rm -rf fitgirl-ddl-ng || exit 1

mkdir fitgirl-ddl-ng
mv python-embed-amd64 *.bat fitgirl-ddl-ng/

7z a -sfx7z.sfx -t7z -mx=9 -m0=lzma2 -md=256m -ms=on fitgirl-ddl-ng.exe fitgirl-ddl-ng/
