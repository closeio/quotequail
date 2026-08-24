import lxml.html
import pytest

from quotequail._html import (
    Position,
    get_html_tree,
    render_html_tree,
    tree_line_generator,
    trim_tree_after,
    trim_tree_before,
)


def test_tree_line_generator():
    tree = get_html_tree("<div>foo <span>bar</span><br>baz</div>")
    data = list(tree_line_generator(tree))
    div = tree.xpath("div")[0]
    br = tree.xpath("div/br")[0]
    assert data == [
        ((div, Position.Begin), (br, Position.Begin), 0, "foo bar"),
        ((br, Position.End), (div, Position.End), 0, "baz"),
    ]
    data = list(tree_line_generator(tree, max_lines=1))
    div = tree.xpath("div")[0]
    br = tree.xpath("div/br")[0]
    assert data == [
        ((div, Position.Begin), (br, Position.Begin), 0, "foo bar"),
    ]

    tree = get_html_tree("<div><h1>foo</h1>bar</div>")
    data = list(tree_line_generator(tree))
    div = tree.xpath("div")[0]
    h1 = tree.xpath("div/h1")[0]
    assert data == [
        ((h1, Position.Begin), (h1, Position.End), 0, "foo"),
        ((h1, Position.End), (div, Position.End), 0, "bar"),
    ]

    tree = get_html_tree("<div><blockquote>hi</blockquote>world</div>")
    data = list(tree_line_generator(tree))
    div = tree.xpath("div")[0]
    blockquote = tree.xpath("div/blockquote")[0]
    assert data == [
        ((blockquote, Position.Begin), (blockquote, Position.End), 1, "hi"),
        ((blockquote, Position.End), (div, Position.End), 0, "world"),
    ]

    tree = get_html_tree(
        """
        <table>
            <tr><td>Subject: </td><td>the subject</td></tr>
            <tr><td>From: </td><td>from line</td></tr>
        </table>"""
    )
    data = list(tree_line_generator(tree))
    tr1, tr2 = tree.xpath("table/tr")
    assert data == [
        (
            (tr1, Position.Begin),
            (tr1, Position.End),
            0,
            "Subject: the subject",
        ),
        ((tr2, Position.Begin), (tr2, Position.End), 0, "From: from line"),
    ]


def test_trim_after():
    html = "<div>A<span>B</span>C<span>D</span>E</div>"

    tree = get_html_tree(html)
    trim_tree_after(tree.find("div/span"))
    assert render_html_tree(tree) == "<div>A<span>B</span></div>"

    tree = get_html_tree(html)
    trim_tree_after(tree.find("div/span[2]"))
    assert (
        render_html_tree(tree) == "<div>A<span>B</span>C<span>D</span></div>"
    )

    tree = get_html_tree(html)
    trim_tree_after(tree.find("div/span"), include_element=False)
    assert render_html_tree(tree) == "<div>A</div>"

    tree = get_html_tree(html)
    trim_tree_after(tree.find("div/span[2]"), include_element=False)
    assert render_html_tree(tree) == "<div>A<span>B</span>C</div>"


def test_trim_before():
    html = "<div>A<span>B</span>C<span>D</span>E</div>"

    tree = get_html_tree(html)
    trim_tree_before(tree.find("div/span"))
    assert (
        render_html_tree(tree) == "<div><span>B</span>C<span>D</span>E</div>"
    )

    tree = get_html_tree(html)
    trim_tree_before(tree.find("div/span[2]"))
    assert render_html_tree(tree) == "<div><span>D</span>E</div>"

    tree = get_html_tree(html)
    trim_tree_before(tree.find("div/span"), include_element=False)
    assert render_html_tree(tree) == "<div>C<span>D</span>E</div>"

    tree = get_html_tree(html)
    trim_tree_before(tree.find("div/span[2]"), include_element=False)
    assert render_html_tree(tree) == "<div>E</div>"


@pytest.mark.parametrize(
    ("html", "expected"),
    [
        # '@' in tag name — unescaped email-style pseudo-tag
        (
            '<div>x<addr@domain foo="bar">y</addr@domain>z</div>',
            '<div>x&lt;addr@domain foo="bar"&gt;yz</div>',
        ),
        # ':' and '"' in tag name — lxml parses <ahref="https://..."> this way
        (
            '<div>x<ahref="https://example.com">click</ahref>z</div>',
            '<div>x&lt;ahref="https: example.com"=""&gt;clickz</div>',
        ),
        # ':' and '=' in tag name — e.g. <a:b=c>
        (
            "<div>x<a:b=c>click</a:b>z</div>",
            "<div>x&lt;a:b=c&gt;clickz</div>",
        ),
    ],
)
def test_get_html_tree_flattens_malformed_tags(html, expected):
    # Tags whose names contain XPath-special or invalid characters
    # must be rendered as escaped visible text rather than roundtripped as real
    # tags,which would raise ValueError in lxml
    assert render_html_tree(get_html_tree(html)) == expected


@pytest.mark.parametrize(
    ("html", "expected"),
    [
        # Control character next to a flattened pseudo-tag
        (
            "<div><foo@bar>\x01text</foo@bar></div>",
            "<div>&lt;foo@bar&gt;text</div>",
        ),
        # Control character as a value
        (
            '<div><foo@bar baz="\x02">hi</foo@bar></div>',
            '<div>&lt;foo@bar baz=""&gt;hi</div>',
        ),
        # NULL byte and noncharacters in ordinary text.
        ("<div>a\x00b\ufffec\uffff</div>", "<div>abc</div>"),
        # Lone surrogate.
        ("<div>a\ud800b</div>", "<div>ab</div>"),
        # Email with binary garbage found in the wild.
        (
            (
                "<div><p>hi</p><e!s\ufffd@\ufffd\ufffda "
                ':\ufffd9\ufffd\x15\ufffdk\x1a\ufffd\x18\ufffd6="">'
                "after</div>"
            ),
            (
                "<div><p>hi</p>&lt;e!s\ufffd@\ufffd\ufffda "
                ':\ufffd9\ufffd\ufffdk\ufffd\ufffd6=""&gt;after</div>'
            ),
        ),
    ],
)
def test_get_html_tree_strips_xml_illegal_chars(html, expected):
    assert render_html_tree(get_html_tree(html)) == expected


def test_get_html_tree_keeps_xml_legal_whitespace():
    # Control characters inside the XML 1.0 Char production and should survive.
    tree = get_html_tree("<div>a\tb\nc</div>")
    assert tree.xpath("string()") == "a\tb\nc"


def test_get_html_tree_outlook_tag_roundtrip():
    # Outlook uses <o:p> for paragraph padding. The tag must survive the
    # get_html_tree → render_html_tree roundtrip unchanged.
    html = "<div>foo<o:p></o:p>bar</div>"
    assert (
        render_html_tree(get_html_tree(html)) == "<div>foo<o:p></o:p>bar</div>"
    )


def test_render_html_tree_suppresses_space_in_stored_tag_name():
    # Verify that if a tag name containing ':' and ' ' somehow ends up in
    # __tag_name, render_html_tree must not raise ValueError.
    tree = lxml.html.fragment_fromstring("<div><span>text</span></div>")
    span = tree.find("span")
    span.attrib["__tag_name"] = "o:p style"
    result = render_html_tree(tree)
    assert "text" in result
    assert "__tag_name" not in result
