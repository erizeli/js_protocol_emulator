"""Independent cycle-indexed reference for sampled transitions."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Event:
    delta_time: int
    pin_mask: int
    pin_value: int


def capture_events(initial_value, samples):
    """samples[0] is the first sample one cycle after capture start."""
    previous = initial_value
    last_transition = 0
    events = []
    for cycle, value in enumerate(samples, start=1):
        if value != previous:
            events.append(Event(cycle - last_transition, previous ^ value, value))
            previous = value
            last_transition = cycle
    return events
