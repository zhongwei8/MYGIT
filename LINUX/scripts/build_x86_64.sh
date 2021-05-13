#!/bin/bash

set -e

OS='linux'
ARCH='x86_64'
BUILD_TYPE="Release"
CUSTOM_SYSTEM_NAME="${OS}-${ARCH}"
BUILD_DIR="$(pwd)/build_${CUSTOM_SYSTEM_NAME}"
INSTALL_DIR="output/${CUSTOM_SYSTEM_NAME}"

# Clear
echo "Clean build directory: ${BUILD_DIR}"
rm -rf "${BUILD_DIR}"

echo "Clean output directory: ${INSTALL_DIR}"
rm -rf ${INSTALL_DIR}

cmake -B"${BUILD_DIR}" \
      -DOS=$OS \
      -DARCH=$ARCH \
      -DCMAKE_INSTALL_PREFIX=${INSTALL_DIR} \
      -DCMAKE_BUILD_TYPE=${BUILD_TYPE} \
      -DMIOT_HAR_ENABLE_TESTS=ON \
      . || exit 1

cmake --build "${BUILD_DIR}" --target install || exit 1

cd "${BUILD_DIR}"
make test CTEST_OUTPUT_ON_FAILURE=TRUE GTEST_COLOR=TRUE
make install
make package
cd -

# Test Python module import
export PYTHONPATH=${BUILD_DIR}:${PYTHONPATH}
python3 -c "import src.c.har_detector.har_detector"
python3 -c "import src.c.har_model.har_model"
python3 -c "import mi_har_py"
python3 -c "import mi_ior_py"
