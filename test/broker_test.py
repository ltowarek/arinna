#!/usr/bin/env python3

import time
import unittest
import paho.mqtt.client as mqtt

class BrokerTest(unittest.TestCase):
    def test_broker_is_alive(self):
        is_alive = False
        def on_message(client, userdata, message):
            nonlocal is_alive
            is_alive = True if message.payload.decode() == 'True' else False

        client = mqtt.Client()
        client.on_message = on_message
        client.connect('localhost')
        client.loop_start()
        client.subscribe('test/broker/is_alive')
        client.publish('test/broker/is_alive', 'True')
        time.sleep(1)
        client.loop_stop()
        client.disconnect()

        self.assertTrue(is_alive)


if __name__ == '__main__':
    unittest.main()

