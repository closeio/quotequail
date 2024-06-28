# quotequail
# a library that identifies quoted text in email messages

from . import _internal, _patterns

__version__ = "0.3.0"
__all__ = ["quote", "quote_html", "unwrap", "unwrap_html"]


def quote(text: str, limit: int = 1000) -> list[tuple[bool, str]]:
    """
    Take a plain text message as an argument, return a list of tuples. The
    first argument of the tuple denotes whether the text should be expanded by
    default. The second argument is the unmodified corresponding text.

    Example: [(True, 'expanded text'), (False, '> Some quoted text')]

    Unless the limit param is set to None, the text will automatically be
    quoted starting at the line where the limit is reached.
    """
    lines = text.split("\n")

    found = _internal.find_quote_position(
        lines, _patterns.MAX_WRAP_LINES, limit
    )

    if found is not None:
        return [
            (True, "\n".join(lines[: found + 1])),
            (False, "\n".join(lines[found + 1 :])),
        ]

    return [(True, text)]


def quote_html(html: str, limit: int = 1000) -> list[tuple[bool, str]]:
    """
    Like quote(), but takes an HTML message as an argument. The limit param
    represents the maximum number of lines to traverse until quoting the rest
    of the markup. Lines are separated by block elements or <br>.
    """
    from . import _html

    tree = _html.get_html_tree(html)

    start_refs, end_refs, lines = _html.get_line_info(tree, limit + 1)

    found = _internal.find_quote_position(lines, 1, limit)

    if found is None:
        # No quoting found and we're below limit. We're done.
        return [(True, _html.render_html_tree(tree))]

    start_tree = _html.slice_tree(
        tree, start_refs, end_refs, (0, found + 1), html_copy=html
    )
    end_tree = _html.slice_tree(tree, start_refs, end_refs, (found + 1, None))

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

    if unwrap_result:
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
