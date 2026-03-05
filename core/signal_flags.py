import threading
from contextlib import contextmanager

_local = threading.local()

def is_team_signal_suppressed() -> bool:
    return getattr(_local, "suppress_team_signal", False)

@contextmanager
def suppress_team_signals():
    prev = getattr(_local, "suppress_team_signal", False)
    _local.suppress_team_signal = True
    try:
        yield
    finally:
        _local.suppress_team_signal = prev