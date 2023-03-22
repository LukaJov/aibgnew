from enum import Enum
from typing import Any, Iterable, Callable
from time import perf_counter_ns


def PPTime(time: int):
    if time < 1e3:
        return str(time) + " ns"
    if time < 1e6:
        return str(round(time/1e3, 2)) + " μs"
    if time < 1e9:
        return str(round(time/1e6, 2)) + " ms"
    return str(round(time/1e9, 2)) + " s"


class State(Enum):
    FAIL = 0
    SUCCESS = 1
    PENDING = 2


class BaseBlock:
    ID: int = 0

    def __init__(self) -> None:
        # Basic info setup
        self._id: int = BaseBlock.ID
        self._type: str = self.__class__.__name__
        self._time: int = 0
        self._state: State = State.PENDING
        BaseBlock.ID += 1

    def __call__(self) -> tuple[State, Any]:
        return (State.FAIL, None)

    def clear(self) -> None:
        self._time = 0
        self._state = State.PENDING

    def _pprint(self, depth=0):
        return "\t"*depth + "%s [X] %s %s" % (self._type, self._state, PPTime(self._time),)

    def __repr__(self):
        return self.pprint(0)


class Sequence(BaseBlock):
    def __init__(self, seq: Iterable[BaseBlock]) -> None:
        super().__init__()
        self.seq = seq

    def __call__(self) -> tuple[State, Any]:
        self._time = perf_counter_ns()
        for i in self.seq:
            ret = i()
            if ret[0] is State.SUCCESS:
                self._time = perf_counter_ns() - self._time
                self._state = State.SUCCESS

                return ret

        self._time = perf_counter_ns() - self._time
        self._state = State.FAIL
        return (State.FAIL, None)

    def clear(self) -> None:
        self._time = 0
        self._state = State.PENDING
        for i in self.seq:
            i.clear()

    def _pprint(self, depth=0):
        temp = ""
        for i in self.seq:
            temp += "\n"+"\t"*(depth+1) + "-: "+i._pprint(depth+1)
        return "%s [X] %s %s %s" % (self._type, self._state, PPTime(self._time), temp)

    def __repr__(self):
        return self._pprint(0)


class Decision(BaseBlock):
    def __init__(self,
                 condition: Callable[[], bool],
                 true: BaseBlock,
                 false: BaseBlock,
                 *args, **kwargs
                 ) -> None:
        super().__init__()
        self.condition = condition
        self.true = true
        self.false = false

        self.args = args
        self.kwargs = kwargs

    def __call__(self) -> tuple[State, Any]:
        self._time = perf_counter_ns()
        condition_ret = self.condition(*self.args, **self.kwargs)
        if condition_ret:
            temp = self.true()
            self._time = perf_counter_ns() - self._time
            self._state = temp[0]
            return temp
        else:
            temp = self.false()
            self._time = perf_counter_ns() - self._time
            self._state = temp[0]
            return temp

    def clear(self) -> None:
        self._time = 0
        self._state = State.PENDING
        self.true.clear()
        self.false.clear()

    def _pprint(self, depth=0):
        temp = ""
        temp += "\n"+"\t"*(depth+1) + "T: "+self.true._pprint(depth+1)
        temp += "\n"+"\t"*(depth+1) + "F: "+self.false._pprint(depth+1)
        return "%s [%s <- %s, %s] %s %s %s" % (self._type, self.condition.__name__, self.args, self.kwargs, self._state, PPTime(self._time), temp)

    def __repr__(self):
        return self._pprint(0)


class Action(BaseBlock):
    def __init__(self, method: Callable[[], Any], *args, **kwargs) -> None:
        super().__init__()
        self.method = method

        self.args = args
        self.kwargs = kwargs

    def __call__(self) -> tuple[State, Any]:
        self._time = perf_counter_ns()
        ret = None
        try:
            ret = self.method(*self.args, **self.kwargs)
        except:
            #catch error
            self._time = perf_counter_ns() - self._time
            self._state = State.FAIL
            return (State.FAIL, None)

        self._time = perf_counter_ns() - self._time
        if ret is None or ret is False:
            self._state = State.FAIL
            return (State.FAIL, ret)

        self._state = State.SUCCESS
        return (State.SUCCESS, ret)

    def clear(self) -> None:
        self._time = 0
        self._state = State.PENDING

    def _pprint(self, depth):
        return "%s [%s <- %s, %s] %s %s" % (self._type, self.method.__name__, self.args, self.kwargs, self._state, PPTime(self._time))

    def __repr__(self):
        return self._pprint(0)


SEQ = Sequence
ACT = Action
DEC = Decision
