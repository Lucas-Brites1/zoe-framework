from zoe_doc.doc_generator import DocGenerator
from zoe_http._file_util import FileUtil
from zoe_http.request import Request
from zoe_http.response import Response
from zoe_router.route import Route
from zoe_http.handler import Handler

class DocExpose(Handler):
  @staticmethod
  def get_handler() -> Route:
    return Route.get(endpoint="/docs", handler=DocExpose())


  def handle(self, req: Request) -> Response:
    html : bytes | None = FileUtil.read(DocGenerator._OUTPUT_PATH)
    if html is None:
      raise ValueError

    html_str: str = html.decode(encoding="utf-8")
    return Response.html(body=html_str)
