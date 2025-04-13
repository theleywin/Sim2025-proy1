from abc import ABC
from typing import List, Callable
from heapq import heappop

class State(ABC):
    pass

class Event(ABC):
    def __init__(self, time: float, interval: float) -> None:
        self.time: float = time
        self.interval: float = interval

    def __lt__(self, other):
        return self.time < other.time

    def __gt__(self, other):
        return self.time > other.time

    def __eq__(self, other):
        return self.time == other.time

    def action(self, state: State, events: List['Event']):
        pass
    
class Apply_Time_Effects(ABC):
    def action(self, interval: float, state: State):
        pass
    
    
def simulation(events: List[Event], apply_time_effects: Apply_Time_Effects, state: State, max_time: float, stop_case: Callable[[State], bool]) -> (List[Event], State):
   
    history = []
    last_time = 0
    interrupted = False

    while events:
        event = heappop(events)

        if event.time > max_time:
            break

        last_time = event.time
        history.append(event)

        apply_time_effects.action(event.time - last_time, state)
        
        if stop_case(state):
            interrupted = True
            break

        event.action(state, events)
        if stop_case(state):
            interrupted = True
            break

    if not interrupted:
        apply_time_effects.action(max_time - last_time, state)

    return history, state