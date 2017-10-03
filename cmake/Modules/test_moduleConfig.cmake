INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_TEST_MODULE test_module)

FIND_PATH(
    TEST_MODULE_INCLUDE_DIRS
    NAMES test_module/api.h
    HINTS $ENV{TEST_MODULE_DIR}/include
        ${PC_TEST_MODULE_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    TEST_MODULE_LIBRARIES
    NAMES gnuradio-test_module
    HINTS $ENV{TEST_MODULE_DIR}/lib
        ${PC_TEST_MODULE_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
)

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(TEST_MODULE DEFAULT_MSG TEST_MODULE_LIBRARIES TEST_MODULE_INCLUDE_DIRS)
MARK_AS_ADVANCED(TEST_MODULE_LIBRARIES TEST_MODULE_INCLUDE_DIRS)

