
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
            # TODO: record last bubble lifetime here
            self.didPop = True
            self._trigger('state/is_popped', [1])
        elif self.didPop and not popped:
            print("new bubble")
            self.didPop = False
            self._trigger('state/is_popped', [0])
        #
        ##
        if dominant_colours is not None:
            # remap h,s,v - h 0->11, s,v=0-255
            c = dominant_colours['colours'] 
            w = dominant_colours['weights']

            if self.colours is not None:
                colour_change_precision = [12, 64, 64] #h/s/v
                # only trigger sending update data when the rounded (reduced precision) colour states change
                if not self._arrays_equal_with_precision(self.colours, c, colour_change_precision):
                    colours = []
                    for i in range(len(c)):
                        # sending colour parameters of [h,s,v,weight]
                        colours = colours + np.append(c[i], w[i]).tolist()
                        self.colours[i] = c[i]
                    
                    # variance - difference between max and min of all h,s,v values
                    c_min = np.min(c, axis=0)
                    c_max = np.max(c, axis=0)
                    variance = c_max - c_min

                    # since hue is cyclic the min/max needs to take that into account and wrap around
                    if variance[0] > 0.5:
                        v2 = (c_min[0] + 1.0) - c_max[0]
                        if v2 < variance[0]:
                            variance[0] = v2
                    
                    self._trigger('state/colours', colours + variance.tolist())
            
            else:
                self.colours = c
            
            self.colours_weights = w
        #
        ##
        if tracked_features is not None:
            v = tracked_features['velocities']
            if self.velocities is not None:
                velocity_change_precision = [64, 64]
                if not self._arrays_equal_with_precision(self.velocities, v, velocity_change_precision):
                    if len(v) > 0:
                        # send both max and average x,y velocity lists, concatenated into a single list of [x,y,x,y]
                        self._trigger("state/velocity", np.max(v,axis=0).tolist() + np.average(v,axis=0).tolist())
                    self.velocities = v
            else:
                self.velocities = v
            
        #
        ##
        t = time.time()
        if t - self.last_tick > self.tick_time:
            self.last_tick = t
            # occasionally resend popped state so sonic-pi is updated if started/stopped out of sequence
            self._trigger('state/is_popped', [1 if self.didPop else 0])

        

    #
    def _trigger(self, name="test", args=[]):
        self.sender.send_message(f'/{name}', args)
    
    #
    def _arrays_equal_with_precision(self, a, b, precisions):
        if len(a) != len(b): return False
        if len(a) == 0 and len(b) == 0: return True
        aa = np.array(np.rint(np.multiply(a, precisions)), dtype=np.uint8)
        bb = np.array(np.rint(np.multiply(b, precisions)), dtype=np.uint8)
        return np.array_equal(aa, bb)
