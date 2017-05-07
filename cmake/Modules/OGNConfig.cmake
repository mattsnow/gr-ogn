INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_OGN OGN)

FIND_PATH(
    OGN_INCLUDE_DIRS
    NAMES OGN/api.h
    HINTS $ENV{OGN_DIR}/include
        ${PC_OGN_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    OGN_LIBRARIES
    NAMES gnuradio-OGN
    HINTS $ENV{OGN_DIR}/lib
        ${PC_OGN_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
)

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(OGN DEFAULT_MSG OGN_LIBRARIES OGN_INCLUDE_DIRS)
MARK_AS_ADVANCED(OGN_LIBRARIES OGN_INCLUDE_DIRS)

