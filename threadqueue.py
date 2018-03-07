from multiprocessing import Queue
from threading import Thread
from urllib.request import urlopen
from re import compile, MULTILINE
from time import time


class ThreadUrl(Thread):
    """Threaded website reader"""

    def __init__(self, queue, out_queue):
        Thread.__init__(self)
        self.queue = queue
        self.out_queue = out_queue

    def run(self):
        while True:
            # Grabs host from queue
            host = self.queue.get()

            # Grabs urls of hosts and then grabs chunk of webpage
            url = urlopen(host)
            chunk = url.read()
            print
            "Reading: %s" % host

            # Place chunk into out queue
            self.out_queue.put(chunk)

            # Signals to queue job is done
            self.queue.task_done()


class DatamineThread(Thread):
    """Threaded title parser"""

    def __init__(self, out_queue):
        Thread.__init__(self)
        self.out_queue = out_queue

    def run(self):
        while True:
            # Grabs chunk from queue
            chunk = self.out_queue.get()

            # Parse the chunk
            title = compile('<title>(.*)</title>', MULTILINE).findall(chunk)
            print
            title

            # Signals to queue job is done
            self.out_queue.task_done()


def main():
    # Spawn a pool of threads, and pass them queue instance
    for i in range(5):
        t = ThreadUrl(queue, out_queue)
        t.daemon = True
        t.start()

    # Populate queue with data
    for host in hosts:
        queue.put(host)

    for i in range(5):
        dt = DatamineThread(out_queue)
        dt.daemon = True
        dt.start()

    # Wait on the queue until everything has been processed
    queue.join()
    out_queue.join()


if __name__ == '__main__':
    hosts = ["http://yahoo.com", "http://google.com", "http://amazon.com",
             "http://ibm.com", "http://apple.com"]

    queue = Queue()
    out_queue = Queue()

    start = time()
    main()
    print
    "Elapsed Time: %s" % (time() - start)