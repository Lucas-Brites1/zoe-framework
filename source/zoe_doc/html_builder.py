from abc import ABC, abstractmethod
from typing import Self, Union
from html import escape

class HtmlContent(ABC): 
    @abstractmethod
    def append(self, content: Union[str,"HtmlContent",None] = None) -> "HtmlContent": ...

    @property
    @abstractmethod
    def make(self) -> str: ...

    def __str__(self) -> str: 
        return self.make

    def __repr__(self) -> str:
        return self.make
    

class HtmlElement(HtmlContent):
    def __init__(self, tag: str, **attrs):
        self._tag = tag
        self._attrs = self._normalize_attrs(attrs)
        self._content: list[str] = []
    
    def append(self, content: Union[str,"HtmlContent",None] = None) -> Self:
        if content is None:
            return self

        if isinstance(content, HtmlContent):
            self._content.append(content.make)
        else:
            self._content.append(escape(str(content)))
        
        return self
    
    def _normalize_attrs(self, attrs: dict) -> dict:
        normalized = {}
        for key, value in attrs.items():
            if key.endswith("_"):
                key = key[:-1]
            key = key.replace("_", "-")
            normalized[key] = str(value)
        return normalized

    def _build_content(self) -> str:
        attrs = ""
        if self._attrs:
            attrs = " " + " ".join(f'{k}="{v}"' for k, v in self._attrs.items())

        open_tag = f"<{self._tag}{attrs}>"
        close_tag = f"</{self._tag}>"
        children = "".join(self._content)
        
        return f"{open_tag}{children}{close_tag}"

    def pretty(self, indent: int = 0) -> str:
        spaces = "  " * indent
        attrs = ""
        if self._attrs:
            attrs = " " + " ".join(
                f'{k}="{v}"' 
                for k, v in self._attrs.items()
            )
        
        result = f"{spaces}<{self._tag}{attrs}>"
        
        if self._content:
            result += "\n"
            for child in self._content:
                result += f"{spaces}  {child}\n"
            result += f"{spaces}</{self._tag}>"
        else:
            result += f"</{self._tag}>"
        
        return result

    @property
    def make(self) -> str:
        return self._build_content()


class SelfClosingElement(HtmlContent):
    def __init__(self, tag: str, **attrs):
        self._tag = tag
        self._attrs = self._normalize_attrs(attrs)

    def _normalize_attrs(self, attrs: dict) -> dict:
        normalized = {}
        for key, value in attrs.items():
            if key.endswith("_"):
                key = key[:-1]
            key = key.replace("_", "-")
            normalized[key] = str(value)
        return normalized

    def append(self, content: Union[str,"HtmlContent",None] = None) -> Self:
        raise ValueError(f"<{self._tag}> é auto-fechada e não pode ter filhos")

    @property
    def make(self) -> str:
        attrs = ""
        if self._attrs:
            attrs = " " + " ".join(f'{k}="{v}"' for k, v in self._attrs.items())
        return f"<{self._tag}{attrs} />"


# ============================================
# Page Structure
# ============================================
def html(**attrs) -> HtmlElement:
    return HtmlElement("html", **attrs)

def head(**attrs) -> HtmlElement:
    return HtmlElement("head", **attrs)

def body(**attrs) -> HtmlElement:
    return HtmlElement("body", **attrs)

def title(**attrs) -> HtmlElement:
    return HtmlElement("title", **attrs)

def meta(**attrs) -> SelfClosingElement:
    return SelfClosingElement("meta", **attrs)

def link(**attrs) -> SelfClosingElement:
    return SelfClosingElement("link", **attrs)

def style(**attrs) -> HtmlElement:
    return HtmlElement("style", **attrs)

def script(**attrs) -> HtmlElement:
    return HtmlElement("script", **attrs)

# ============================================
# Text Elements
# ============================================
def h1(**attrs) -> HtmlElement:
    return HtmlElement("h1", **attrs)

def h2(**attrs) -> HtmlElement:
    return HtmlElement("h2", **attrs)

def h3(**attrs) -> HtmlElement:
    return HtmlElement("h3", **attrs)

def h4(**attrs) -> HtmlElement:
    return HtmlElement("h4", **attrs)

def h5(**attrs) -> HtmlElement:
    return HtmlElement("h5", **attrs)

