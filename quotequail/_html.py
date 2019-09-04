# HTML utils

import lxml.html
import lxml.etree

from ._patterns import FORWARD_LINE, FORWARD_STYLES, MULTIPLE_WHITESPACE_RE

INLINE_TAGS = ['a', 'b', 'em', 'i', 'strong', 'span', 'font', 'q',
               'object', 'bdo', 'sub', 'sup', 'center', 'td', 'th']
# replaced by binary data, so should be preserved in HTML no matter the text
# around it.
REPLACED_TAGS = ['img']

BEGIN = 'begin'
END = 'end'

try:
    string_class = basestring # Python 2.7
except NameError:
    string_class = str # Python 3.x

def trim_tree_after(element, include_element=True):
    """
    Removes the document tree following the given element. If include_element
    is True, the given element is kept in the tree, otherwise it is removed.
    """
    el = element
    for parent_el in element.iterancestors():
        el.tail = None
        if el != element or include_element:
            el = el.getnext()
        while el is not None:
            remove_el = el
            el = el.getnext()
            parent_el.remove(remove_el)
        el = parent_el

def trim_tree_before(element, include_element=True, keep_head=True):
    """
    Removes the document tree preceding the given element. If include_element
    is True, the given element is kept in the tree, otherwise it is removed.
    """
    el = element
    for parent_el in element.iterancestors():
        parent_el.text = None
        if el != element or include_element:
            el = el.getprevious()
        else:
            parent_el.text = el.tail
        while el is not None:
            remove_el = el
            el = el.getprevious()
            tag = remove_el.tag
            is_head = isinstance(tag, string_class) and tag.lower() == 'head'
            if not keep_head or not is_head:
                parent_el.remove(remove_el)
        el = parent_el

def is_replaced(el):
    return (
        isinstance(el.tag, string_class) and
        el.tag.lower() in REPLACED_TAGS
    )

def trim_slice(lines, slice_tuple, start_refs, end_refs):
    """
    Trim a slice tuple (begin, end) so it starts at the first non-empty line
    (obtained via indented_tree_line_generator / get_line_info) and ends at the
    last non-empty line within the slice. Returns the new slice.
    """
    def _empty(line):
        return not line or line.strip() == '>'

    if not slice_tuple:
        return None

    slice_start, slice_end = slice_tuple

    if slice_start is None:
        slice_start = 0
    if slice_end is None:
        slice_end = len(lines)

    # Trim from beginning
    while (slice_start < slice_end and
           _empty(lines[slice_start]) and
           not is_replaced(start_refs[slice_start][0])):
        slice_start += 1

    # Trim from end
    while (slice_end > slice_start and
           _empty(lines[slice_end-1]) and
           not is_replaced(end_refs[slice_end-1][0])):
        slice_end -= 1

    return (slice_start, slice_end)

def unindent_tree(element):
    """
    Removes the outermost indent. For example, the tree
    "<div>A<blockqote>B<div>C<blockquote>D</blockquote>E</div>F</blockquote>G</div>"
    is transformed to
    "<div>A<div>B<div>C<blockquote>D</blockquote>E</div>F</div>G</div>"
    """
    for el in element.iter():
        if is_indentation_element(el):
            el.attrib.clear()
            el.tag = 'div'
            return

