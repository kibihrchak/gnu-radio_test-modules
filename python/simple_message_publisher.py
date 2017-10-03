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

import numpy
from gnuradio import gr
import pmt

class simple_message_publisher(gr.sync_block):
    """
    docstring for block simple_message_publisher
    """
    def __init__(self, divisor):
        gr.sync_block.__init__(self,
            name="simple_message_publisher",
            in_sig=[numpy.uint8],
            out_sig=None)

        self.__DIVISOR = divisor
        self.message_port_register_out(pmt.intern('out'))
        self.message_port_register_out(pmt.intern('out_int'))


    def post_message(self, value):
        value_str = str(value)

        send_pmt = pmt.make_u8vector(len(value_str), ord(' '))

        for i in range(len(value_str)):
            pmt.u8vector_set(send_pmt, i, ord(value_str[i]))

        self.message_port_pub(
                pmt.intern('out'),
                pmt.cons(pmt.PMT_NIL, send_pmt))

        self.message_port_pub(
                pmt.intern('out_int'),
                pmt.cons(pmt.PMT_NIL, pmt.from_long(int(value))))


    def work(self, input_items, output_items):
        in0 = input_items[0]

        for i in in0:
            if i % self.__DIVISOR == 0:
                self.post_message(i)

        return len(input_items[0])

