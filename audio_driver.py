
import numpy as np
import time

from pythonosc import osc_message_builder
from pythonosc import udp_client

from threading import Thread

# quick OSC test...
# sender = udp_client.SimpleUDPClient('127.0.0.1', 4560)
# sender.send_message('/trigger/test', [50, 100, 1])

class AudioDriver:

    def __init__(self, osc_ip='127.0.0.1', osc_port=4560):
        self.sender = udp_client.SimpleUDPClient(osc_ip, osc_port)

    # update state with current data
    def update(self, popped, dominant_colours, tracked_features):       
        print("AudioDriver update")
        # todo 
        # tracked_features -- min/max/average velocity/direction
        # dominant_colours -- hsv representation
        
    def _trigger(self, name='text', parameters=[]):
        self.sender.send_message(f'/trigger/{name}', parameters)

        