def slice_tree(tree, start_refs, end_refs, slice_tuple, html_copy=None):
    """
    Slices the HTML tree with the given start_refs and end_refs (obtained via
    get_line_info) at the given slice_tuple, a tuple (start, end) containing
    the start and end of the slice (or None, to start from the start / end at
    the end of the tree). If html_copy is specified, a new tree is constructed
    from the given HTML (which must be the equal to the original tree's HTML*).
    The resulting tree is returned.

    *) The reason we have to specify the HTML is that we can't reliably
       construct a copy of the tree using copy.copy() (see bug
       https://bugs.launchpad.net/lxml/+bug/1562550).
    """

    start_ref = None
    end_ref = None

    if slice_tuple:
        slice_start, slice_end = slice_tuple

        if ((slice_start is not None and slice_start >= len(start_refs)) or
            (slice_end is not None and slice_end <= 0)):
            return get_html_tree('')

        if slice_start != None and slice_start <= 0:
            slice_start = None

        if slice_end != None and slice_end >= len(start_refs):
            slice_end = None
    else:
        slice_start, slice_end = None, None

    if slice_start is not None:
        start_ref = start_refs[slice_start]

    if slice_end is not None:
        if slice_end < len(end_refs):
            end_ref = end_refs[slice_end-1]

    if html_copy is not None:
        et = lxml.etree.ElementTree(tree)

        new_tree = get_html_tree(html_copy)

        if start_ref:
            selector = et.getelementpath(start_ref[0])
            start_ref = (new_tree.find(selector), start_ref[1])

        if end_ref:
            selector = et.getelementpath(end_ref[0])
            end_ref = (new_tree.find(selector), end_ref[1])

    else:
        new_tree = tree

    if start_ref:
        include_start = (start_ref[1] == BEGIN or is_replaced(start_ref[0]))
    if end_ref:
        include_end = (end_ref[1] == END or is_replaced(end_ref[0]))

    # If start_ref is the same as end_ref, and we don't include the element,
    # we are removing the entire tree. We need to handle this separately,
    # otherwise trim_tree_after won't work because it can't find the already
    # removed reference.
    if start_ref and end_ref and start_ref[0] == end_ref[0]:
        if not include_start or not include_end:
            return get_html_tree('')

    if start_ref:
        trim_tree_before(start_ref[0], include_element=include_start)
    if end_ref:
        trim_tree_after(end_ref[0], include_element=include_end)

    return new_tree

def get_html_tree(html):
    """
    Given the HTML string, returns a LXML tree object. The tree is wrapped in
    <div> elements if it doesn't have a top level tag or parsing would
    otherwise result in an error. The wrapping can be later removed with
    strip_wrapping().
    """

    parser = lxml.html.HTMLParser(encoding='utf-8')
    html = html.encode('utf8')

    try:
        tree = lxml.html.fromstring(html, parser=parser)
    except lxml.etree.Error:
        # E.g. empty document. Use dummy <div>
        tree = lxml.html.fromstring('<div></div>')

    # If the document doesn't start with a top level tag, wrap it with a <div>
    # that will be later stripped out for consistent behavior.
    if tree.tag not in lxml.html.defs.top_level_tags:
        html = b'<div>%s</div>' % html
        tree = lxml.html.fromstring(html, parser=parser)

    # HACK for Outlook emails, where tags like <o:p> are rendered as <p>. We
    # can generally ignore these tags so we replace them with <span>, which
    # doesn't cause a line break. Also, we can't look up the element path of
    # tags that contain colons. When rendering the tree, we will restore the
    # tag name.
    for el in tree.iter():
        if el.nsmap or (isinstance(el.tag, string_class) and ':' in el.tag):
            if el.nsmap:
                actual_tag_name = '{}:{}'.format(list(el.nsmap.keys())[0], el.tag)
            else:
                actual_tag_name = el.tag
            el.tag = 'span'
            el.attrib['__tag_name'] = actual_tag_name

    return tree

def strip_wrapping(html):
    """
    Removes the wrapping that might have resulted when using get_html_tree().
    """
    if html.startswith('<div>') and html.endswith('</div>'):
        html = html[5:-6]
    return html.strip()

def render_html_tree(tree):
    """
    Renders the given HTML tree, and strips any wrapping that was applied in
    get_html_tree().

    You should avoid further processing of the given tree after calling this
    method because we modify namespaced tags here.
    """

    # Restore any tag names that were changed in get_html_tree()
    for el in tree.iter():
        if '__tag_name' in el.attrib:
            actual_tag_name = el.attrib.pop('__tag_name')
            el.tag = actual_tag_name

    html = lxml.html.tostring(tree, encoding='utf8').decode('utf8')

    return strip_wrapping(html)

def is_indentation_element(element):
    if isinstance(element.tag, string_class):
        return element.tag.lower() == 'blockquote'
    return False

