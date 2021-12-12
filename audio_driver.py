
from random import randint, random
import numpy as np
import time

from pythonosc import udp_client

from threading import Thread

"""
# simple sonic-pi test  
live_loop :foo do
  use_real_time
  a, b, c, d, e, f = sync "/osc*/trigger/test"
  synth :dark_ambience, note: a, attack: b, decay: c, sustain: d, release: e, cutoff: f
end
"""

class AudioDriver:

    didPop = False
    dominant_colours = None

    def __init__(self, osc_ip='127.0.0.1', osc_port=4560):
        self.sender = udp_client.SimpleUDPClient(osc_ip, osc_port)

    # update state with current data
    def update(self, popped=False, dominant_colours=None, tracked_features=None):       
        
        if popped and not self.didPop:
            self.didPop = True
            print("popped")
        elif self.didPop and not popped:
            self.didPop = False
            print("new bubble")

        if dominant_colours is not None:
            self.last_colours = self.dominant_colours
            self.dominant_colours = dominant_colours
            # print(dominant_colours)

        if tracked_features is not None:
            p = tracked_features['points']
            v = tracked_features['velocities']
            # if len(v) > 0:
                # example 
                # print(np.min(v,axis=0), np.max(v,axis=0), np.median(v, axis=0))


        # quick test triggering random notes
        if random() < 0.01:
            # test script parameters are - note,a,d,s,r,cuttoff
            self._trigger(name='test', parameters = [randint(34,72), randint(0,5), 1, 1, randint(1,5), randint(50,100)])

        
    def _trigger(self, name='test', parameters=[]):
        self.sender.send_message(f'/trigger/{name}', parameters)

    