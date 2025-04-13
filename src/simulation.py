from inventory import Sale_Product_Event, Refill_Inventory_Event, Inventory_State, Inventory_Config, Apply_Time_Effects_Inventory
from heapq import heappush, heapify
from typing import List, Callable
from core import Event, State, simulation


def generate_events(index: int, time: float, time_dist: Callable[[], float], cant_dist: Callable[[], int],
                    config: Inventory_Config) -> List[Event]:
    current = 0
    events = []

    def post_action(time: float, state: State, events: List[Event]):
        if state.cants[index] < config.parameter_s:
            heappush(events, Refill_Inventory_Event(time, config.refill_interval, index, config.parameter_S -
                                         state.cants[index],
                                         config.cost_refill(config.parameter_S - state.cants[index])))

    while current < time:
        interval = time_dist()
        current += interval
        events.append(Sale_Product_Event(current, interval, index,
                                       cant_dist(), config.price, post_action))

    return events


def configure(time: float, time_dist: Callable[[], float], configs: List[Inventory_Config],
              cant_dists: List[Callable[[], int]]) -> List[Event]:
    events = []

    for i in range(len(configs)):
        events += generate_events(i, time, time_dist, cant_dists[i], configs[i])

    heapify(events)

    return events


def inventory_simulation(time: float, time_dist: Callable[[], float], configs: List[Inventory_Config],
                         cant_dists: List[Callable[[], int]], initial_cants: List[int], initial_money: float,
                         stop_case: Callable[[Inventory_State], bool] = lambda x: False):

    state = Inventory_State(initial_cants, initial_money)
    events = configure(time, time_dist, configs, cant_dists)
    action_by_time = Apply_Time_Effects_Inventory(configs)

    return simulation(events, action_by_time, state, time, stop_case)
