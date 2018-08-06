#!/usr/bin/env python3

import arinna.inverter_provider as ip


def test_is_valid_response_returns_false_given_ack_is_passed():
    assert ip.is_valid_response(b'(ACK9 \r') is False


def test_is_valid_response_returns_false_given_nak_is_passed():
    assert ip.is_valid_response(b'(NAKss\r') is False


def test_is_valid_response_returns_true_given_valid_response_is_passed():
    assert ip.is_valid_response(b'(NAKss\r') is False
