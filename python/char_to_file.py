#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2017 Marko Oklobdzija
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

import numpy
from gnuradio import gr

class char_to_file(gr.sync_block):
    """
    docstring for block char_to_file
    """
    def __init__(self, output_filename, debug_filename):
        gr.sync_block.__init__(self,
            name="char_to_file",
            in_sig=[numpy.uint8],
            out_sig=None)

        self.output_file = open(output_filename, 'w')
        self.debug_file = open(debug_filename, 'w')

    def __del__(self):
        self.output_file.close()
        self.debug_file.close()

    def work(self, input_items, output_items):
        in0 = input_items[0]

        self.debug_file.write("Received data: " + repr(in0) + "\n")

        for i in in0:
            self.output_file.write(chr(i))

        self.output_file.flush()

        return len(input_items[0])

