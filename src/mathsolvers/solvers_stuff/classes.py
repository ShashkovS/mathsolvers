# steps\.append\(\s*^\s*\{\s*'action': ([\s\S]*?),\s*'solution': ([\s\S]*?),\s*'answer': ([\s\S]*?),?\s*\n +\}$\n\s*
# sol.add_step(\n  action=$1,\n  solution=$2,\n  answer=$3
import enum
import typing

SolverName = typing.Literal['simplify', 'solve', 'factor', 'units', 'format', 'compare', 'calc']


class Step(typing.TypedDict):
    action: str
    solution: str
    answer: str


@enum.unique
class CHANGE(enum.Enum):
    NoChange = enum.auto()
    Unknown = enum.auto()
    CancelRational = enum.auto()
    SubFromBothPartOfRel = enum.auto()
    CollectNumerAndDenumer = enum.auto()
    PowerSimp = enum.auto()
    CalcelMuls = enum.auto()
    SqrtDenest = enum.auto()
    ExpandMul = enum.auto()
    DoitMul = enum.auto()
    DoitAdd = enum.auto()
    DoitPow = enum.auto()
    DoitSqrt = enum.auto()
    DoitAbs = enum.auto()
    RemoveOnes = enum.auto()
    CollectNumer = enum.auto()
    DivInts = enum.auto()
    Div = enum.auto()
