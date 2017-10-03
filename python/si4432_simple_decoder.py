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
import logging
import array

logging.basicConfig(level=logging.DEBUG)


class StateMachine:
    class State:
        pass


class si4432_simple_decoder(gr.sync_block):
    """
    docstring for block si4432_simple_decoder
    """

    class PacketDecoder(StateMachine):
        class Preamble(StateMachine.State):
            __PREAMBLE_PATTERN = array.array('B', [0x00, 0x01])

            def __get_next_lookup(self):
                return self.__PREAMBLE_PATTERN[self.__sequence_counter %
                        len(self.__PREAMBLE_PATTERN)]

            def __init__(self, state_machine):
                self.__state_machine = state_machine
                self.__SEQUENCE_LENGTH = \
                        self.__state_machine.PREAMBLE_LENGHT

                self.__sequence_counter = 0
                self.__looking_for = self.__get_next_lookup()

            def run(self, input_data):
                if input_data == self.__looking_for:
                    self.__sequence_counter = \
                            self.__sequence_counter + 1

                    if self.__sequence_counter == \
                            self.__SEQUENCE_LENGTH:
                        logging.debug("Preamble found")
                        return (PacketDecoder.SyncWord(
                            self.__state_machine), 1)
                    else:
                        self.__looking_for = self.__get_next_lookup()
                        return (self, 1)
                else:
                    logging.debug("Preamble fail; Resetting")
                    self.__looking_for = self.__PREAMBLE_PATTERN[0]
                    self.__sequence_counter = 0

        class SyncWord(StateMachine.State):
            def __init__(self, state_machine):
                self.__state_machine = state_machine
                self.__byte_counter = 0
                self.__bit_counter = 0
                self.__SYNC_WORD = self.__state_machine.SYNC_WORD

            def get_bit(self):
                byte = self.__SYNC_WORD[self.__byte_counter]
                return ((byte >> self.__bit_counter) & 0x01)

            def run(self, input_data):
                bit = get_bit()

                if input_data == \
                        self.__HEADER_PATTERN[self.__sequence_counter]:
                    self.__sequence_counter = \
                            self.__sequence_counter + 1

                    if self.__sequence_counter == \
                            len(self.__HEADER_PATTERN):
                        logging.debug("Header found")
                        return (PacketDecoder.DataSize(
                            self.__state_machine), 1)
                    else:
                        return (self, 1)
                else:
                    logging.debug("Header not found")
                    return (PacketDecoder.Preamble(
                        self.__state_machine), 0)

        class Header(StateMachine.State):
            def __init__(self, state_machine):
                self.__state_machine = state_machine
                self.__sequence_counter = 0
                self.__HEADER_PATTERN = \
                        self.__state_machine.header_pattern

            def run(self, input_data):
                if input_data == \
                        self.__HEADER_PATTERN[self.__sequence_counter]:
                    self.__sequence_counter = \
                            self.__sequence_counter + 1

                    if self.__sequence_counter == \
                            len(self.__HEADER_PATTERN):
                        logging.debug("Header found")
                        return (PacketDecoder.DataSize(
                            self.__state_machine), 1)
                    else:
                        return (self, 1)
                else:
                    logging.debug("Header not found")
                    return (PacketDecoder.Preamble(
                        self.__state_machine), 0)

        class DataSize(StateMachine.State):
            def __init__(self, state_machine):
                self.__state_machine = state_machine

            def run(self, input_data):
                self.__state_machine.data_size = input_data
                logging.debug("Data size read: {}".
                        format(self.__state_machine.data_size))
                return (PacketDecoder.Data(self.__state_machine), 1)

        class Data(StateMachine.State):
            def __init__(self, state_machine):
                self.__state_machine = state_machine
                self.__data_size = self.__state_machine.data_size
                self.__sequence_counter = 0

            def run(self, input_data):
                self.__state_machine.data.append(input_data)
                self.__sequence_counter = self.__sequence_counter + 1

                if self.__sequence_counter == self.__data_size:
                    logging.debug("Data read")
                    return (PacketDecoder.Crc(self.__state_machine), 1)
                else:
                    return (self, 1)

        class Crc(StateMachine.State):
            def __init__(self, state_machine):
                self.__state_machine = state_machine
                self.__crc_length = self.__state_machine.crc_length
                self.__sequence_counter = 0

            def run(self, input_data):
                self.__state_machine.crc.append(input_data)
                self.__sequence_counter = self.__sequence_counter + 1

                if self.__sequence_counter == self.__crc_length:
                    logging.debug("CRC read")
                    self.__state_machine.packet_received()
                    return (PacketDecoder.Preamble(
                        self.__state_machine), 1)
                else:
                    return (self, 1)

        def __init__(self, preamble_pattern, sync_word, header):
            self.PREAMBLE_PATTERN = preamble_pattern
            self.SYNC_WORD = sync_word
            self.HEADER = header

            self.reset()

        def reset(self):
            self.data_size = 0
            self.data = array.array('B')
            self.crc = array.array('B')

            self.current_state = PacketDecoder.Preamble(self)

        def run(self, input_data):
            i = 0

            logging.debug("Run with {} data".format(len(input_data)))

            while i < len(input_data):
                next_state, increment = self.current_state.run(
                        input_data[i])

                self.current_state = next_state
                i = i + increment

        def packet_received(self):
            logging.debug("Packet received (CRC skip)")
            print("'" + self.data.tobytes().decode("utf-8") + "'")
            del self.data[:]
            del self.crc[:]

    def __init__(self,
            preamble_pattern, sync_word, header, output_filename):
        gr.sync_block.__init__(self,
            name="si4432_simple_decoder",
            in_sig=[numpy.uint8],
            out_sig=None)

        self.__packet_decoder = PacketDecoder(
                preamble_pattern, sync_word, header)

        self.output_filename = output_filename

    def work(self, input_items, output_items):
        in0 = input_items[0]

        self.__packet_decoder.run(in0)

        return len(input_items[0])

