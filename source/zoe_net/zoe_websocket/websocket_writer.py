# WIP
from asyncio import StreamWriter

class WebsocketWriter:
  def __init__(self, connection_writer: StreamWriter) -> None:
    self.conn_writer = connection_writer

  async def write(self, frame: 'WebsocketFrame') -> None:
    self.conn_writer.write(frame.bytes)
    await self.conn_writer.drain()

