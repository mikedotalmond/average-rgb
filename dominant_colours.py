import warnings
import cv2
import numpy as np
import time

from threading import Thread
from sklearn.cluster import KMeans

class DominantColours:

    clusters = None
    colours = None
    labels = None
    frame = None

    stopped = False
    draw_chart = False
    chart = None
    update_delay = 1.0
    
    def __init__(self, clusters=3, process_fps=8, debug=False, print_timings=False):
        self.clusters = clusters
        self.frame = np.zeros((8, 8, 3), np.uint8)
        self.update_delay = 1.0 / process_fps
        self.stopped = False
        self.debug = debug
        self.print_timings = print_timings
        self.chart = None

    #
    def start(self):
        Thread(target=self.process, args=()).start()
        return self
        
    #
    def stop(self):
        self.stopped = True
    
    #
    def set_frame(self, frame):
        self.frame = frame
    
    #
    def process(self):       
        
        while not self.stopped:

            t1 = time.perf_counter()

            img = self.frame
            
            # reshape to a list of pixels
            img = img.reshape((img.shape[0] * img.shape[1], 3))

            # use k-means to cluster pixels
            kmeans = KMeans(n_clusters = self.clusters)

            # ignore warnings like: ConvergenceWarning: Number of distinct clusters (1) found smaller than n_clusters (5)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                kmeans.fit(img)
            
            # the cluster centers are our dominant colors.
            self.colours = kmeans.cluster_centers_
            
            #save labels
            self.labels = kmeans.labels_

            #
            self.buildHistogram()
            
            process_time = time.perf_counter() - t1
            if self.print_timings:
                print(f'dominant colours process_time {process_time}')

            sleep_time = self.update_delay - process_time
            time.sleep(sleep_time if sleep_time > 0 else 0)


    def buildHistogram(self, width=128, height=32):
        # labels form 0 to no. of clusters
        numLabels = np.arange(0, self.clusters + 1)
       
        #create frequency count tables    
        (hist, _) = np.histogram(self.labels, bins = numLabels)
        hist = hist.astype("float")
        hist /= hist.sum()
        
        colours = self.colours
        #descending order sorting as per frequency count
        colours = colours[(-hist).argsort()]
        hist = hist[(-hist).argsort()] 
        
        self.colours = colours
        self.hist = hist

        if not self.debug:
            return

        # create empty chart
        chart = np.zeros((height, width, 3), np.uint8)
        start = 0

        # draw colour rectangles
        for i in range(self.clusters):
            end = start + hist[i] * width
            
            r = colours[i][0]
            g = colours[i][1]
            b = colours[i][2]

            cv2.rectangle(chart, (int(start), 0), (int(end), height), (r,g,b), -1)
            start = end
        
        self.chart = chart

