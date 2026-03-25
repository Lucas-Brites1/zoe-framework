from zoe_doc.doc_metadata import *
from zoe_doc.html_builder import *
from zoe_di.inspector import ModelInspector
from typing import Type
import json


class HTMLGen:

    @classmethod
    def sidebar_route(cls, info: RouteInfo, id: int, active: bool = False) -> HtmlElement:
        method = info["method"]
        path   = info["path"]
        class_ = "sidebar-route active" if active else "sidebar-route"
        return (
            div(class_=class_, data_rid=str(id), onclick=f"showRoute('{id}')")
            .append(span(class_=f"method-badge m-{method}").append(method))
            .append(span(class_="route-path-label").append(path))
        )

    @classmethod
    def sidebar_group(cls, prefix: str, group_id: str, *routes: HtmlElement) -> HtmlElement:
        container = div(class_="sidebar-sub", id=f"sub-{group_id}")
        for route in routes:
            container.append(route)

        label = (
            div(class_="sidebar-section-label", onclick=f"toggleGroup('{group_id}')")
            .append(span().append(prefix))
            .append(span(class_="sidebar-chevron").append(i(**{"data-lucide": "chevron-down"})))
        )

        return (
            div()
            .append(label)
            .append(container)
        )

    @classmethod
    def central_panel(cls, info: RouteInfo, id: int, active: bool = False) -> HtmlElement:
        method      = info["method"]
        path        = info["path"]
        meta        = info["metadata"]
        summary     = meta.get("summary")
        title       = summary.get("title", "")       if summary else ""
        description = summary.get("description", "") if summary else ""
        tags        = summary.get("tags", [])         if summary else []
        deprecated  = meta.get("deprecated", False)
        version     = meta.get("version")

        class_ = "content-panel active animate-in" if active else "content-panel"

        endpoint_row = (
            div(class_="route-endpoint")
            .append(span(class_=f"route-method m-{method}").append(method))
            .append(span(class_="route-path").append(path))
        )
        if deprecated:
            endpoint_row.append(
                span(class_="deprecated-badge")
                .append(i(**{"data-lucide": "alert-triangle"}))
                .append(" DEPRECATED")
            )
        if version:
            endpoint_row.append(span(class_="version-badge").append(version))

        header_area = div(class_="route-header-area")
        header_area.append(endpoint_row)
        header_area.append(h1(class_="route-title").append(title))

        if description:
            header_area.append(p(class_="route-desc").append(description))

        if tags:
            tag_row = div(class_="tag-row")
            for tag in tags:
                tag_row.append(span(class_="tag").append(tag))
            header_area.append(tag_row)

        panel = div(class_=class_, id=f"panel-{id}").append(header_area)
        return panel

    @classmethod
    def security(cls, info: RouteInfo) -> HtmlElement:
        sec: RouteSecurity | None = info["metadata"].get("security")
        container = div()
        if not sec:
            return container

        scheme = sec.get("scheme")
        label  = scheme.value if hasattr(scheme, "value") else str(scheme)  # type: ignore
        desc   = sec.get("description", "")

        pill = (
            div(class_="security-pill")
            .append(i(**{"data-lucide": "lock"}))
            .append(" ")
            .append(label.upper())
        )

        section = div(class_="section")
        section.append(div(class_="section-label").append("Security"))
        section.append(pill)
        if desc:
            section.append(p(class_="field-desc", style="margin-top:8px").append(desc))

        container.append(section)
        return container

    @classmethod
    def _params_table(cls, label: str, params: list, badge_class: str, badge_label: str) -> HtmlElement:
        section = div(class_="section")
        section.append(div(class_="section-label").append(label))

        table = div(class_="params-table")
        head  = (
            div(class_="params-table-head")
            .append(span().append("Parameter"))
            .append(span().append("Type"))
            .append(span().append("Description"))
        )
        table.append(head)

        for param in params:
            name   = param.get("name", "")
            reason = param.get("reason", "")
            row = (
                div(class_="params-table-row")
                .append(
                    div()
                    .append(
                        div(class_="param-name")
                        .append(name)
                        .append(span(class_=f"field-badge {badge_class}").append(badge_label))
                    )
                )
                .append(div().append(span(class_="param-type").append("string")))
                .append(div().append(p(class_="param-desc").append(reason)))
            )
            table.append(row)

        section.append(table)
        return section

    @classmethod
    def path_query_params(cls, info: RouteInfo) -> HtmlElement:
        req          = info["metadata"].get("request")
        path_params  = req.get("path_params",  []) if req else []
        query_params = req.get("query_params", []) if req else []
        container    = div()

        if path_params:
            container.append(cls._params_table("Path Parameters", path_params, "b-req", "REQUIRED"))

        if query_params:
            container.append(cls._params_table("Query Parameters", query_params, "b-opt", "OPTIONAL"))

        return container

    @classmethod
    def request_headers(cls, info: RouteInfo) -> HtmlElement:
        req     = info["metadata"].get("request")
        container = div()
        if not req:
            return container
        headers: list[RouteHeader] = req.get("headers", [])
        if not headers:
            return container

        section = div(class_="section")
        section.append(div(class_="section-label").append("Headers"))
        for h_ in headers:
            reason = h_.get("reason", "")
            top    = (
                div(class_="field-top")
                .append(span(class_="field-name").append(h_.get("header_key", "")))
                .append(span(class_="field-type").append(h_.get("header_value", "")))
                .append(span(class_="field-badge b-req").append("REQUIRED"))
            )
            row = div(class_="field-row").append(top)
            if reason:
                row.append(p(class_="field-desc").append(reason))
            section.append(row)

        container.append(section)
        return container

    @classmethod
    def request_body(cls, info: RouteInfo) -> HtmlElement:
        req       = info["metadata"].get("request")
        container = div()
        if not req:
            return container
        model: Type[Model] | None = req.get("body")
        if not model:
            return container

        fields_meta, _ = ModelInspector._inspect_model(model)
        section = div(class_="section")
        section.append(div(class_="section-label").append(f"Request Body · {model.__name__}"))

        try:
            inst    = model.__new__(model)
            example = getattr(inst, "example", None)
        except Exception:
            example = None

        if example:
            section.append(
                div(class_="example-wrap")
                .append(div(class_="example-label").append("Example"))
                .append(div(class_="example-block").append(json.dumps(example, indent=2)))
            )

        for fname, fmeta in fields_meta.items():
            is_opt   = fmeta.field_is_optional
            is_gen   = fmeta.field_object.has_generator
            bcls     = "b-gen" if is_gen else ("b-opt" if is_opt else "b-req")
            blbl     = "GENERATED" if is_gen else ("OPTIONAL" if is_opt else "REQUIRED")
            tname    = fmeta.field_type.__name__ if hasattr(fmeta.field_type, "__name__") else str(fmeta.field_type)  # type: ignore

            top = (
                div(class_="field-top")
                .append(span(class_="field-name").append(fname))
                .append(span(class_=f"field-badge {bcls}").append(blbl))
                .append(span(class_="field-type").append(tname))
            )
            val_row = div(class_="validator-row")
            for v in fmeta.field_object.validators:
                val_row.append(span(class_="validator").append(f"{type(v).__name__}()"))

            section.append(div(class_="field-row").append(top).append(val_row))

        req_examples: dict | None = req.get("examples")  # type: ignore
        if req_examples:
            for label_, data in req_examples.items():
                section.append(
                    div(class_="example-wrap")
                    .append(div(class_="example-label").append(label_))
                    .append(div(class_="example-block").append(json.dumps(data, indent=2)))
                )

        container.append(section)
        return container

    @classmethod
    def responses(cls, info: RouteInfo) -> HtmlElement:
        resp_list: list[RouteResponse] | None = info["metadata"].get("responses")
        container = div()
        if not resp_list:
            return container

        section = div(class_="section")
        section.append(div(class_="section-label").append("Responses"))

        for resp in resp_list:
            code     = resp.get("status_code", 200)
            desc     = resp.get("description", "")
            examples = resp.get("examples")
            cs       = str(code)
            sclass   = "s2xx" if cs.startswith("2") else "s3xx" if cs.startswith("3") else "s4xx" if cs.startswith("4") else "s5xx"

            row = (
                div(class_="response-row")
                .append(
                    div(class_="response-top")
                    .append(span(class_=f"response-code {sclass}").append(cs))
                    .append(span(class_="response-desc").append(desc))
                )
            )

            if examples:
                for lbl, data in examples.items():
                    row.append(
                        div(class_="example-wrap")
                        .append(div(class_="example-label", style="margin-top:10px").append(lbl))
                        .append(div(class_="example-block").append(json.dumps(data, indent=2)))
                    )

            section.append(row)

        container.append(section)
        return container

    @classmethod
    def business_logic(cls, info: RouteInfo) -> HtmlElement:
        logic: BusinessLogic | None = info["metadata"].get("logic")
        container = div()
        if not logic:
            return container

        summary_text = logic.get("summary", "")
        notes        = logic.get("notes", "")
        steps        = logic.get("steps", [])

        section = div(class_="section")
        section.append(div(class_="section-label").append("Business Logic"))
        section.append(p(class_="field-desc", style="margin-bottom:14px").append(summary_text))

        for idx, step in enumerate(steps):
            how = step.get("how", "")
            why = step.get("why", "")
            body_ = div()
            body_.append(div(class_="step-what").append(step.get("what", "")))
            if how:
                body_.append(div(class_="step-how").append(how))
            if why:
                body_.append(
                    div(class_="step-why")
                    .append(i(**{"data-lucide": "corner-down-right"}))
                    .append(f" {why}")
                )
            section.append(
                div(class_="logic-step")
                .append(div(class_="step-num").append(str(idx + 1)))
                .append(body_)
            )

        if notes:
            section.append(
                div(class_="logic-notes")
                .append(i(**{"data-lucide": "file-text"}))
                .append(f" {notes}")
            )

        container.append(section)
        return container

    @classmethod
    def depends_on(cls, info: RouteInfo) -> HtmlElement:
        deps: list[DependsOn] | None = info["metadata"].get("depends_on")
        container = div()
        if not deps:
            return container

        section = div(class_="section")
        section.append(div(class_="section-label").append("Dependencies"))

        for dep in deps:
            service   = dep.get("service", "")
            reason    = dep.get("reason", "")
            lifecycle = dep.get("lifecycle")
            lbl       = lifecycle.value if lifecycle and hasattr(lifecycle, "value") else ""

            inner = div(style="flex:1")
            inner.append(div(class_="dep-name").append(service))
            if reason:
                inner.append(div(class_="dep-reason").append(reason))

            card = div(class_="dep-card").append(inner)
            if lbl:
                card.append(span(class_="field-badge b-gen").append(lbl.upper()))

            section.append(card)

        container.append(section)
        return container

    @classmethod
    def author_infos(cls, info: RouteInfo) -> HtmlElement:
        author: Author | None = info["metadata"].get("author")
        container = div()
        if not author:
            return container

        name    = author.get("name", "")
        email   = author.get("email", "")
        squad   = author.get("squad", "")
        team    = author.get("team", "")
        contact = author.get("contact")

        initials = "".join(w[0].upper() for w in name.split()[:2]) if name else "?"
        meta_parts = [x for x in [email, squad, team] if x]
        meta_text  = " · ".join(meta_parts)

        right = div()
        right.append(div(class_="author-name").append(name))
        if meta_text:
            right.append(div(class_="author-meta").append(meta_text))
        if contact:
            c = ", ".join(contact) if isinstance(contact, list) else contact
            right.append(div(class_="author-meta", style="margin-top:3px").append(c))

        section = div(class_="section")
        section.append(div(class_="section-label").append("Author"))
        section.append(
            div(class_="author-card")
            .append(div(class_="author-avatar").append(initials))
            .append(right)
        )

        container.append(section)
        return container

    @classmethod
    def try_it_out(cls, info: RouteInfo, id: int) -> HtmlElement:
        method = info.get("method", "GET")
        path   = info.get("path", "/")
        prefix = info.get("prefix", "")
        req    = info["metadata"].get("request")

        full_path = (prefix.rstrip("/") + "/" + path.lstrip("/")).rstrip("/") or "/"

        body_placeholder = ""
        if req and req.get("body"):
            model = req["body"]  # type: ignore
            try:
                inst    = model.__new__(model)
                example = getattr(inst, "example", None)
            except Exception:
                example = None
            if example is None:
                fields_meta, _ = ModelInspector._inspect_model(model)
                example = {
                    fname: f"<{fmeta.field_type.__name__ if hasattr(fmeta.field_type, '__name__') else 'value'}>"  # type: ignore
                    for fname, fmeta in fields_meta.items()
                }
            body_placeholder = json.dumps(example, indent=2)

        top = (
            div(class_="try-top")
            .append(
                div(class_="try-top-left")
                .append(div(class_="try-play-btn").append(i(**{"data-lucide": "play"})))
                .append(div(class_="try-title").append("Try it out"))
            )
            .append(span(class_="try-console-label").append("Interactive"))
        )

        box = div(class_="try-box").append(top)

        box.append(
            div(class_="try-body")
            .append(
                div(class_="try-path-row")
                .append(span(class_=f"try-method-chip m-{method}").append(method))
                .append(
                    input_(
                        class_="try-path-input",
                        id=f"try-path-{id}",
                        type="text",
                        value=full_path
                    )
                )
            )
        )

        if method in ("POST", "PUT", "PATCH"):
            box.append(
                div(class_="try-body")
                .append(div(class_="try-body-label").append("Request Body"))
                .append(textarea(class_="try-textarea", id=f"try-body-{id}").append(body_placeholder))
            )

        # ── Auth ──────────────────────────────────────────────────────
        schemes = [
            ("none",   "None"),
            ("bearer", "Bearer"),
            ("apikey", "API Key"),
            ("basic",  "Basic"),
            ("oauth2", "OAuth 2.0"),
            ("custom", "Custom"),
        ]

        auth_tabs = div(class_="try-auth-tabs")
        for idx, (scheme_id, scheme_label) in enumerate(schemes):
            cls_ = "try-auth-tab active" if idx == 0 else "try-auth-tab"
            auth_tabs.append(
                button(class_=cls_, **{"data-scheme": scheme_id},
                       onclick=f"switchAuthScheme('{id}','{scheme_id}')")
                .append(scheme_label)
            )

        # Bearer group
        auth_bearer = (
            div(class_="try-auth-group", **{"data-group": "bearer"})
            .append(
                div(class_="try-auth-row")
                .append(span(class_="try-auth-prefix").append("Bearer"))
                .append(input_(class_="try-auth-input", id=f"try-auth-bearer-token-{id}", type="text", placeholder="token"))
            )
        )

        # API Key group
        auth_apikey = (
            div(class_="try-auth-group", **{"data-group": "apikey"})
            .append(
                div(class_="try-auth-pair")
                .append(input_(class_="try-auth-input", id=f"try-auth-apikey-name-{id}", type="text", placeholder="X-API-Key", value="X-API-Key"))
                .append(input_(class_="try-auth-input", id=f"try-auth-apikey-val-{id}",  type="text", placeholder="api-key-value"))
            )
        )

        # Basic group
        auth_basic = (
            div(class_="try-auth-group", **{"data-group": "basic"})
            .append(
                div(class_="try-auth-pair")
                .append(input_(class_="try-auth-input", id=f"try-auth-basic-user-{id}", type="text",     placeholder="username"))
                .append(input_(class_="try-auth-input", id=f"try-auth-basic-pass-{id}", type="password", placeholder="password"))
            )
        )

        # OAuth2 group
        auth_oauth2 = (
            div(class_="try-auth-group", **{"data-group": "oauth2"})
            .append(
                div(class_="try-auth-row")
                .append(span(class_="try-auth-prefix").append("Bearer"))
                .append(input_(class_="try-auth-input", id=f"try-auth-oauth2-token-{id}", type="text", placeholder="access token"))
            )
        )

        # Custom group
        auth_custom = (
            div(class_="try-auth-group", **{"data-group": "custom"})
            .append(
                div(class_="try-auth-pair")
                .append(input_(class_="try-auth-input", id=f"try-auth-custom-name-{id}", type="text", placeholder="Header-Name"))
                .append(input_(class_="try-auth-input", id=f"try-auth-custom-val-{id}",  type="text", placeholder="value"))
            )
        )

        auth_container = (
            div(class_="try-body")
            .append(div(class_="try-body-label").append("Auth"))
            .append(
                div(id=f"try-auth-container-{id}")
                .append(auth_tabs)
                .append(auth_bearer)
                .append(auth_apikey)
                .append(auth_basic)
                .append(auth_oauth2)
                .append(auth_custom)
            )
        )

        box.append(auth_container)

        # ── Custom Headers ────────────────────────────────────────────
        box.append(
            div(class_="try-body")
            .append(div(class_="try-body-label").append("Headers"))
            .append(div(class_="try-headers-list", id=f"try-headers-{id}"))
            .append(
                HtmlElement("button",
                    class_="try-add-header-btn",
                    onclick=f"addHeader('{id}')"
                )
                .append(i(**{"data-lucide": "plus"}))
                .append(" Add Header")
            )
        )

        box.append(
            div(class_="try-footer")
            .append(
                button(
                    class_="try-btn",
                    id=f"exec-btn-{id}",
                    data_method=method,
                    onclick=f"executeRequest('{id}')"
                )
                .append(i(**{"data-lucide": "send"}))
                .append(" Send Request")
            )
        )

        box.append(
            div(class_="try-response", id=f"try-response-{id}", style="display:none")
            .append(
                div(class_="try-response-header")
                .append(span(class_="try-response-status", id=f"try-status-{id}").append(""))
                .append(span(class_="try-response-time", id=f"try-time-{id}").append(""))
            )
            .append(div(class_="try-response-body", id=f"try-response-body-{id}"))
        )

        return div(class_="section").append(box)

    # ── Code Examples ──────────────────────────────────────────────────────────

    @classmethod
    def _build_example_payload(cls, req: RouteRequest | None) -> dict | None:
        if not req or not req.get("body"):
            return None
        model = req["body"]  # type: ignore
        try:
            inst    = model.__new__(model)
            example = getattr(inst, "example", None)
        except Exception:
            example = None
        if example is None:
            fields_meta, _ = ModelInspector._inspect_model(model)
            example = {
                fname: f"<{fmeta.field_type.__name__ if hasattr(fmeta.field_type, '__name__') else 'value'}>"  # type: ignore
                for fname, fmeta in fields_meta.items()
            }
        return example

    @classmethod
    def _build_curl(cls, method: str, full_path: str, req: RouteRequest | None, example: dict | None) -> str:
        lines = [f"curl -X {method} \\"]
        lines.append(f"  'http://localhost:8080{full_path}' \\")

        if req and req.get("headers"):
            for h in req.get("headers", []):
                lines.append(f"  -H '{h.get('header_key', '')}: {h.get('header_value', '')}' \\")

        if method in ("POST", "PUT", "PATCH") and example:
            lines.append(f"  -H 'Content-Type: application/json' \\")
            body_str = json.dumps(example, separators=(",", ": "))
            lines.append(f"  -d '{body_str}'")
        else:
            lines[-1] = lines[-1].rstrip(" \\")

        return "\n".join(lines)

    @classmethod
    def _build_python(cls, method: str, full_path: str, req: RouteRequest | None, example: dict | None) -> str:
        lines = ["import requests", ""]

        extra_headers: list[str] = []
        if req and req.get("headers"):
            for h in req.get("headers", []):
                extra_headers.append(f'    "{h.get("header_key", "")}": "{h.get("header_value", "")}"')

        if method in ("POST", "PUT", "PATCH") and example:
            extra_headers.append('    "Content-Type": "application/json"')

        if extra_headers:
            lines.append("headers = {")
            lines.extend([line + "," for line in extra_headers])
            lines.append("}")
            lines.append("")

        if method in ("POST", "PUT", "PATCH") and example:
            lines.append(f"payload = {json.dumps(example, indent=4)}")
            lines.append("")
            hdr = ", headers=headers" if extra_headers else ""
            lines.append(f'response = requests.{method.lower()}(')
            lines.append(f'    "http://localhost:8080{full_path}",')
            lines.append(f'    json=payload{hdr}')
            lines.append(")")
        else:
            hdr = ", headers=headers" if extra_headers else ""
            lines.append(f'response = requests.{method.lower()}(')
            lines.append(f'    "http://localhost:8080{full_path}"{hdr}')
            lines.append(")")

        lines.append("")
        lines.append("print(response.status_code)")
        lines.append("print(response.json())")
        return "\n".join(lines)

    @classmethod
    def _build_node(cls, method: str, full_path: str, req: RouteRequest | None, example: dict | None) -> str:
        lines = ['// Node.js — fetch API (built-in Node 18+)', ""]

        has_body = method in ("POST", "PUT", "PATCH") and example

        header_entries: list[str] = []
        if req and req.get("headers"):
            for h in req.get("headers", []):
                header_entries.append(f'  "{h.get("header_key", "")}": "{h.get("header_value", "")}"')
        if has_body:
            header_entries.append('  "Content-Type": "application/json"')

        lines.append("const response = await fetch(")
        lines.append(f'  "http://localhost:8080{full_path}",')
        lines.append("  {")
        lines.append(f'    method: "{method}",')

        if header_entries:
            lines.append("    headers: {")
            lines.extend([line + "," for line in header_entries])
            lines.append("    },")

        if has_body:
            lines.append(f"    body: JSON.stringify({json.dumps(example, separators=(',', ': '))}),")

        lines.append("  }")
        lines.append(");")
        lines.append("")
        lines.append("const data = await response.json();")
        lines.append("console.log(data);")
        return "\n".join(lines)

    @classmethod
    def code_examples(cls, info: RouteInfo, id: int) -> HtmlElement:
        method    = info.get("method", "GET")
        path      = info.get("path", "/")
        prefix    = info.get("prefix", "")
        req       = info["metadata"].get("request")
        full_path = (prefix.rstrip("/") + "/" + path.lstrip("/")).rstrip("/") or "/"

        example = cls._build_example_payload(req)

        curl   = cls._build_curl(method, full_path, req, example)
        python = cls._build_python(method, full_path, req, example)
        node   = cls._build_node(method, full_path, req, example)

        tabs = (
            div(class_="code-tabs")
            .append(button(class_="code-tab active", data_tab=f"curl-{id}",   onclick=f"switchTab(this,'{id}')").append("cURL"))
            .append(button(class_="code-tab",        data_tab=f"python-{id}", onclick=f"switchTab(this,'{id}')").append("Python"))
            .append(button(class_="code-tab",        data_tab=f"node-{id}",   onclick=f"switchTab(this,'{id}')").append("Node.js"))
        )

        def code_block(lang_id: str, content: str, visible: bool) -> HtmlElement:
            wrapper = div(class_="code-example", id=lang_id)
            if not visible:
                wrapper = div(class_="code-example", id=lang_id, style="display:none")
            copy_btn = button(
                class_="code-copy-btn",
                data_target=lang_id,
                onclick=f"copyCode('{lang_id}')"
            ).append("Copy")
            block = div(class_="code-example-inner").append(copy_btn).append(
                pre(class_="code-pre").append(code(class_="code-content").append(content))
            )
            wrapper.append(block)
            return wrapper

        section = div(class_="section")
        section.append(div(class_="section-label").append("Code Examples"))
        box = div(class_="code-examples-box")
        box.append(tabs)
        box.append(code_block(f"curl-{id}",   curl,   True))
        box.append(code_block(f"python-{id}", python, False))
        box.append(code_block(f"node-{id}",   node,   False))
        section.append(box)
        return section

    # ── Full Panel — two-column layout ────────────────────────────────────────

    @classmethod
    def full_panel(cls, info: RouteInfo, id: int, active: bool = False) -> str:
        panel = cls.central_panel(info, id, active=active)

        left = div(class_="doc-left")
        left \
            .append(cls.security(info)) \
            .append(cls.path_query_params(info)) \
            .append(cls.request_headers(info)) \
            .append(cls.request_body(info)) \
            .append(cls.responses(info)) \
            .append(cls.author_infos(info)) \
            .append(cls.business_logic(info)) \
            .append(cls.depends_on(info))

        right = div(class_="doc-right")
        right \
            .append(cls.code_examples(info, id)) \
            .append(cls.try_it_out(info, id))

        panel.append(div(class_="doc-body").append(left).append(right))
        return panel.make

    @staticmethod
    def find_tag_and_insert(template: str, tag: str, content: str) -> str:
        return template.replace(f"<!-- {tag} -->", content)
