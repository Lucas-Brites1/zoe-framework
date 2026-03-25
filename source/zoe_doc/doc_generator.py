from typing import Any, Callable, Type, Optional, TypeVar
from zoe_doc.doc_metadata import *
from zoe_doc.dynamic_html import HTMLGen
from zoe_http._file_util import FileUtil, ROOT, Path
from zoe_exceptions.exc_internal_exc import InternalServerException, ZoeNonHttpError
import base64

T = TypeVar('T')

class DocGenerator:
  _TEMPLATE_PATH: Path = Path(FileUtil.mount_path("source", "zoe_doc", "zoe_doc_files") / "static_page.html")
  _OUTPUT_PATH:   Path = Path(FileUtil.mount_path("source", "zoe_doc", "zoe_doc_files") / "generated_docs.html")

  @staticmethod
  def __get_html_template() -> str:
    b_html: bytes | None = FileUtil.read(path=DocGenerator._TEMPLATE_PATH)
    if b_html is None:
      raise InternalServerException.from_unexpected_error(
        RuntimeError("Error while trying to read html template to generate docs.")
      )
    return b_html.decode(encoding="utf-8", errors="replace")

  @staticmethod
  def __build_sidebar(routes: list[RouteInfo], route_ids: dict[tuple, int]) -> str:
    groups: dict[str, list[RouteInfo]] = {}

    for route_info in routes:
      prefix = route_info["prefix"]
      if prefix not in groups:
        groups[prefix] = []
      groups[prefix].append(route_info)

    sidebar_html  = ""
    first_overall = True

    for prefix, group_routes in groups.items():
      group_id = prefix.replace("/", "_").strip("_") or "root"
      route_elements = []

      for info in group_routes:
        # chave inclui prefix — rotas com mesmo path em routers diferentes ficam distintas
        key    = (info["method"], info["prefix"], info["path"])
        rid    = route_ids[key]
        active = first_overall
        first_overall = False
        route_elements.append(HTMLGen.sidebar_route(info, rid, active=active))

      sidebar_html += HTMLGen.sidebar_group(prefix, group_id, *route_elements).make

    return sidebar_html

  @staticmethod
  def __insert_icon() -> str:
    html = DocGenerator.__get_html_template()
    icon_path  = FileUtil.mount_path("source", "zoe_doc", "zoe_doc_files") / "zoe_icon.png"
    icon_bytes = FileUtil.read(icon_path)
    icon_b64   = f"data:image/png;base64,{base64.b64encode(icon_bytes).decode()}" if icon_bytes else ""
    return HTMLGen.find_tag_and_insert(html, "ZOE_ICON", icon_b64)

  @staticmethod
  def generate(routes: list[RouteInfo]) -> None:
    if not routes:
      return

    html: str = DocGenerator.__insert_icon()

    # (method, prefix, path) — único por rota mesmo com paths iguais em routers diferentes
    route_ids: dict[tuple, int] = {
      (info["method"], info["prefix"], info["path"]): i
      for i, info in enumerate(routes)
    }

    panels_html  = "".join(
      HTMLGen.full_panel(info, i, active=(i == 0))
      for i, info in enumerate(routes)
    )
    sidebar_html = DocGenerator.__build_sidebar(routes, route_ids)

    html = HTMLGen.find_tag_and_insert(html, "ZOE_PANELS",  panels_html)
    html = HTMLGen.find_tag_and_insert(html, "ZOE_SIDEBAR", sidebar_html)

    FileUtil.write(DocGenerator._OUTPUT_PATH, html.encode())


def doc(
  summary:    Summary             | None = None,
  author:     Author              | None = None,
  request:    RouteRequest        | None = None,
  responses:  list[RouteResponse] | None = None,
  security:   RouteSecurity       | None = None,
  logic:      BusinessLogic       | None = None,
  depends_on: list[DependsOn]     | None = None,
  version:    str                 | None = None,
  deprecated: bool = False
) -> Callable:
  def wrapped(handler: type[T]) -> type[T]:
    meta: DocMetadata = {}
    if summary    is not None: meta["summary"]    = summary
    if author     is not None: meta["author"]     = author
    if request    is not None: meta["request"]    = request
    if responses  is not None: meta["responses"]  = responses
    if security   is not None: meta["security"]   = security
    if logic      is not None: meta["logic"]      = logic
    if depends_on is not None: meta["depends_on"] = depends_on
    if version    is not None: meta["version"]    = version
    if deprecated:             meta["deprecated"] = deprecated
    handler.__zoe_doc__ = meta  # type: ignore
    return handler
  return wrapped
