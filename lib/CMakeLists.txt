# Copyright 2011,2012,2016 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.

########################################################################
# Setup library
########################################################################
include(GrPlatform) #define LIB_SUFFIX

include_directories(${Boost_INCLUDE_DIR})
link_directories(${Boost_LIBRARY_DIRS})

list(APPEND test_module_sources
)

set(test_module_sources "${test_module_sources}" PARENT_SCOPE)
if(NOT test_module_sources)
	MESSAGE(STATUS "No C++ sources... skipping lib/")
	return()
endif(NOT test_module_sources)

add_library(gnuradio-test_module SHARED ${test_module_sources})
target_link_libraries(gnuradio-test_module ${Boost_LIBRARIES} ${GNURADIO_ALL_LIBRARIES})
set_target_properties(gnuradio-test_module PROPERTIES DEFINE_SYMBOL "gnuradio_test_module_EXPORTS")

if(APPLE)
    set_target_properties(gnuradio-test_module PROPERTIES
        INSTALL_NAME_DIR "${CMAKE_INSTALL_PREFIX}/lib"
    )
endif(APPLE)

########################################################################
# Install built library files
########################################################################
include(GrMiscUtils)
GR_LIBRARY_FOO(gnuradio-test_module RUNTIME_COMPONENT "test_module_runtime" DEVEL_COMPONENT "test_module_devel")

########################################################################
# Build and register unit test
########################################################################
include(GrTest)

include_directories(${CPPUNIT_INCLUDE_DIRS})

list(APPEND test_test_module_sources
    ${CMAKE_CURRENT_SOURCE_DIR}/test_test_module.cc
    ${CMAKE_CURRENT_SOURCE_DIR}/qa_test_module.cc
)

add_executable(test-test_module ${test_test_module_sources})

target_link_libraries(
  test-test_module
  ${GNURADIO_RUNTIME_LIBRARIES}
  ${Boost_LIBRARIES}
  ${CPPUNIT_LIBRARIES}
  gnuradio-test_module
)

GR_ADD_TEST(test_test_module test-test_module)

########################################################################
# Print summary
########################################################################
message(STATUS "Using install prefix: ${CMAKE_INSTALL_PREFIX}")
message(STATUS "Building for version: ${VERSION} / ${LIBVER}")

