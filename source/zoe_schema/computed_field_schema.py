from typing import Any, Callable

class _ComputedField:
  def __init__(self, lambda_: Callable[[dict], Any]) -> None:
    self._lambda = lambda_

def ComputedField(lambda_: Callable[[dict], Any]) -> Any:
  return _ComputedField(lambda_)
