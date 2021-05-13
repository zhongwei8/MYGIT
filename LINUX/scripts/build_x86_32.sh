#!/bin/bash

set -e

export CFLAGS="-fPIC"
export CXXFLAGS="-fPIC -I${BUILD_DIR}/third_party/install/gtest/include"

OS='linux'
ARCH='x86_32'
BUILD_TYPE="Release"
CUSTOM_SYSTEM_NAME="${OS}-${ARCH}"
BUILD_DIR="build_${CUSTOM_SYSTEM_NAME}"/
INSTALL_DIR="output/${CUSTOM_SYSTEM_NAME}"

# Clear
echo "Clean build directory: ${BUILD_DIR}"
rm -rf ${BUILD_DIR}

cmake -B${BUILD_DIR} \
      -DOS=$OS \
      -DARCH=$ARCH \
      -DCMAKE_INSTALL_PREFIX=${INSTALL_DIR} \
      -DCMAKE_BUILD_TYPE=${BUILD_TYPE} \
      -DX86_32=ON \
      . || exit 1

cmake --build ${BUILD_DIR} --target install || exit 1

# Package
cd ${BUILD_DIR}
make package
cd -
