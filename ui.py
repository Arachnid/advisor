import Queue
import threading
import time

class UIEventGenerator(object):
    def __init__(self, poll_interval, poll_functions, sleep_func=time.sleep, time_func=time.time):
        self.poll_interval = poll_interval
        self.poll_functions = poll_functions
        self.sleep_func = sleep_func
        self.time_func = time_func

        self.q = Queue.Queue()
        self.ui_thread = threading.Thread(target=self._ui_thread)
        self.ui_thread.daemon = True
    
    def start(self):
        self._stop = False
        self.ui_thread.start()
     
    def stop(self):
        self._stop = True
        self.ui_thread.join()
    
    def __iter__(self):
        return self
    
    def next(self):
        return self.q.get()
    
    def _ui_thread(self):
        while not self._stop:
            now = self.time_func()
            for func in self.poll_functions:
                for event in func(now):
                    self.q.put(event)
            self.sleep_func(self.poll_interval)

            
class Event(object):
    def __init__(self, now):
        self.now = now


class InputEvent(Event):
    def __init__(self, now, state, args):
        super(InputEvent, self).__init__(now)
        self.state = state
        self.args = args

    def __repr__(self):
        return "InputEvent(%r, %r, %r)" % (self.now, self.state, self.args)

        
class InputEventHandler(object):
    def __init__(self, status_func, args):
        self.status_func = status_func
        self.args = args
        self.current_state = status_func()
    
    def __call__(self, now):
        state = self.status_func()
        if state != self.current_state:
            yield InputEvent(now, state, self.args)
            self.current_state = state

            
class MultiPulseEventHandler(object):
    IDLE = 1
    PULSE = 2
    WAITING = 3
    
    def __init__(self, status_func, default_state, interpulse_delay, args):
        self.status_func = status_func
        self.default_input_state = default_state
        self.interpulse_delay = interpulse_delay
        self.args = args
        
        self.last_event = None
        self.pulse_count = 0
        self.state = self.IDLE
    
    def __call__(self, now):
        state = self.status_func()
        if self.state == self.IDLE:
            if state != self.default_input_state:
                self.state = self.PULSE
                self.pulse_count = 1
                self.last_event = now
        elif self.state == self.PULSE:
            if state == self.default_input_state:
                self.state = self.WAITING
                self.last_event = now
        elif self.state == self.WAITING:
            if state != self.default_input_state:
                self.state = self.PULSE
                self.pulse_count += 1
                self.last_event = now
            elif now > self.last_event + self.interpulse_delay:
                yield InputEvent(now, self.pulse_count, self.args)
                self.state = self.IDLE
                self.last_event = now

class TimeoutEvent(Event): pass
                
class TimeoutEventHandler(object):
    def __init__(self):
        self.timeout_at = None
        
    def __call__(self, now):
        if self.timeout_at and now > self.timeout_at:
            yield TimeoutEvent(now)
            self.timeout_at = None
    
    def set_timeout(self, delay):
        self.timeout_at = time.time() + delay
