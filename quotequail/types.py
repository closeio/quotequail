from typing import TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:
    from lxml.html import HtmlElement

Element: TypeAlias = "HtmlElement"
ElementRef = tuple["Element", str]
