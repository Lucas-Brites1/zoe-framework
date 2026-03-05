from zoe_di.box import Box
from zoe_di.lifecycle import SINGLETON
from zoe_di.singleton import Singleton
from zoe_di.container import Container
#RPC
#ORM

class Database:
  def __init__(self, host: str = "127.0.0.1"):
    self.host = host

  def print_daora(self):
    print("Daora")

Container.provide_instance(obj=Database(), key="legal")
Container.resolve(key="legal").instance.print_daora() # type: ignore
