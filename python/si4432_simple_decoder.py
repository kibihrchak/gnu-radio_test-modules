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
import pmt

logging.basicConfig(level=logging.DEBUG)


class StateMachine:
    class State:
        def __init__(self, state_machine):
            self._state_machine = state_machine

        def process(self, input_data):
            pass

    class BitPackerState(State):
        def __init__(self, state_machine):
            StateMachine.State.__init__(self, state_machine)
            self.reset()

        def _reset_buffer(self):
            self._byte_placeholder = 0
            self._bit_counter = 0

        def reset(self):
            self._reset_buffer()

        def _process_byte(self, item):
            pass

        def process(self, input_data):
            total_processed = 0

            while total_processed < len(input_data):
                self._byte_placeholder = \
                        (self._byte_placeholder << 1) | \
                        input_data[total_processed]
                self._bit_counter = self._bit_counter + 1
                total_processed = total_processed + 1

                if self._bit_counter == 8:
                    data_is_read = self._process_byte(
                            self._byte_placeholder)
                    self._reset_buffer()

                    if data_is_read == True:
                        break

            return total_processed

    class ReadBytesState(BitPackerState):
        def __init__(self, state_machine, message, next_state):
            StateMachine.BitPackerState.__init__(self, state_machine)
            self._message = message
            self._next_state = next_state

            self.reset()

        def reset(self):
            StateMachine.BitPackerState.reset(self)
            self._data = array.array('B')

        def get_data(self):
            return self._data

        def set_data_size(self, data_size):
            self._data_size = data_size

        def _data_read_user_action(self):
            pass

        def _process_byte(self, item):
            self._data.append(item)

            data_is_read = len(self._data) == self._data_size

            if data_is_read:
                logging.debug(self._message)
                self._data_read_user_action()
                self._state_machine.next_state(self._next_state)

            return data_is_read

