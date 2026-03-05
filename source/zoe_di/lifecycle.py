from enum import Enum

class Lifecycle(Enum):
  SINGLETON = "singleton"
  TRANSIENT = "transient"
  SCOPED    = "scoped"
  PROVIDED  = "provided"


SINGLETON = Lifecycle.SINGLETON
TRANSIENT = Lifecycle.TRANSIENT
SCOPED    = Lifecycle.SCOPED
PROVIDED  = Lifecycle.PROVIDED
