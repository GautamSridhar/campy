import signal
import logging

class QueueKeyboardInterrupt(object):
    '''
    Usage:
    from campy.utils.utils import HandleKeyboardInterrupt

    with QueueKeyboardInterrupt(queue):
            # stuff here will not be interrupted by SIGINT
            <critical_code()>
    '''
    def __init__(self, object):
            # Insert queue object into keyboard interrupt handler for signaling
            self.queue = object["queue"]
            self.message = object["message"]

    def __enter__(self):
            self.signal_received = False
            self.old_handler = signal.signal(signal.SIGINT, self.handler)
    
    def handler(self, sig, frame):
            self.signal_received = (sig, frame)
            logging.debug('SIGINT received. Delaying KeyboardInterrupt.')
            self.queue.append(self.message)
    
    def __exit__(self, type, value, traceback):
            pass

class HandleKeyboardInterrupt:
    '''
    Usage:
    from campy.utils.utils import HandleKeyboardInterrupt

    with HandleKeyboardInterrupt(queue):
            # stuff here will not be interrupted by SIGINT
            <critical_code()>
    '''
    def __init__(self):
            pass

    def __enter__(self):
            self.signal_received = False
            self.old_handler = signal.signal(signal.SIGINT, self.handler)

    def handler(self, sig, frame):
            self.signal_received = (sig, frame)
            logging.debug('SIGINT received. Delaying KeyboardIntterupt.')
    
    def __exit__(self, type, value, traceback):
            pass