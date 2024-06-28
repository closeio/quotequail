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
