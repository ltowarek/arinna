#!/usr/bin/env python3


class FakeSerial:
    def __init__(self):
        self._last_written_data = None
        self._response = None
        self.read_data = []

    @property
    def last_written_data(self):
        return self._last_written_data

    @property
    def response(self):
        return self._response

    @response.setter
    def response(self, value):
        self._response = bytearray(value)

    def write(self, data):
        self._last_written_data = data

    def read(self):
        while self._response:
            yield bytes([self._response.pop(0)])

    def read_until(self, expected):
        output = b''
        for b in self.read():
            if b == expected:
                break
            output += b
        return output
