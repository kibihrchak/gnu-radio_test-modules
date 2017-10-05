#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2017 <+YOU OR YOUR COMPANY+>.
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

from gnuradio import gr, gr_unittest
from gnuradio import blocks
from si4432_simple_decoder import si4432_simple_decoder

class qa_si4432_simple_decoder (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        import tempfile
        import numpy

        SRC_FILENAME = 'in.bin'
        PREAMBLE_LEN_UNITS = 4
        SYNC_WORD = (0x2d, 0xd4)
        HEADER_LEN = 4

        output_file = tempfile.NamedTemporaryFile(mode='r')


        #   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #   Create, connect blocks

        src = blocks.file_source(gr.sizeof_char*1, SRC_FILENAME, False)
        dec = si4432_simple_decoder(
                PREAMBLE_LEN_UNITS, SYNC_WORD, HEADER_LEN,
                output_file.name)
        dst = blocks.message_debug()

        self.tb.connect(src, dec)
        self.tb.msg_connect(dec, 'out', dst, 'print')


        #   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #   Kick

        self.tb.run ()


        #   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #   Check

        print(output_file.read())


        #   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #   Cleanup

        output_file.close()


if __name__ == '__main__':
    gr_unittest.run(qa_si4432_simple_decoder, "qa_si4432_simple_decoder.xml")
