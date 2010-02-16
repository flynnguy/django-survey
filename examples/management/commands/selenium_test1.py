from django.core.management.commands import runserver
import sys
import time
import thread
import threading

class ThreadSafeWriter(file):
    def __init__(self, *args, **kwdargs):
        self.lock = thread.allocate()
        return super(ThreadSafeWriter, self).__init__(*args, **kwdargs)
    def write(self, *args, **kwdargs):
        self.lock.acquire()
        res = super(ThreadSafeWriter, self).write(*args, **kwdargs)
        super(ThreadSafeWriter, self).flush()
        self.lock.release()
        return res
    def writeline(self, *args, **kwdargs):
        self.lock.acquire()
        res = super(ThreadSafeWriter, self).writeline(*args, **kwdargs)
        super(ThreadSafeWriter, self).flush()
        self.lock.release()
        return res
    def writelines(self, *args, **kwdargs):
        self.lock.acquire()
        res = super(ThreadSafeWriter, self).writelines(*args, **kwdargs)
        super(ThreadSafeWriter, self).flush()
        self.lock.release()
        return res

class Command(runserver.Command):
    def handle(self, addrport='', *args, **options):
        ## make stdout and error be thread safe and to files.
        #sys.stdout = ThreadSafeWriter('events.log', 'a')
        #sys.stderr = ThreadSafeWriter('errors.log', 'a')

        real_handle = super(Command, self).handle
        ## startup selenium

        ## start server in a seprate thread
        server = threading.Thread(target=real_handle, name='server',
                                  args=args, kwargs=options)
        server.setDaemon(False)
        server.start()

        ## run test
        time.sleep(20)

        ## stop server
        del server