def tree_token_generator(el, indentation_level=0):
    """
    Internal generator that yields tokens for the given HTML element as
    follows:

    - A tuple (LXML element, BEGIN, indentation_level)
    - Text right after the start of the tag, or None.
    - Recursively calls the token generator for all child objects
    - A tuple (LXML element, END, indentation_level)
    - Text right after the end of the tag, or None.
    """

    if not isinstance(el.tag, string_class):
        return

    tag_name = el.tag.lower()

    is_indentation = is_indentation_element(el)

    if is_indentation:
        indentation_level += 1

    yield (el, BEGIN, indentation_level)

    yield el.text

    for child in el.iterchildren():
        for token in tree_token_generator(child, indentation_level):
            yield token

    if is_indentation:
        indentation_level -= 1

    yield (el, END, indentation_level)

    yield el.tail

def tree_line_generator(el, max_lines=None):
    """
    Internal generator that iterates through an LXML tree and yields a tuple
    per line. In this context, lines are blocks of text separated by <br> tags
    or by block elements. The tuples contain the following elements:

    - A tuple with the element reference (element, position) for the start
      of the line. The tuple consists of:
        - The LXML HTML element which references the line
        - Whether the text starts at the beginning of the referenced element,
          or after the closing tag
    - A similar tuple indicating the ending of the line.
    - The email indentation level, if detected.
    - The plain (non-HTML) text of the line

    If max_lines is specified, the generator stops after yielding the given
    amount of lines.

    For example, the HTML tree "<div>foo <span>bar</span><br>baz</div>" yields:

    - ((<Element div>, 'begin'), (<Element br>, 'begin'), 0, 'foo bar')
    - ((<Element br>, 'end'), (<Element div>, 'end'), 0, 'baz').

    To illustrate the indentation level, the HTML tree
    '<div><blockquote>hi</blockquote>world</div>' yields:

    - ((<Element blockquote>, 'begin'), (<Element blockquote>, 'end'), 1, 'hi')
    - ((<Element blockquote>, 'end'), (<Element div>, 'end'), 0, 'world')
    """

    def _trim_spaces(text):
        return MULTIPLE_WHITESPACE_RE.sub(' ', text).strip()

    counter = 1
    if max_lines != None and counter > max_lines:
        return

    # Buffer for the current line.
    line = ''

    # The reference tuple (element, position) for the start of the line.
    start_ref = None

    # The indentation level at the start of the line.
    start_indentation_level = None

    for token in tree_token_generator(el):
        if token is None:
            continue

        elif isinstance(token, tuple):
            el, state, indentation_level = token

            tag_name = el.tag.lower()

            line_break = (tag_name == 'br' and state == BEGIN)
            is_block = (tag_name not in INLINE_TAGS)
            is_forward = (is_block and state == BEGIN and
                          el.attrib.get('style') in FORWARD_STYLES)

            if is_block or line_break:
                line = _trim_spaces(line)

                if line or line_break or is_forward:
                    end_ref = (el, state)
                    yield start_ref, end_ref, start_indentation_level, line
                    counter += 1
                    if max_lines != None and counter > max_lines:
                        return
                    line = ''

                    if is_forward:
                        # Simulate forward
                        yield (end_ref, end_ref, start_indentation_level,
                               FORWARD_LINE)
                        counter += 1
                        if max_lines != None and counter > max_lines:
                            return

                if not line:
                    start_ref = (el, state)
                    start_indentation_level = indentation_level

        elif isinstance(token, string_class):
            line += token

        else:
            raise RuntimeError('invalid token: {}'.format(token))

    line = _trim_spaces(line)
    if line:
        yield line

def indented_tree_line_generator(el, max_lines=None):
    """
    Like tree_line_generator, but yields tuples (start_ref, end_ref, line),
    where the line already takes the indentation into account by having "> "
    prepended. If a line already starts with ">", it is escaped ("\\>"). This
    makes it possible to reliably use methods that analyze plain text to detect
    quoting.
    """
    gen = tree_line_generator(el, max_lines)
    for start_ref, end_ref, indentation_level, line in gen:
        # Escape line
        if line.startswith('>'):
            line = '\\' + line
        yield start_ref, end_ref, '> '*indentation_level + line

def get_line_info(tree, max_lines=None):
    """
    Shortcut for indented_tree_line_generator() that returns an array of
    start references, an array of corresponding end references (see
    tree_line_generator() docs), and an array of corresponding lines.
    """
    line_gen = indented_tree_line_generator(tree, max_lines=max_lines)
    line_gen_result = list(zip(*line_gen))
    if line_gen_result:
        return line_gen_result
    else:
        return [], [], []
