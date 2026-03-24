from zoe_doc.doc_metadata import *
from zoe_di.inspector import ModelInspector
from typing import Type
import json

class HTMLGen:

    @classmethod
    def sidebar_route(cls, info: RouteInfo, id: int) -> str:
        method = info["method"]
        path   = info["path"]
        return (
            f'<div class="sidebar-sub-item" onclick="showRoute(\'{id}\')">'
            f'<span class="sidebar-badge b-{method}">{method}</span>'
            f'{path}'
            f'</div>'
        )

    @classmethod
    def sidebar_group(cls, prefix: str, group_id: str, routes_html: str) -> str:
        return (
            f'<div class="sidebar-group-label">{prefix}</div>'
            f'<div class="sidebar-sub" id="sub-{group_id}">'
            f'{routes_html}'
            f'</div>'
        )

    @classmethod
    def central_panel(cls, info: RouteInfo, id: int) -> str:
        method      = info["method"]
        path        = info["path"]
        summary     = info["metadata"].get("summary")
        title       = summary.get("title", "")       if summary else ""
        description = summary.get("description", "") if summary else ""
        deprecated  = info["metadata"].get("deprecated", False)
        version     = info["metadata"].get("version")

        deprecated_badge = '<span class="deprecated-badge">⚠ DEPRECATED</span>' if deprecated else ""
        version_badge    = f'<span class="nav-version" style="margin-left:8px">{version}</span>' if version else ""

        return (
            f'<div class="content-panel" id="panel-{id}">'
            f'<div class="route-badge-row">'
            f'<span class="route-method-badge b-{method}">{method}</span>'
            f'<span class="route-path-text">{path}</span>'
            f'{deprecated_badge}{version_badge}'
            f'</div>'
            f'<h1 class="route-title">{title}</h1>'
            f'<p class="route-desc">{description}</p>'
        )

    @classmethod
    def path_query_params(cls, info: RouteInfo) -> str:
        route_request: RouteRequest | None = info["metadata"].get("request")
        query_params: list[RouteParam] = route_request.get("query_params", []) if route_request else []
        path_params:  list[RouteParam] = route_request.get("path_params",  []) if route_request else []

        output = ""

        if path_params:
            output += '<h2 class="section-h">Path Parameters</h2>'
            for pparam in path_params:
                output += (
                    f'<div class="field-row">'
                    f'<div class="field-top">'
                    f'<span class="field-fname">{pparam.get("name")}</span>'
                    f'<span class="field-req-badge req">REQUIRED</span>'
                    f'</div>'
                    f'<p class="field-desc">{pparam.get("reason", "")}</p>'
                    f'</div>'
                )

        if query_params:
            output += '<h2 class="section-h">Query Parameters</h2>'
            for qparam in query_params:
                output += (
                    f'<div class="field-row">'
                    f'<div class="field-top">'
                    f'<span class="field-fname">{qparam.get("name")}</span>'
                    f'<span class="field-req-badge opt">OPTIONAL</span>'
                    f'</div>'
                    f'<p class="field-desc">{qparam.get("reason", "")}</p>'
                    f'</div>'
                )

        return output

    @classmethod
    def request_headers(cls, info: RouteInfo) -> str:
        route_request: RouteRequest | None = info["metadata"].get("request")
        if not route_request:
            return ""

        headers: list[RouteHeader] = route_request.get("headers", [])
        if not headers:
            return ""

        output = '<h2 class="section-h">Headers</h2>'
        for header in headers:
            reason = header.get("reason", "")
            output += (
                f'<div class="field-row">'
                f'<div class="field-top">'
                f'<span class="field-fname">{header.get("header_key")}</span>'
                f'<span class="field-req-badge req">REQUIRED</span>'
                f'<span class="field-type-tag">{header.get("header_value")}</span>'
                f'</div>'
                f'{"<p class=field-desc>" + reason + "</p>" if reason else ""}'
                f'</div>'
            )

        return output

    @classmethod
    def request_body(cls, info: RouteInfo) -> str:
        request: RouteRequest | None = info["metadata"].get("request")
        if not request:
            return ""

        model: Type[Model] | None = request.get("body")
        if not model:
            return ""

        fields_meta, _ = ModelInspector._inspect_model(model)

        output = f'<h2 class="section-h">Request Body · {model.__name__}</h2>'

        for fname, fmeta in fields_meta.items():
            is_optional   = fmeta.field_is_optional
            has_generator = fmeta.field_object.has_generator

            badge_class = "gen" if has_generator else ("opt" if is_optional else "req")
            badge_label = "GENERATED" if has_generator else ("OPTIONAL" if is_optional else "REQUIRED")

            type_name = fmeta.field_type.__name__ if hasattr(fmeta.field_type, "__name__") else str(fmeta.field_type) # type: ignore

            validators = "".join(
                f'<span class="validator-tag">{type(v).__name__}()</span>'
                for v in fmeta.field_object.validators
            )

            output += (
                f'<div class="field-row">'
                f'<div class="field-top">'
                f'<span class="field-fname">{fname}</span>'
                f'<span class="field-req-badge {badge_class}">{badge_label}</span>'
                f'<span class="field-type-tag">{type_name}</span>'
                f'</div>'
                f'<div class="field-validators">{validators}</div>'
                f'</div>'
            )

        return output

    @classmethod
    def responses(cls, info: RouteInfo) -> str:
        responses: list[RouteResponse] | None = info["metadata"].get("responses")
        if not responses:
            return ""

        output = '<h2 class="section-h">Responses</h2>'

        for resp in responses:
            code        = resp.get("status_code", 200)
            description = resp.get("description", "")
            example     = resp.get("example")

            color = "#4ade80" if str(code).startswith("2") else \
                    "#facc15" if str(code).startswith("3") else \
                    "#fca5a5"

            example_html = ""
            if example:
                formatted = json.dumps(example, indent=2)
                example_html = f'<div class="code-block" style="margin-top:8px;background:var(--surface2);border-radius:6px;padding:12px"><pre>{formatted}</pre></div>'

            output += (
                f'<div class="field-row">'
                f'<div class="field-top">'
                f'<span class="field-fname" style="color:{color}">{code}</span>'
                f'<span class="field-type-tag">{description}</span>'
                f'</div>'
                f'{example_html}'
                f'</div>'
            )

        return output

    @classmethod
    def security(cls, info: RouteInfo) -> str:
        sec: RouteSecurity | None = info["metadata"].get("security")
        if not sec:
            return ""

        scheme = sec.get("scheme")
        scheme_label = scheme.value if hasattr(scheme, "value") else str(scheme) # type: ignore
        description  = sec.get("description", "")

        return (
            f'<h2 class="section-h">Security</h2>'
            f'<div class="field-row">'
            f'<div class="field-top">'
            f'<span class="field-fname">{scheme_label.upper()}</span>'
            f'<span class="field-req-badge req">REQUIRED</span>'
            f'</div>'
            f'{"<p class=field-desc>" + description + "</p>" if description else ""}'
            f'</div>'
        )

    @classmethod
    def business_logic(cls, info: RouteInfo) -> str:
        logic: BusinessLogic | None = info["metadata"].get("logic")
        if not logic:
            return ""

        summary = logic.get("summary", "")
        notes   = logic.get("notes", "")
        steps: list[LogicStep] = logic.get("steps", [])

        steps_html = ""
        for i, step in enumerate(steps):
            how = step.get("how", "")
            why = step.get("why", "")
            steps_html += (
                f'<div class="field-row">'
                f'<div class="field-top">'
                f'<span class="field-fname">Step {i + 1}</span>'
                f'<span class="field-type-tag">{step.get("what", "")}</span>'
                f'</div>'
                f'{"<p class=field-desc>" + how + "</p>" if how else ""}'
                f'{"<p class=field-desc style=color:var(--text3)>" + why + "</p>" if why else ""}'
                f'</div>'
            )

        notes_html = f'<p class="field-desc" style="margin-top:12px;color:var(--text3)">{notes}</p>' if notes else ""

        return (
            f'<h2 class="section-h">Business Logic</h2>'
            f'<p class="route-desc" style="margin-bottom:16px">{summary}</p>'
            f'{steps_html}'
            f'{notes_html}'
        )

    @classmethod
    def depends_on(cls, info: RouteInfo) -> str:
        deps: list[DependsOn] | None = info["metadata"].get("depends_on")
        if not deps:
            return ""

        output = '<h2 class="section-h">Dependencies</h2>'

        for dep in deps:
            service   = dep.get("service", "")
            reason    = dep.get("reason", "")
            lifecycle = dep.get("lifecycle")
            lifecycle_label = lifecycle.value if lifecycle and hasattr(lifecycle, "value") else ""

            output += (
                f'<div class="field-row">'
                f'<div class="field-top">'
                f'<span class="field-fname">{service}</span>'
                f'{"<span class=field-req-badge gen>" + lifecycle_label.upper() + "</span>" if lifecycle_label else ""}'
                f'</div>'
                f'{"<p class=field-desc>" + reason + "</p>" if reason else ""}'
                f'</div>'
            )

        return output

    @classmethod
    def try_it_out(cls, info: RouteInfo, id: int) -> str:
        method  = info["method"]
        path    = info["path"]
        request: RouteRequest | None = info["metadata"].get("request")

        body_placeholder = ""
        if request and request.get("body"):
            model = request["body"] # type: ignore
            fields_meta, _ = ModelInspector._inspect_model(model)
            example = {
                fname: f"<{fmeta.field_type.__name__ if hasattr(fmeta.field_type, '__name__') else 'value'}>" # type: ignore
                for fname, fmeta in fields_meta.items()
            }
            body_placeholder = json.dumps(example, indent=2)

        textarea_html = ""
        if method in ("POST", "PUT", "PATCH"):
            textarea_html = (
                f'<div class="try-body">'
                f'<textarea class="try-textarea" id="try-body-{id}">{body_placeholder}</textarea>'
                f'</div>'
            )

        return (
            f'<div class="try-section">'
            f'<div class="try-header">'
            f'<div class="try-header-left">'
            f'<div class="try-play">▷</div>'
            f'<div class="try-title">Try it out</div>'
            f'</div>'
            f'<span class="try-subtitle">Interactive Console</span>'
            f'</div>'
            f'{textarea_html}'
            f'<div class="try-footer">'
            f'<button class="try-execute" id="exec-btn-{id}" onclick="executeRequest(\'{id}\')">'
            f'Send Request →'
            f'</button>'
            f'</div>'
            f'</div>'
        )

    @classmethod
    def feedback(cls, id: int) -> str:
        return (
            f'<div class="feedback-row">'
            f'<span class="feedback-label">Was this helpful?</span>'
            f'<button class="feedback-btn" id="btn-helpful-{id}" onclick="toggleFeedback(\'{id}\', \'helpful\')">👍 Helpful</button>'
            f'<button class="feedback-btn" id="btn-issue-{id}"   onclick="toggleFeedback(\'{id}\', \'issue\')">👎 Issue</button>'
            f'</div>'
        )

    @classmethod
    def full_panel(cls, info: RouteInfo, id: int) -> str:
        return (
            cls.central_panel(info, id)
            + cls.security(info)
            + cls.path_query_params(info)
            + cls.request_headers(info)
            + cls.request_body(info)
            + cls.responses(info)
            + cls.business_logic(info)
            + cls.depends_on(info)
            + cls.try_it_out(info, id)
            + cls.feedback(id)
            + '</div>'
        )

    @staticmethod
    def find_tag_and_insert(template: str, tag: str, content: str) -> str:
        return template.replace(f"<!-- {tag} -->", content)
