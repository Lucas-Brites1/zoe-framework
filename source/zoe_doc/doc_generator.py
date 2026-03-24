from typing import Any, Callable, Type, Optional, TypeVar
from zoe_doc.doc_metadata import *
from zoe_doc.dynamic_html import HTMLGen
from zoe_http._file_util import FileUtil, ROOT, Path
from zoe_exceptions.exc_internal_exc import InternalServerException, ZoeNonHttpError

T = TypeVar('T')

class DocGenerator:
  _TEMPLATE_PATH: Path = Path(FileUtil.mount_path("/source", "/zoe_doc", "/zoe_doc_files") / "static_page.html")
  _OUTPUT_PATH:   Path = Path(FileUtil.mount_path("/source", "/zoe_doc", "/zoe_doc_files") / "generated_docs.html")

  @staticmethod
  def __get_html_template() -> str:
    b_html: bytes | None = FileUtil.read(path=DocGenerator._TEMPLATE_PATH)

    if b_html is None:
       raise InternalServerException.from_unexpected_error(
          RuntimeError("Error while trying to read html template to generate docs.")
       )

    return b_html.decode(encoding="utf-8", errors="replace")


  @staticmethod
  def __build_sidebar(routes: list[RouteInfo], route_ids: dict[str, int]) -> str:
    groups: dict[str, list[RouteInfo]] = {}

    for route_info in routes:
        route_prefix: str = route_info["prefix"]
        if route_prefix not in groups:
            groups[route_prefix] = []
        groups[route_prefix].append(route_info)

    sidebar_html = ""
    for prefix, group_routes in groups.items():
        group_id     = prefix.replace("/", "_").strip("_")
        routes_html  = "".join(
            HTMLGen.sidebar_route(info, route_ids[info["path"]])
            for info in group_routes
        )
        sidebar_html += HTMLGen.sidebar_group(prefix, group_id, routes_html)

    return sidebar_html

  @staticmethod
  def generate(routes: list[RouteInfo]) -> None:
      html = DocGenerator.__get_html_template()
      route_ids = {info.get("path"): i for i, info in enumerate(routes)}

      panels_html  = "".join(HTMLGen.full_panel(info, i) for i, info in enumerate(routes))
      sidebar_html = DocGenerator.__build_sidebar(routes, route_ids=route_ids)

      html = HTMLGen.find_tag_and_insert(html, "ZOE_PANELS",  panels_html)
      html = HTMLGen.find_tag_and_insert(html, "ZOE_SIDEBAR", sidebar_html)

      FileUtil.write(DocGenerator._OUTPUT_PATH, html.encode())

def doc(
  summary:    Summary      | None = None,
  author:     Author       | None = None,
  request:    RouteRequest | None = None,
  responses:   list[RouteResponse] | None = None,
  security:   RouteSecurity | None = None,
  logic:      BusinessLogic | None = None,
  depends_on: list[DependsOn] | None = None,
  version:    str | None = None,
  deprecated: bool = False
) -> Callable:
  def wrapped(handler: type[T]) -> type[T]:
      meta: DocMetadata = {}
      if summary    is not None: meta["summary"]    = summary
      if author     is not None: meta["author"]     = author
      if request    is not None: meta["request"]    = request
      if responses   is not None: meta["responses"]  = responses
      if security   is not None: meta["security"]   = security
      if logic      is not None: meta["logic"]      = logic
      if depends_on is not None: meta["depends_on"] = depends_on
      if version    is not None: meta["version"]    = version
      if deprecated:             meta["deprecated"] = deprecated
      handler.__zoe_doc__ = meta
      print(handler)
      return handler
  return wrapped
