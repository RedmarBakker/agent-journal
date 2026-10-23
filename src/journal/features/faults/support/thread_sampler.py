import sys
import threading
import time
from collections import Counter

from journal.features.faults.support.thread_sample import ThreadSample

SAMPLE_HZ = 100
WAITING_FUNCTIONS = frozenset({"wait", "sleep", "select", "poll", "accept", "recv", "recv_into", "readinto", "readline", "_wait_for_tstate_lock", "get", "wait_for", "acquire", "join", "read1", "serve_forever", "_handle_request_noblock"})


class ThreadSampler:
    """Looks at every thread's stack a hundred times a second for a while and counts where the journal's time goes: the function each working thread is in, by thread, and every function on a working stack with what it calls; a thread waiting on a lock, a socket or a sleep is not working."""

    def sampled(self, seconds: float) -> ThreadSample:
        busy_functions, stack_functions, sample_count = Counter(), Counter(), 0
        sampler_thread = threading.get_ident()
        end_at = time.monotonic() + seconds
        while time.monotonic() < end_at:
            thread_names = {thread.ident: thread.name for thread in threading.enumerate()}
            for ident, frame in sys._current_frames().items():
                if ident == sampler_thread or frame.f_code.co_name in WAITING_FUNCTIONS:
                    continue
                busy_functions[f"{thread_names.get(ident, ident)}: {self.place(frame)}"] += 1
                stack_functions.update({self.place(stack_frame) for stack_frame in self.stack(frame)})
            sample_count += 1
            time.sleep(1 / SAMPLE_HZ)
        return ThreadSample(busy_functions, stack_functions, sample_count)

    @staticmethod
    def place(frame) -> str:
        path = frame.f_code.co_filename
        file_name = path.split("/src/", 1)[-1] if "/src/" in path else path.rsplit("/", 1)[-1]
        return f"{frame.f_code.co_qualname} ({file_name}:{frame.f_code.co_firstlineno})"

    @staticmethod
    def stack(frame) -> list:
        frames = []
        while frame is not None:
            frames.append(frame)
            frame = frame.f_back
        return frames
