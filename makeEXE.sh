#!/bin/bash

echo "Building SimCenterBackendApplicationss ..."
mkdir -p build
cd build
conan install .. --build missing
status=$?; if [[ $status != 0 ]]; then echo "conan failed"; exit $status; fi
cmake ..
status=$?; if [[ $status != 0 ]]; then echo "cmake failed"; exit $status; fi
cmake --build . --config Release
status=$?; if [[ $status != 0 ]]; then echo "make failed"; exit $status; fi
cmake --install .
status=$?; if [[ $status != 0 ]]; then echo "make install failed"; exit $status; fi
make install .
cd ..




