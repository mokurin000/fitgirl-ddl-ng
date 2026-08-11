BIN_NAME=fitgirl_ddl_ngui
BIN_FILE="target/release/${BIN_NAME}.exe"

python_ver=3.14
python_full_ver=${python_ver}.7
python_num_ver=$(echo -n $python_ver | tr -cd '0-9')

(
    if ! [ -d "launcher" ]; then
        git clone --depth 1 \
            https://github.com/mokurin000/pyo3-simple-launcher \
            launcher
    fi

    cd launcher
    [ -d ".git" ] && git pull

    export CARGO_TARGET_DIR=target

    uv run generate.py "${BIN_NAME}" fitgirl_ddl_ng.gui.__main__:main
    cargo +nightly build --release
)

mkdir -p deploy-gui && cd deploy-gui || exit 1

python_zip="python-${python_full_ver}-embed-amd64"

# Download the latest python embed 3.14 build here

if ! [ -f "${python_zip}.zip" ]; then
    curl -LO "https://www.python.org/ftp/python/${python_full_ver}/${python_zip}.zip"
fi

output_dir="Lib"
rm -rf "${output_dir}" || exit 1

(
    mkdir -p "${output_dir}" && cd "${output_dir}" || exit 1
    unzip "../${python_zip}.zip"
)

# Install dependencies
pip3.14 install "..[gui]" -t Lib/site-packages

# Clean-up *.pyc
for dir in "__pycache__" "tests"; do
    find "Lib/site-packages" -name "$dir" -type d | xargs rm -rf
done
# Remove python interceptors
rm Lib/python{,w}.exe Lib/python${python_num_ver}._pth
mv Lib/python${python_num_ver}.dll .

cat > "python${python_num_ver}._pth" <<EOF
Lib/
Lib/python${python_num_ver}.zip
import site
EOF

cp "../launcher/${BIN_FILE}" .
