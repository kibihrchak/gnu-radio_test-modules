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
from simple_message_publisher import simple_message_publisher

class qa_simple_message_publisher (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        import array
        import pmt


        divisor = 3
        input_len = 20


        #   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #   Create input

        data_src = array.array('B')
        data_expected = array.array('B')

        for i in range(input_len):
            data_src.append(i)

            if i % divisor == 0:
                data_expected.append(i)


        #   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #   Create, connect blocks

        src = blocks.vector_source_b(data_src)
        msg_pub = simple_message_publisher(divisor)
        dst = blocks.message_debug()
        dst_int = blocks.message_debug()

        self.tb.connect(src, msg_pub)
        self.tb.msg_connect(msg_pub, 'out', dst, 'store')
        self.tb.msg_connect(msg_pub, 'out_int', dst_int, 'store')


        #   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #   Kick

        self.tb.run ()


        #   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #   Check

        self.assertEqual(len(data_expected), dst.num_messages())
        self.assertEqual(len(data_expected), dst_int.num_messages())

        print("Byte vector input")
        print("<meta>|<msg>|<message_str>")

        for i in range(dst.num_messages()):
            message_pmt = dst.get_message(i)

            meta = pmt.to_python(pmt.car(message_pmt))
            msg = pmt.cdr(message_pmt)

            message_str = "".join([
                chr(x) for x in pmt.u8vector_elements(msg)])

            print(str(meta) + "|" + str(msg) + "|" + message_str)

            message_num = int(message_str)

            self.assertEqual(message_num, data_expected[i])


        print("Int vector input")
        print("<meta>|<msg>|<message_str>")

        for i in range(dst_int.num_messages()):
            message_pmt = dst_int.get_message(i)

            meta = pmt.to_python(pmt.car(message_pmt))
            msg = pmt.cdr(message_pmt)


            message_val = pmt.to_long(msg)

            print(str(meta) + "|" + str(msg) + "|" + str(message_val))

            self.assertEqual(message_val, data_expected[i])


if __name__ == '__main__':
    gr_unittest.run(qa_simple_message_publisher, "qa_simple_message_publisher.xml")
