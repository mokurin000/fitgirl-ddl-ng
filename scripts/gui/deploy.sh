mkdir -p deploy-gui && cd deploy-gui || exit 1

python_ver=3.14
python_full_ver=${python_ver}.7
python_zip="python-${python_full_ver}-embed-amd64"

# Download the latest python embed 3.14 build here

if ! [ -f "${python_zip}.zip" ]; then
    curl -LO "https://www.python.org/ftp/python/${python_full_ver}/${python_zip}.zip"
fi
python_dir="python-embed-amd64"
rm -rf "${python_dir}" || exit 1
mkdir -p "${python_dir}" && cd "${python_dir}" || exit 1
unzip "../${python_zip}.zip"

# Enable the site-packages support
sed -i 's/#import site/import site/g' python3*._pth
# Install dependencies
pip3.14 install "../..[gui]" -t Lib/site-packages

# clean-up *.pyc
for dir in "__pycache__" "tests"; do
    find "Lib/site-packages" -name "$dir" -type d | xargs rm -rf
done

# TODO: GUI launcher without flashing console
