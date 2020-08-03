import multiprocessing
import os
import signal
import threading


#
# ProcessTaskBase =====================================================================
#
class ProcessTaskBase(object):  # TODO: put this class to swss-platform-common
    def __init__(self):
        self.task_process = None
        self.task_stopping_event = multiprocessing.Event()

    def task_worker(self):
        pass

    def task_run(self):
        if self.task_stopping_event.is_set():
            return

        self.task_process = multiprocessing.Process(target=self.task_worker)
        self.task_process.start()

    def task_stop(self):
        self.task_stopping_event.set()
        os.kill(self.task_process.pid, signal.SIGKILL)


#
# ThreadTaskBase =====================================================================
#
class ThreadTaskBase(object):  # TODO: put this class to swss-platform-common;
    def __init__(self):
        self.task_thread = None
        self.task_stopping_event = threading.Event()

    def task_worker(self):
        pass

    def task_run(self):
        if self.task_stopping_event.is_set():
            return

        self.task_thread = threading.Thread(target=self.task_worker)
        self.task_thread.start()

    def task_stop(self):
        self.task_stopping_event.set()
        self.task_thread.join()