def h6(**attrs) -> HtmlElement:
    return HtmlElement("h6", **attrs)

def p(**attrs) -> HtmlElement:
    return HtmlElement("p", **attrs)

def span(**attrs) -> HtmlElement:
    return HtmlElement("span", **attrs)

def strong(**attrs) -> HtmlElement:
    return HtmlElement("strong", **attrs)

def em(**attrs) -> HtmlElement:
    return HtmlElement("em", **attrs)

def small(**attrs) -> HtmlElement:
    return HtmlElement("small", **attrs)

def mark(**attrs) -> HtmlElement:
    return HtmlElement("mark", **attrs)

def code(**attrs) -> HtmlElement:
    return HtmlElement("code", **attrs)

def pre(**attrs) -> HtmlElement:
    return HtmlElement("pre", **attrs)

def blockquote(**attrs) -> HtmlElement:
    return HtmlElement("blockquote", **attrs)

def br(**attrs) -> SelfClosingElement:
    return SelfClosingElement("br", **attrs)

def hr(**attrs) -> SelfClosingElement:
    return SelfClosingElement("hr", **attrs)

# ============================================
# Sections/Layout
# ============================================
def header(**attrs) -> HtmlElement:
    return HtmlElement("header", **attrs)

def footer(**attrs) -> HtmlElement:
    return HtmlElement("footer", **attrs)

def main(**attrs) -> HtmlElement:
    return HtmlElement("main", **attrs)

def nav(**attrs) -> HtmlElement:
    return HtmlElement("nav", **attrs)

def section(**attrs) -> HtmlElement:
    return HtmlElement("section", **attrs)

def article(**attrs) -> HtmlElement:
    return HtmlElement("article", **attrs)

def aside(**attrs) -> HtmlElement:
    return HtmlElement("aside", **attrs)

# ============================================
# Group Elements
# ============================================
def div(**attrs) -> HtmlElement:
    return HtmlElement("div", **attrs)

# ============================================
# Navigation
# ============================================
def a(**attrs) -> HtmlElement:
    return HtmlElement("a", **attrs)

# ============================================
# Lists
# ============================================
def ul(**attrs) -> HtmlElement:
    return HtmlElement("ul", **attrs)

def ol(**attrs) -> HtmlElement:
    return HtmlElement("ol", **attrs)

def li(**attrs) -> HtmlElement:
    return HtmlElement("li", **attrs)

def dl(**attrs) -> HtmlElement:
    return HtmlElement("dl", **attrs)

def dt(**attrs) -> HtmlElement:
    return HtmlElement("dt", **attrs)

def dd(**attrs) -> HtmlElement:
    return HtmlElement("dd", **attrs)

# ============================================
# Tables
# ============================================
def table(**attrs) -> HtmlElement:
    return HtmlElement("table", **attrs)

def caption(**attrs) -> HtmlElement:
    return HtmlElement("caption", **attrs)

def thead(**attrs) -> HtmlElement:
    return HtmlElement("thead", **attrs)

def tbody(**attrs) -> HtmlElement:
    return HtmlElement("tbody", **attrs)

def tfoot(**attrs) -> HtmlElement:
    return HtmlElement("tfoot", **attrs)

def tr(**attrs) -> HtmlElement:
    return HtmlElement("tr", **attrs)

def th(**attrs) -> HtmlElement:
    return HtmlElement("th", **attrs)

def td(**attrs) -> HtmlElement:
    return HtmlElement("td", **attrs)

def col(**attrs) -> SelfClosingElement:
    return SelfClosingElement("col", **attrs)

def colgroup(**attrs) -> HtmlElement:
    return HtmlElement("colgroup", **attrs)

# ============================================
# Forms
# ============================================
def form(**attrs) -> HtmlElement:
    return HtmlElement("form", **attrs)

def input_(**attrs) -> SelfClosingElement:
    return SelfClosingElement("input", **attrs)

def textarea(**attrs) -> HtmlElement:
    return HtmlElement("textarea", **attrs)

def button(**attrs) -> HtmlElement:
    return HtmlElement("button", **attrs)

def label(**attrs) -> HtmlElement:
    return HtmlElement("label", **attrs)

def select(**attrs) -> HtmlElement:
    return HtmlElement("select", **attrs)

