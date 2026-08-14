#!/usr/bin/env bash

set -e

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <python-version>"
    echo "Example: $0 3.14.7"
    exit 1
fi

python_full_ver="$1"

if ! [[ "$python_full_ver" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Invalid Python version: $python_full_ver"
    echo "Expected format: X.Y.Z"
    exit 1
fi

python_ver="${python_full_ver%.*}"
python_num_ver="${python_ver//./}"
pip_cmd="pip${python_ver}"

BIN_NAME=fitgirl_ddl_ngui
BIN_FILE="target/release/${BIN_NAME}.exe"

python_zip="python-${python_full_ver}-embed-amd64"

echo "Python version: ${python_full_ver}"
echo "Python ABI:     ${python_num_ver}"
echo "pip command:    ${pip_cmd}"

(
    if ! [ -d "launcher" ]; then
        git clone --depth 1 \
            https://github.com/mokurin000/pyo3-simple-launcher \
            launcher
    fi

    cd launcher

    [ -d ".git" ] && git pull

    export CARGO_TARGET_DIR=target

    uv run generate.py \
        "${BIN_NAME}" \
        fitgirl_ddl_ng.gui.__main__:main

    cargo +nightly build --release
)

mkdir -p deploy-gui
cd deploy-gui

# Download Python embeddable package.
if ! [ -f "${python_zip}.zip" ]; then
    curl -fLO \
        "https://www.python.org/ftp/python/${python_full_ver}/${python_zip}.zip"
fi

# Extract Python.
rm -rf Lib

mkdir -p Lib

(
    cd Lib
    unzip "../${python_zip}.zip"
)

# Install dependencies with the requested Python version.
"${pip_cmd}" install "..[gui]" -t Lib/site-packages

# Remove unnecessary files.
for dir in "__pycache__" "tests"; do
    find Lib/site-packages \
        -name "$dir" \
        -type d \
        -prune \
        -exec rm -rf {} +
done

# Remove Python executables and the original _pth file.
rm -f \
    Lib/python.exe \
    Lib/pythonw.exe \
    "Lib/python${python_num_ver}._pth"

# Get the Python DLL.
mv "Lib/python${python_num_ver}.dll" Lib/python3.dll .

rm -rf Lib/site-packages/bin

# Remove typing-only files and Cython sources.
find Lib/site-packages \
    \( \
        -name "py.typed" \
        -o -name "*.pyi" \
        -o -name "cython" \
    \) \
    -exec rm -rf {} +

# Pack selected Python libraries.
(
    cd Lib/site-packages

    rmdir */ 2>/dev/null || true

    7z a \
        -sdel \
        -mx9 \
        -mfb=273 \
        ../library.zip \
        *.dist-info \
        mss \
        wrapt \
        emoji \
        websockets \
        zendriver \
        colorama \
        deprecated \
        loguru \
        win32_setctime \
        asyncio_atexit.py
)

# Configure isolated Python path.
cat > "python${python_num_ver}._pth" <<EOF
Lib/
Lib/python${python_num_ver}.zip
Lib/library.zip
import site
EOF

# Copy launcher executable.
cp "../launcher/${BIN_FILE}" .

echo
echo "Deployment completed:"
echo "  ${PWD}/${BIN_NAME}.exe"
echo "  Python ${python_full_ver}"
