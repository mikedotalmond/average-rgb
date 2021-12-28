
from random import randint, random
import numpy as np
import time

from pythonosc import udp_client

from threading import Thread

"""
# sonic-pi test  

live_loop :osc_tick do
  use_real_time
  tick_time = sync "/osc*/trigger/tick"
  puts "osc tick"
  puts tick_time[0]
  puts get[:is_popped]
end


live_loop :popped_state do
  use_real_time
  is_popped = sync "/osc*/trigger/state/is_popped"
  set :is_popped, is_popped[0]
end

live_loop :setter do
  use_real_time
  # test setting a collection of variable values from OSC sync...
  a, b, c, d, e, f = sync "/osc*/trigger/state/test"
  set :foo, rrand(70, 130)
  set :boo, [a,b,c,d,e,f]
end

live_loop :getter do
  use_real_time
  # ... and reading them back in another liveloop thread
  sync "/osc*/trigger/state/**"
  puts "trigger"
  puts get[:foo]
  puts get[:boo]
  puts get[:is_popped]
  sleep 0.1
end
"""

class AudioDriver:

    didPop = False

    colours = None
    colours_weights = None

    points = None
    velocities = None

    # occasionally tick state
    last_tick = 0
    tick_time = 1

    def __init__(self, osc_ip='127.0.0.1', osc_port=4560):
        self.sender = udp_client.SimpleUDPClient(osc_ip, osc_port)

    #
    # update state with current data
    def update(self, popped=False, dominant_colours=None, tracked_features=None):       
        #
        ##
        if popped and not self.didPop:
            print("bubble popped")
            self.didPop = True
            self._trigger(name='state/is_popped', parameters=[1])
        elif self.didPop and not popped:
            print("new bubble")
            self.didPop = False
            self._trigger(name='state/is_popped', parameters=[0])
        #
        ##
        if dominant_colours is not None:
            # remap h,s,v - h 0->11, s,v=0-255
            c = np.array(np.rint(np.multiply(dominant_colours['colours'], [12,255,255])), dtype=np.uint8)
            w = dominant_colours['weights']

            if self.colours is not None:
                # only trigger sending update data when the remapped colour states change
                if not np.array_equal(self.colours, c):
                    for i in range(len(c)):
                        # sending colour parameters of [h,s,v,weight]
                        self._trigger(f'state/colour/{i}', parameters = np.append(c[i], w[i]))
                        self.colours[i] = c[i]
                    
                    # difference between max and min of all h,s,v values
                    variance = np.max(c,axis=0) - np.min(c,axis=0)
                    self._trigger('state/colour/variance', parameters = variance.tolist())
            else:        
                self.colours = c
            
            self.colours_weights = w
        #
        ##
        if tracked_features is not None:
            # p = tracked_features['points']
            v = tracked_features['velocities']

            # if self.points is not None:
            #     if not np.array_equal(self.points, p):
            #         if len(p) > 0:
            #             med = np.median(p,axis=0)
            #             variance = np.max(p,axis=0) - np.min(p,axis=0)
            #             self._trigger("state/position/variance", parameters = variance.tolist())
            #             self._trigger("state/position/median", parameters = med.tolist())

            if self.velocities is not None:
                if not np.array_equal(self.velocities, v):
                    if len(v) > 0:
                        self._trigger("state/velocity/min", parameters = np.min(v,axis=0).tolist())
                        self._trigger("state/velocity/max", parameters = np.max(v,axis=0).tolist())
                        self._trigger("state/velocity/median", parameters = np.median(v,axis=0).tolist())

            # self.points = p
            self.velocities = v
            
        #
        ##
        t = time.time()
        if t - self.last_tick > self.tick_time:
            self.last_tick = t
            # occasionally resend popped state so sonic-pi is updated if started/stopped out of sequence
            self._trigger(name='state/is_popped', parameters=[1 if self.didPop else 0])

        

        
    def _trigger(self, name='test', parameters=[]):
        # print("osc", name, parameters)
        self.sender.send_message(f'/{name}', parameters)
    