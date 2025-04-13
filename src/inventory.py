from typing import List, Callable
from core import Event, State, Apply_Time_Effects


class Inventory_State(State):
    def __init__(self, initial_cants: List[int], initial_money: float) -> None:
        self.cants: List[int] = initial_cants
        self.money: float = initial_money
        self.money_history: List[float] = [initial_money]

    def add_cant(self, index: int, cant: int):
        self.cants[index] += cant

    def remove_cant(self, index: int, cant: int):
        self.cants[index] -= cant

    def add_money(self, money: float):
        self.money += money
        self.money_history.append(self.money)

    def remove_money(self, money: float):
        self.money -= money
        self.money_history.append(self.money)


class Refill_Inventory_Event(Event):
    def __init__(self, current_time: float, interval: float, index: int, cant: int, cost: int) -> None:
        super().__init__(current_time + interval, interval)
        self.index: int = index
        self.cant: int = cant
        self.cost: float = cost

    def action(self, state: State, _: List[Event]):
        state.add_cant(self.index, self.cant)
        state.remove_money(self.cost)


class Sale_Product_Event(Event):
    def __init__(self, current_time: float, interval: float, index: int, cant: int, price: float,
                 post_action: Callable[[float, Inventory_State, List[Event]], None]) -> None:
        super().__init__(interval + current_time, interval)
        self.index: int = index
        self.cant: int = cant
        self.price: float = price
        self.post_action: Callable[[Inventory_State, Event]] = post_action

    def action(self, state: Inventory_State, events: List[Event]):
        if state.cants[self.index] >= self.cant:
            state.remove_cant(self.index, self.cant)
            state.add_money(self.price * self.cant)
        else:
            state.add_money(self.price * state.cants[self.index])
            state.remove_cant(self.index, state.cants[self.index])

        self.post_action(self.time, state, events)


class Inventory_Config:
    def __init__(self, price: float, parameter_s: int, parameter_S: int, refill_interval: float,
                 cost_refill: Callable[[int], float], cost_inventory: Callable[[int, float], float]) -> None:
        self.parameter_s: int = parameter_s
        self.parameter_S: int = parameter_S
        self.price = price
        self.refill_interval: float = refill_interval
        self.cost_refill: Callable[[int], float] = cost_refill
        self.cost_inventory: Callable[[int, float], float] = cost_inventory


class Apply_Time_Effects_Inventory(Apply_Time_Effects):
    def __init__(self, configs: List[Inventory_Config]) -> None:
        self.configs: List[Inventory_Config] = configs

    def action(self, interval: float, state: Inventory_State):
        for config in self.configs:
            state.remove_money(config.cost_inventory(state.cants[self.configs.index(config)], interval))