def option(**attrs) -> HtmlElement:
    return HtmlElement("option", **attrs)

def optgroup(**attrs) -> HtmlElement:
    return HtmlElement("optgroup", **attrs)

def fieldset(**attrs) -> HtmlElement:
    return HtmlElement("fieldset", **attrs)

def legend(**attrs) -> HtmlElement:
    return HtmlElement("legend", **attrs)

def datalist(**attrs) -> HtmlElement:
    return HtmlElement("datalist", **attrs)

def output(**attrs) -> HtmlElement:
    return HtmlElement("output", **attrs)

def progress(**attrs) -> HtmlElement:
    return HtmlElement("progress", **attrs)

def meter(**attrs) -> HtmlElement:
    return HtmlElement("meter", **attrs)

# ============================================
# Media
# ============================================
def img(**attrs) -> SelfClosingElement:
    return SelfClosingElement("img", **attrs)

def video(**attrs) -> HtmlElement:
    return HtmlElement("video", **attrs)

def audio(**attrs) -> HtmlElement:
    return HtmlElement("audio", **attrs)

def source(**attrs) -> SelfClosingElement:
    return SelfClosingElement("source", **attrs)

def track(**attrs) -> SelfClosingElement:
    return SelfClosingElement("track", **attrs)

def picture(**attrs) -> HtmlElement:
    return HtmlElement("picture", **attrs)

def iframe(**attrs) -> HtmlElement:
    return HtmlElement("iframe", **attrs)

def embed(**attrs) -> SelfClosingElement:
    return SelfClosingElement("embed", **attrs)

def object_(**attrs) -> HtmlElement:
    return HtmlElement("object", **attrs)

def param(**attrs) -> SelfClosingElement:
    return SelfClosingElement("param", **attrs)

def canvas(**attrs) -> HtmlElement:
    return HtmlElement("canvas", **attrs)

def svg(**attrs) -> HtmlElement:
    return HtmlElement("svg", **attrs)

# ============================================
# Interactive Elements
# ============================================
def details(**attrs) -> HtmlElement:
    return HtmlElement("details", **attrs)

def summary(**attrs) -> HtmlElement:
    return HtmlElement("summary", **attrs)

def dialog(**attrs) -> HtmlElement:
    return HtmlElement("dialog", **attrs)

# ============================================
# Semantic Text
# ============================================
def abbr(**attrs) -> HtmlElement:
    return HtmlElement("abbr", **attrs)

def address(**attrs) -> HtmlElement:
    return HtmlElement("address", **attrs)

def cite(**attrs) -> HtmlElement:
    return HtmlElement("cite", **attrs)

def q(**attrs) -> HtmlElement:
    return HtmlElement("q", **attrs)

def dfn(**attrs) -> HtmlElement:
    return HtmlElement("dfn", **attrs)

def time(**attrs) -> HtmlElement:
    return HtmlElement("time", **attrs)

def var(**attrs) -> HtmlElement:
    return HtmlElement("var", **attrs)

def samp(**attrs) -> HtmlElement:
    return HtmlElement("samp", **attrs)

def kbd(**attrs) -> HtmlElement:
    return HtmlElement("kbd", **attrs)

def sub(**attrs) -> HtmlElement:
    return HtmlElement("sub", **attrs)

def sup(**attrs) -> HtmlElement:
    return HtmlElement("sup", **attrs)

def i(**attrs) -> HtmlElement:
    return HtmlElement("i", **attrs)

def b(**attrs) -> HtmlElement:
    return HtmlElement("b", **attrs)

def u(**attrs) -> HtmlElement:
    return HtmlElement("u", **attrs)

def s(**attrs) -> HtmlElement:
    return HtmlElement("s", **attrs)

def del_(**attrs) -> HtmlElement:
    return HtmlElement("del", **attrs)

def ins(**attrs) -> HtmlElement:
    return HtmlElement("ins", **attrs)

# ============================================
# Other
# ============================================
def noscript(**attrs) -> HtmlElement:
    return HtmlElement("noscript", **attrs)

def template(**attrs) -> HtmlElement:
    return HtmlElement("template", **attrs)

def slot(**attrs) -> HtmlElement:
    return HtmlElement("slot", **attrs)