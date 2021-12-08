import warnings
import cv2
import numpy as np
import time

from threading import Thread
from sklearn.cluster import KMeans

class DominantColours:

    CLUSTERS = None
    COLORS = None
    LABELS = None
    FRAME = None
    
    def __init__(self, clusters=3, process_fps=8, draw_chart=False):
        self.CLUSTERS = clusters
        self.FRAME = np.zeros((8, 8, 3), np.uint8)
        self.update_delay = 1.0 / process_fps
        self.stopped = False
        self.draw_chart = draw_chart
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
        self.FRAME = frame
    
    #
    def process(self):       
        
        while not self.stopped:

            t1 = time.perf_counter()

            img = self.FRAME
            
            # convert to rgb from bgr
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # reshape to a list of pixels
            img = img.reshape((img.shape[0] * img.shape[1], 3))

            # use k-means to cluster pixels
            kmeans = KMeans(n_clusters = self.CLUSTERS)

            # ignore warnings like: ConvergenceWarning: Number of distinct clusters (1) found smaller than n_clusters (5)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                kmeans.fit(img)
            
            # the cluster centers are our dominant colors.
            self.COLORS = kmeans.cluster_centers_
            
            #save labels
            self.LABELS = kmeans.labels_

            #
            self.buildHistogram()
            
            process_time = time.perf_counter() - t1
            sleep_time = self.update_delay - process_time

            # print(f'dominant colours process_time {process_time}')
            time.sleep(sleep_time if sleep_time > 0 else 0)


    def buildHistogram(self, width=480, height=27):
        # labels form 0 to no. of clusters
        numLabels = np.arange(0, self.CLUSTERS + 1)
       
        #create frequency count tables    
        (hist, _) = np.histogram(self.LABELS, bins = numLabels)
        hist = hist.astype("float")
        hist /= hist.sum()
        
        #appending frequencies to cluster centers
        colors = self.COLORS
        # print(colors)
        
        #descending order sorting as per frequency count
        colors = colors[(-hist).argsort()]
        hist = hist[(-hist).argsort()] 

        if not self.draw_chart:
            return

        # create empty chart
        chart = np.zeros((height, width, 3), np.uint8)
        start = 0

        # draw colour rectangles
        for i in range(self.CLUSTERS):
            end = start + hist[i] * width
            
            r = colors[i][0]
            g = colors[i][1]
            b = colors[i][2]

            # print(r,g,b)

            cv2.rectangle(chart, (int(start), 0), (int(end), height), (r,g,b), -1)
            start = end
        
        self.chart = chart

