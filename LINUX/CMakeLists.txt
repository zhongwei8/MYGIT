cmake_minimum_required(VERSION 3.12)
project(activity_recognition VERSION 0.5.0)

##--------------------- Default values for IDE -----------------------------##
option(MIOT_HAR_ENABLE_TESTS "whether to build c++ unit tests" OFF)
if (NOT DEFINED OS)
  message(STATUS "OS not set, set to default: linux")
  set(OS "linux")
endif ()
if (NOT DEFINED ARCH)
  message(STATUS "ARCH not set, set to default: x86_64")
  set(ARCH "x86_64")
endif ()
if (NOT DEFINED LIB_TYPE)
  message(STATUS "LIB_TYPE not set, set to default: STATIC")
  set(LIB_TYPE "STATIC")
endif ()

if (OS STREQUAL "linux" AND ARCH STREQUAL "x86_64")
  set(HOST ON)
endif()
if (OS STREQUAL "android")
  set(LIB_TYPE "SHARED")
endif()

##--------------------- Version info ---------------------------------------##
execute_process(COMMAND bash "-c" "cd ${CMAKE_CURRENT_SOURCE_DIR} && git rev-parse --short HEAD" OUTPUT_VARIABLE GIT_COMMIT_ID OUTPUT_STRIP_TRAILING_WHITESPACE)
string(TIMESTAMP BUILD_DATE "%Y-%m-%d %H:%M")
set(VERSION_INFO_STRING "xiaomi_miot_algo_har_version: ${PROJECT_VERSION}.${GIT_COMMIT_ID} (${BUILD_DATE})")
set(VERSION_NAME_STRING "MiHAR-${PROJECT_VERSION}")
if (BUILD_INFO)
    set(VERSION_NAME_STRING ${VERSION_NAME_STRING}-${BUILD_INFO})
endif ()
configure_file("${PROJECT_SOURCE_DIR}/src/c/miot_algo_har_version.c.in" "${PROJECT_SOURCE_DIR}/src/c/miot_algo_har_version.c")
message(STATUS "Version info: ${VERSION_INFO_STRING}")
message(STATUS "Version name: ${VERSION_NAME_STRING}")

##--------------------- Compile Options ------------------------------------##
if (CMAKE_TOOLCHAIN_FILE)
    message(STATUS "Using toolchain file: ${CMAKE_TOOLCHAIN_FILE}")
endif()
add_compile_options(-Wall)
set(CMAKE_C_STANDARD 99)
set(CMAKE_C_FLAGS_RELEASE "${CMAKE_C_FLAGS_RELEASE} -O2")
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -O2")
if (HOST)
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fPIC")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fPIC")
endif()
if (${OS} STREQUAL "linux" AND ${ARCH} STREQUAL "x86_32")
  message(STATUS "Building configure for linux-x86_32: -m32")
  add_compile_options(-m32)
  add_link_options(-m32)
endif()

message(STATUS "CMAKE_C_COMPILER: ${CMAKE_C_COMPILER}")
message(STATUS "CMAKE_C_FLAGS: ${CMAKE_C_FLAGS}")
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")

##--------------------- Global Macros --------------------------------------##

##--------------------- Include path ---------------------------------------##
include_directories(src/c/) # Add the given directories to those the compile uses to search for include files.
                            # Relative paths are interpreted as relative to the current source directory.
include_directories(miot-algo-common/src/c)

##--------------------- Subdirectories -------------------------------------##
add_subdirectory(miot-algo-common EXCLUDE_FROM_ALL) # Add a subdirectory to the build. The source_dir specifies the directory in which the source
set(COMMON_LIB miot-algo-common)
add_subdirectory(src/c/har_model)
add_subdirectory(src/c/har_detector)

##--------------------- Source files ---------------------------------------##
set(MI_HAR_LIB_C
  src/c/activity_recognizer.c
  src/c/har_detector/har_detector.c
  src/c/har_model/har_model.c
  src/c/miot_algo_har_version.c
)

set(MI_HAR_LIB_H
  src/c/activity_recognizer.h
  src/c/activity_type.h
)

set(MI_IOR_LIB_C
  src/c/gpgsv/gpgsv_utils.c
  src/c/indoor_outdoor_recognizer.c
  src/c/miot_algo_har_version.c
)

