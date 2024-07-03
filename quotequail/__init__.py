# quotequail
# a library that identifies quoted text in email messages

from . import _internal, _patterns
from ._enums import Position

__version__ = "0.4.0"
__all__ = ["quote", "quote_html", "unwrap", "unwrap_html"]


def quote(
    text: str, *, limit: int = 1000, quote_intro_line: bool = False
) -> list[tuple[bool, str]]:
    """
    Divide email body into quoted parts.

    Args:
        text: Plain text message.
        limit: If set, the text will automatically be quoted starting at the
            line where the limit is reached.
        quote_intro_line: Whether the line introducing the quoted text ("On ...
            wrote:" / "Begin forwarded message:") should be part of the quoted
            text.

    Returns:
        List of tuples: The first argument of the tuple denotes whether the
        text should be expanded by default. The second argument is the
        unmodified corresponding text.

        Example: [(True, 'expanded text'), (False, '> Some quoted text')]
    """
    lines = text.split("\n")

    position = Position.Begin if quote_intro_line else Position.End
    found = _internal.find_quote_position(
        lines,
        _patterns.MAX_WRAP_LINES,
        limit=limit,
        position=position,
    )

    if found is None:
        return [(True, text)]

    split_idx = found if quote_intro_line else found + 1
    return [
        (True, "\n".join(lines[:split_idx])),
        (False, "\n".join(lines[split_idx:])),
    ]


def quote_html(
    html: str, *, limit: int = 1000, quote_intro_line: bool = False
) -> list[tuple[bool, str]]:
    """
    Like quote(), but takes an HTML message as an argument.

    Args:
        html: HTML message.
        limit: Maximum number of lines to traverse until quoting the rest of
            the markup. Lines are separated by block elements or <br>.
        quote_intro_line: Whether the line introducing the quoted text ("On ...
            wrote:" / "Begin forwarded message:") should be part of the quoted
            text.
    """
    from . import _html

    tree = _html.get_html_tree(html)

    start_refs, end_refs, lines = _html.get_line_info(tree, limit + 1)

    position = Position.Begin if quote_intro_line else Position.End
    found = _internal.find_quote_position(
        lines, 1, limit=limit, position=position
    )

    if found is None:
        # No quoting found and we're below limit. We're done.
        return [(True, _html.render_html_tree(tree))]

    split_idx = found if quote_intro_line else found + 1
    start_tree = _html.slice_tree(
        tree, start_refs, end_refs, (0, split_idx), html_copy=html
    )
    end_tree = _html.slice_tree(tree, start_refs, end_refs, (split_idx, None))

    return [
        (True, _html.render_html_tree(start_tree)),
        (False, _html.render_html_tree(end_tree)),
    ]


def unwrap(text: str) -> dict[str, str] | None:
    """
    If the passed text is the text body of a forwarded message, a reply, or
    contains quoted text, a dictionary with the following keys is returned:

    - type: "reply", "forward" or "quote"
    - text_top: Text at the top of the passed message (if found)
    - text_bottom: Text at the bottom of the passed message (if found)
    - from / to / subject / cc / bcc / reply-to: Corresponding header of the
      forwarded message, if it exists. (if found)
    - text: Unindented text of the wrapped message (if found)

    Otherwise, this function returns None.
    """
    lines = text.split("\n")

    unwrap_result = _internal.unwrap(
        lines,
        _patterns.MAX_WRAP_LINES,
        _patterns.MIN_HEADER_LINES,
        _patterns.MIN_QUOTED_LINES,
    )
    if not unwrap_result:
        return None

    typ, top_range, hdrs, main_range, bottom_range, needs_unindent = (
        unwrap_result
    )

    text_top_lines = lines[slice(*top_range)] if top_range else []
    text_lines = lines[slice(*main_range)] if main_range else []
    text_bottom_lines = lines[slice(*bottom_range)] if bottom_range else []

    if needs_unindent:
        text_lines = _internal.unindent_lines(text_lines)

    result = {
        "type": typ,
    }

    text = "\n".join(text_lines).strip()
    text_top = "\n".join(text_top_lines).strip()
    text_bottom = "\n".join(text_bottom_lines).strip()

    if text:
        result["text"] = text
    if text_top:
        result["text_top"] = text_top
    if text_bottom:
        result["text_bottom"] = text_bottom

    if hdrs:
        result.update(hdrs)

    return result


def unwrap_html(html: str) -> dict[str, str] | None:
    """
    If the passed HTML is the HTML body of a forwarded message, a dictionary
    with the following keys is returned:

    - type: "reply", "forward" or "quote"
    - html_top: HTML at the top of the passed message (if found)
    - html_bottom: HTML at the bottom of the passed message (if found)
    - from / to / subject / cc / bcc / reply-to: Corresponding header of the
      forwarded message, if it exists. (if found)
    - html: HTML of the forwarded message (if found)

    Otherwise, this function returns None.
    """
    from . import _html

    tree = _html.get_html_tree(html)

    start_refs, end_refs, lines = _html.get_line_info(tree)

    unwrap_result = _internal.unwrap(lines, 1, _patterns.MIN_HEADER_LINES, 1)

    if not unwrap_result:
        return None

    typ, top_range, hdrs, main_range, bottom_range, needs_unindent = (
        unwrap_result
    )

    result = {
        "type": typ,
    }

    top_range_slice = _html.trim_slice(lines, top_range)
    main_range_slice = _html.trim_slice(lines, main_range)
    bottom_range_slice = _html.trim_slice(lines, bottom_range)

    if top_range_slice:
        top_tree = _html.slice_tree(
            tree, start_refs, end_refs, top_range_slice, html_copy=html
        )
        html_top = _html.render_html_tree(top_tree)
        if html_top:
            result["html_top"] = html_top

    if bottom_range_slice:
        bottom_tree = _html.slice_tree(
            tree, start_refs, end_refs, bottom_range_slice, html_copy=html
        )
        html_bottom = _html.render_html_tree(bottom_tree)
        if html_bottom:
            result["html_bottom"] = html_bottom

    if main_range_slice:
        main_tree = _html.slice_tree(
            tree, start_refs, end_refs, main_range_slice
        )
        if needs_unindent:
            _html.unindent_tree(main_tree)
        html = _html.render_html_tree(main_tree)
        if html:
            result["html"] = html

    if hdrs:
        result.update(hdrs)

    return result