class PacketDecoder(StateMachine):
    class States:
        class Preamble(StateMachine.State):
            _PREAMBLE_PATTERN = array.array('B', [0x00, 0x01])
            _PREAMBLE_UNIT_LENGTH = 4

            def _get_current_lookup(self):
                pds = PacketDecoder.States

                return pds.Preamble._PREAMBLE_PATTERN[
                        self._sequence_counter %
                        len(pds.Preamble._PREAMBLE_PATTERN)]

            def __init__(self, state_machine):
                StateMachine.State.__init__(self, state_machine)
                self.reset()

            def reset(self):
                self._sequence_counter = 0
                self._looking_for = self._get_current_lookup()

            def set_sequence_length(self, sequence_length):
                self._SEQUENCE_LENGTH = sequence_length

            def process(self, input_data):
                pds = PacketDecoder.States
                
                total_processed = 0

                while total_processed < len(input_data):
                    item = input_data[total_processed]
                    total_processed = total_processed + 1

                    if item == self._looking_for:
                        if self._sequence_counter == \
                                self._SEQUENCE_LENGTH * \
                                self._PREAMBLE_UNIT_LENGTH:
                            logging.debug("Preamble found")
                            self._state_machine.next_state(pds.SyncWord)
                            break
                        else:
                            self._sequence_counter = \
                                    self._sequence_counter + 1
                            self._looking_for = \
                                    self._get_current_lookup()
                    elif self._sequence_counter > 0:
                        self.reset()

                return total_processed

        class SyncWord(StateMachine.State):
            def __init__(self, state_machine):
                StateMachine.State.__init__(self, state_machine)
                self.reset()

            def reset(self):
                self._shift_register = 0

            def set_sync_word(self, sync_word):
                tmp_pattern = 0x00
                tmp_mask = 0x00

                for i in range(len(sync_word)):
                    tmp_pattern = (tmp_pattern << 8) | sync_word[i]
                    tmp_mask = (tmp_mask << 8) | 0xff

                self._shift_register_mask = tmp_mask
                self._sync_word = tmp_pattern

            def process(self, input_data):
                pds = PacketDecoder.States

                total_processed = 0

                while total_processed < len(input_data):
                    item = input_data[total_processed]
                    total_processed = total_processed + 1

                    self._shift_register = \
                            ((self._shift_register << 1) | item) & \
                            self._shift_register_mask

                    if self._shift_register == self._sync_word:
                        logging.debug("Sync word found")
                        self._state_machine.next_state(pds.Header)
                        break

                return total_processed

        class Header(StateMachine.ReadBytesState):
            def __init__(self, state_machine, message, next_state):
                StateMachine.ReadBytesState.__init__(
                        self, state_machine, message, next_state)

        class DataSize(StateMachine.ReadBytesState):
            def __init__(self, state_machine, message, next_state):
                StateMachine.ReadBytesState.__init__(
                        self, state_machine, message, next_state)

            def _data_read_user_action(self):
                logging.debug("Data size: {}".format(self._data[0]))


        class Data(StateMachine.ReadBytesState):
            def __init__(self, state_machine, message, next_state):
                StateMachine.ReadBytesState.__init__(
                        self, state_machine, message, next_state)

        class Crc(StateMachine.ReadBytesState):
            def __init__(self, state_machine, message, next_state):
                StateMachine.ReadBytesState.__init__(
                        self, state_machine, message, next_state)

            def _data_read_user_action(self):
                self._state_machine.packet_received()

    def __init__(
            self,
            preamble_len_units, sync_word, header_len,
            decoder):
        pds = PacketDecoder.States

        self._states = {
                pds.Preamble: pds.Preamble(self),
                pds.SyncWord: pds.SyncWord(self),
                pds.Header: pds.Header(
                    self, "Header read", pds.DataSize),
                pds.DataSize: pds.DataSize(
                    self, "Data size read", pds.Data),
                pds.Data: pds.Data(
                    self, "Data read", pds.Crc),
                pds.Crc: pds.Crc(
                    self, "CRC read", pds.Preamble)}

        self._states[pds.Preamble].set_sequence_length(
                preamble_len_units)
        self._states[pds.SyncWord].set_sync_word(sync_word)
        self._states[pds.Header].set_data_size(header_len)
        self._states[pds.DataSize].set_data_size(1)
        self._states[pds.Crc].set_data_size(2)

        self._decoder = decoder

        self.reset()

    def next_state(self, next_state):
        pds = PacketDecoder.States

        self._current_state = self._states[next_state]
        self._current_state.reset()

        if next_state == pds.Data:
            self._current_state.set_data_size(
                    self._states[pds.DataSize].get_data()[0])

    def reset(self):
        pds = PacketDecoder.States

        self.next_state(pds.Preamble)

    def process(self, input_data):
        total_processed = 0

        #logging.debug("Run with {} data".format(len(input_data)))

        while total_processed < len(input_data):
            iter_processed = self._current_state.process(
                    input_data[total_processed:])

            total_processed = total_processed + iter_processed

    def packet_received(self):
        pds = PacketDecoder.States

        packet = {
                "header": self._states[pds.Header].get_data(),
                "data": self._states[pds.Data].get_data(),
                "crc": self._states[pds.Crc].get_data()}

        self._decoder.packet_received(packet)

class si4432_simple_decoder(gr.sync_block):
    """
    docstring for block si4432_simple_decoder
    """

    def __init__(
            self,
            preamble_len_units, sync_word, header_len,
            output_filename):
        gr.sync_block.__init__(self,
            name="si4432_simple_decoder",
            in_sig=[numpy.uint8],
            out_sig=None)

        self.message_port_register_out(pmt.intern('out'))

        self.__packet_decoder = PacketDecoder(
                preamble_len_units, sync_word, header_len,
                self)
        self.__output_filename = output_filename

    def packet_received(self, packet):
        logging.debug("Packet received")
        logging.debug("Header: {}".format(packet["header"]))
        logging.debug("Data: {}".format(packet["data"]))
        logging.debug("Data (string): '{}'".format(
            ''.join(chr(c) for c in packet["data"])))
        logging.debug("CRC: {}".format(packet["crc"]))


        send_pmt = pmt.make_u8vector(len(packet["data"]), ord(' '))

        for i in range(len(packet["data"])):
            pmt.u8vector_set(send_pmt, i, packet["data"][i])

        self.message_port_pub(pmt.intern('out'),
                pmt.cons(pmt.PMT_NIL, send_pmt))

    def work(self, input_items, output_items):
        in0 = input_items[0]

        self.__packet_decoder.process(in0)

        return len(input_items[0])