##--------------------- Target lib and install -----------------------------##
if ((OS STREQUAL "linux") OR (OS STREQUAL "generic" AND ARCH STREQUAL "qdsp"))
  add_library(mi_har ${LIB_TYPE} ${MI_HAR_LIB_C})
  set_target_properties(mi_har PROPERTIES PUBLIC_HEADER "${MI_HAR_LIB_H}")
endif()

add_library(mi_ior ${LIB_TYPE} ${MI_IOR_LIB_C})
set_target_properties(mi_ior PROPERTIES PUBLIC_HEADER src/c/indoor_outdoor_recognizer.h)

##--------------------- Install and Package --------------------------------##
set(CPACK_GENERATOR "ZIP")
set(CPACK_PACKAGE_NAME "MiHAR")
set(CPACK_SET_DESTDIR ON)
set(CPACK_INSTALL_PREFIX "")
set(CPACK_PACKAGE_VERSION ${PROJECT_VERSION})
if (BUILD_INFO)
    set(CPACK_PACKAGE_VERSION ${CPACK_PACKAGE_VERSION}-${BUILD_INFO})
endif ()
set(CPACK_SYSTEM_NAME ${OS})
if (ARCH)
    set(CPACK_SYSTEM_NAME ${CPACK_SYSTEM_NAME}-${ARCH})
endif ()
set(CPACK_OUTPUT_FILE_PREFIX ${CMAKE_INSTALL_PREFIX})
set(CMAKE_INSTALL_PREFIX ${CMAKE_INSTALL_PREFIX}/${VERSION_NAME_STRING})

if ((OS STREQUAL "linux") OR (OS STREQUAL "generic" AND ARCH STREQUAL "qdsp"))
  set(HAR_MODEL_EXTRA_LIB_PATH ${CMAKE_CURRENT_SOURCE_DIR}/lib/${ARCH}/)
  find_library(LIB_HAR_CNN model_har_cnn HINTS ${HAR_MODEL_EXTRA_LIB_PATH})
  find_library(LIB_MICRO micro HINTS ${HAR_MODEL_EXTRA_LIB_PATH})
  target_link_libraries(mi_har ${LIB_HAR_CNN} ${LIB_MICRO})
  if (LIB_TYPE STREQUAL "STATIC")
    add_custom_command(OUTPUT libmi_har_all.a
      COMMAND bash ${CMAKE_CURRENT_SOURCE_DIR}/scripts/merge_lib.sh libmi_har_all.a $<TARGET_FILE:mi_har>  ${LIB_HAR_CNN} ${LIB_MICRO}
      DEPENDS mi_har
    )
    add_custom_target(mi_har_all ALL DEPENDS libmi_har_all.a)
    install(FILES ${CMAKE_CURRENT_BINARY_DIR}/libmi_har_all.a TYPE LIB)
    install(FILES ${MI_HAR_LIB_H} TYPE INCLUDE)
  else()
  install(TARGETS mi_har
    LIBRARY DESTINATION lib
    PUBLIC_HEADER DESTINATION include
  )
  endif()

else()
  install(TARGETS mi_ior
    LIBRARY DESTINATION lib
    PUBLIC_HEADER DESTINATION include
  )
endif()

##------------------- Dependencies lib and install -------------------------##
# Host Only
if(HOST)
  set_target_properties(mi_har PROPERTIES POSITION_INDEPENDENT_CODE TRUE)
  message("Build activity recognizer for python interface")
  pybind11_add_module(mi_har_py src/c/activity_recognizer_py.cc)
  set_target_properties(mi_har_py PROPERTIES POSITION_INDEPENDENT_CODE TRUE)
  target_link_libraries(mi_har_py PRIVATE mi_har PRIVATE ${COMMON_LIB})
  install(TARGETS mi_har_py LIBRARY DESTINATION lib)

  pybind11_add_module(mi_ior_py src/c/indoor_outdoor_recognizer_py.cc)
  set_target_properties(mi_ior_py PROPERTIES POSITION_INDEPENDENT_CODE TRUE)
  target_link_libraries(mi_ior_py PRIVATE mi_ior PRIVATE ${COMMON_LIB})
  install(TARGETS mi_ior_py LIBRARY DESTINATION lib)
endif()

# Unit Test
if(MIOT_HAR_ENABLE_TESTS)
  message(STATUS "Enable unit test")
  enable_testing()
  include_directories(miot-algo-common/third_party/googletest-1.10.x/googletest/include)
  include_directories(miot-algo-common/third_party/pybind11-2.4.3/include)
  add_subdirectory(test/c)
endif(MIOT_HAR_ENABLE_TESTS)

include(CPack)
