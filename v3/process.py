from message import Message
from queue import Queue
import threading
import time

threadLock = threading.Lock()


class Process(threading.Thread):
    def __init__(self, pid, root_id, neighbor_ids, q, head=None):
        threading.Thread.__init__(self)
        self.pid = pid
        self.neighbor_ids = neighbor_ids
        self.root_id = root_id
        self.q = q
        self.start_signal = False
        self.marked = False
        if int(self.pid) == int(self.root_id):
            self.marked = True
    
    def run(self):
        print(f'{self.pid}: my neighbors are {self.neighbor_ids}. {self.root_id} Marking: {self.marked}, {self.q.qsize()}')
        self._run()
        '''
        if not self.start_signal:
            threadLock.acquire()
            brd = self.q.get()
            threadLock.release()
            if brd.senderID == 'Master' and brd.receiverID == self.pid:
                print(f'{self.pid}: broadcast msg received {brd.msg_type}. Starting to run, {self.q.qsize()}')
                self.start_signal = True
                self._run()
            else:
                threadLock.acquire()
                self.q.put(brd)
                threadLock.release()
        '''
    def _run(self):
        while self.marked != True: #and self.start_signal:
            threadLock.acquire()
            tmp = self.q.get()
            threadLock.release()
            if tmp.receiverID == self.pid and tmp.msg_type=='inter-thread':
                print(f'{self.pid} : Receiving msg {tmp.msg_type}, {self.q.qsize()}')
                self.receive_message(tmp.senderID)
            else:
                threadLock.acquire()
                self.q.put(tmp)
                threadLock.release()

        # Get lock to synchronize threads
        if self.marked and len(self.neighbor_ids) > 0:
            for i in range(len(self.neighbor_ids)):
                self.send_message(self.neighbor_ids[i])

    def set_parent(self, parent):
        self.parent = parent

    def send_message(self, receiver):
        msg = Message(self.pid, int(receiver), 'inter-thread')
        print(f'{self.pid}: sending {msg} to queue, {self.q.qsize()}')
        threadLock.acquire()
        self.q.put(msg)
        threadLock.release()
        print(f'{self.pid}: sent {msg} to queue, {self.q.qsize()}')
        
    def receive_message(self, sender):
        self.head = None
        # Mark the process
        self.marked = True
        self.set_parent(sender)
        print("{} -- Parent set to {}".format(self.pid, self.parent))


def print_time(threadName, counter):
    while counter:
        time.sleep(2)
        print("%s: %s" % (threadName, time.ctime(time.time())))
        counter -= 1