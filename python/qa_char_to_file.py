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
from char_to_file import char_to_file

class qa_char_to_file (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        import tempfile
        import numpy
        import array


        data = array.array('B', "abcdefgh")

        output_file = tempfile.NamedTemporaryFile(mode='r')
        debug_file = tempfile.NamedTemporaryFile(mode='r')


        src = blocks.vector_source_b(data)
        chtof = char_to_file(output_file.name, debug_file.name)

        self.tb.connect(src, chtof)


        self.tb.run ()


        print(debug_file.read())

        output_file.seek(0)
        checkStatus = True

        for i in data:
            c = output_file.read(1)

            if (c != ""):
                ch = str(ord(c))
            else:
                ch = "Empty"

            print(ch + ", " + str(i))

            if (c == "") or (i != ord(c)):
                checkStatus = False
                break;


        output_file.close()
        debug_file.close()


        self.assertTrue(checkStatus)


if __name__ == '__main__':
    gr_unittest.run(qa_char_to_file, "qa_char_to_file.xml")
