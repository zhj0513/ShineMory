from threading import Timer, Thread
from time import sleep


class Scheduler(object):
    def __init__(self, sleep_time, function):
        self.sleep_time = sleep_time
        self.function = function
        self._t = None

    def start(self):  # 用于启动循环任务
        if self._t is None:
            self._t = Timer(self.sleep_time, self._run)
            self._t.start()
        else:
            raise Exception("this timer is already running")

    def _run(self):
        self.function()
        self._t = Timer(self.sleep_time, self._run)
        self._t.start()

    def stop(self):  # 用于停止循环任务
        if self._t is not None:
            self._t.cancel()
            self._t = None


def query_db():
    print("IM QUERYING A DB")


if __name__ == "__main__":
    scheduler = Scheduler(5, query_db)
    scheduler.start()
    # scheduler.stop()
