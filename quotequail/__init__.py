# -*- coding: utf-8 -*-
# quotequail
# a library that identifies quoted text in email messages

import re

__all__ = ['quote', 'quote_html']

# Amount to lines to join to check for potential wrapped patterns.
MAX_WRAP_LINES = 2

REPLY_PATTERNS = [
    '^On .*wrote:$', # apple mail/gmail reply
    '^Am .*schrieb .*:$', # German
    '[0-9]{4}/[0-9]{1,2}/[0-9]{1,2} .* <.*@.*>$', # gmail (?) reply
]

FORWARD_MESSAGES = [
    # apple mail forward
    'Begin forwarded message', 'Anfang der weitergeleiteten E-Mail',

    # gmail/evolution forward
    'Forwarded [mM]essage',

    # outlook
    'Original [mM]essage', 'Ursprüngliche Nachricht', 'Mensaje [oO]riginal',
]

FORWARD_PATTERNS = [
    '^________________________________$', # yahoo?
] + ['^---+ ?%s ?---+$' % p for p in FORWARD_MESSAGES] \
  + ['^%s:$' % p for p in FORWARD_MESSAGES]

FORWARD_STYLES = [
    # Outlook
    'border:none;border-top:solid #B5C4DF 1.0pt;padding:3.0pt 0in 0in 0in',
]

HEADER_MAP = {
    'from': 'from',
    'von': 'from',
    'de': 'from',

    'to': 'to',
    'an': 'to',
    'para': 'to',
    u'à': 'to',

    'cc': 'cc',
    'kopie': 'cc',

    'bcc': 'bcc',
    'blindkopie': 'bcc',

    'reply-to': 'reply-to',
    u'répondre à': 'reply-to',

    'date': 'date',
    'sent': 'date',
    'datum': 'date',
    'enviado el': 'date',
    'enviados': 'date',
    'fecha': 'date',

    'subject': 'subject',
    'betreff': 'subject',
    'asunto': 'subject',
    'objet': 'subject',
}

COMPILED_PATTERNS = [re.compile(regex) for regex in REPLY_PATTERNS + FORWARD_PATTERNS ]

def quote(text, limit=1000):
    """
    Takes a plain text message as an argument, returns a list of tuples. The
    first argument of the tuple denotes whether the text should be expanded by
    default. E.g. [(True, 'expanded text'), (False, 'Some quoted text')]

    Unless the limit param is set to None, the text will automatically be quoted
    starting at the line where the limit is reached.
    """

    lines = text.split('\n')

    found = None

    def _find():
        for n in range(len(lines)):
            for regex in COMPILED_PATTERNS:
                for m in range(MAX_WRAP_LINES):
                    match_line = ''.join(lines[n:n+1+m])
                    if match_line.startswith('>'):
                        match_line = match_line[1:].strip()
                    if re.match(regex, match_line.strip()):
                        return n+m
            if n == limit:
                return n

    found = _find()

    if found != None:
        return [(True, '\n'.join(lines[:found+1])), (False, '\n'.join(lines[found+1:]))]

    return [(True, text)]

def quote_html(html, limit=10000):
    """
    Like quote(), but takes an HTML message as an argument. The limit param
    represents the maximum number of tags to traverse until quoting the rest
    of the markup.
    """
    import lxml.html
    INLINE_TAGS = ['a', 'b', 'em', 'i', 'strong', 'span', 'font', 'q',
                   'object', 'bdo', 'sub', 'sup', 'center']

    def _get_inline_texts(root):
        """
        For a given tag, returns a list of text content by including inline
        tags (and the corresponding insertion index at the end of the text).
        E.g. '<a>x@y.com</a> wrote: <div>anything</div> more text' will
        return [(1, 'x@y.com wrote: '), (3, ' more text')]
        """
        texts = []
        # Text at the beginning of the element which preceeds any other text
        # e.g. '<div>A<a>B</a>C</div>' will return 'A'
        text = root.text or u''
        idx = 0
        for el in root:
            # Need to check if it's a string because comments point to
            # lxml.etree.Comment
            if isinstance(el.tag, basestring) and el.tag.lower() in INLINE_TAGS:
                # For inline tags, append their text content and tail
                # E.g. '<a>B</a>C' will return 'BC'
                text += el.text_content()
                if el.tail:
                    text += el.tail
            else:
                if text:
                    texts.append((idx, text))
                    text = u''
                # For other tags, just use their tail.
                # E.g. '<div>D</div>E' will return 'E'
                if el.tail:
                    text += el.tail

            idx += 1

        if text:
            texts.append((idx, text))

        return texts

    def _insert_quotequail_divider():
        """
        Inserts a quotequail divider div if a pattern is found and returns the
        parent element chain. Returns None if no pattern was found.
        """
        quail_el = lxml.html.Element('div', **{'class': 'quotequail-divider'})

        def _get_parent_chain():
            parent_chain = []
            for parent_el in quail_el.iterancestors():
                parent_chain.append(parent_el)
                if parent_el == tree:
                    break
            return parent_chain

        for n, el in enumerate(tree.iter()):
            style = el.attrib.get('style')
            if style in FORWARD_STYLES:
                el.insert(0, quail_el)
                return _get_parent_chain()
            else:
                for text_idx, text in _get_inline_texts(el):
                    for regex in COMPILED_PATTERNS:
                        if re.match(regex, text.strip()):
                            # Insert quotequail divider *after* the text.
                            # If the index is past the last element, insert it
                            # after the parent element to prevent an orphan tag.
                            # For example, '<p>X wrote:</p><div>text</div>' is
                            # divided into '<p>X wrote:</p>' and '<div>text</div>',
                            # and not '<p>X wrote:</p>' and '<p></p><div>text</div>'
                            if text_idx == len(el):
                                el.addnext(quail_el)
                                el = el.getparent()
                            else:
                                el.insert(text_idx, quail_el)

                            return _get_parent_chain()

            if n == limit:
                el.addnext(quail_el)
                return _get_parent_chain()

    def _strip_wrapping(text):
        if text.startswith('<div>') and text.endswith('</div>'):
            text = text[5:-6]
        return text

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
        html = '<div>%s</div>' % html
        tree = lxml.html.fromstring(html, parser=parser)

    parent_chain = _insert_quotequail_divider() or []

    rendered_tree = lxml.html.tostring(tree)
    parts = rendered_tree.split('<div class="quotequail-divider"></div>')

    if len(parts) == 1:
        return [(True, _strip_wrapping(rendered_tree))]
    else:
        def render_attrs(el):
            return ' '.join('%s="%s"' % (name, val)
                    for name, val in el.attrib.items())

        # Render open tags and attributes (but no content)
        open_sequence = ''.join(['<%s%s%s>' % (el.tag, ' ' if el.attrib else '',
            render_attrs(el)) for el in reversed(parent_chain)])

        close_sequence = ''.join(['</%s>' % el.tag for el in parent_chain])

        return [
            (True, _strip_wrapping(parts[0]+close_sequence)),
            (False, _strip_wrapping(open_sequence+parts[1])),
        ]

def unwrap(text):
    """
    If the passed text is the text body of a forwarded message, a dictionary
    with the following keys is returned:

    - type: "reply", "forward" or "quote"
    - text_top: Text at the top of the passed message (if found)
    - text_bottom: Text at the bottom of the passed message (if found)
    - from / to / subject / cc / bcc / reply-to: Corresponding header of the
      forwarded message, if it exists. (if found)
    - text: Text of the forwarded message (if found)

    Otherwise, this function returns None.
    """

    result = {}

    lines = text.split('\n')

    header_re = re.compile(r'\*?([-\w ]+):\*?(.*)$', re.UNICODE)

    pattern_map = {
        'reply': REPLY_PATTERNS,
        'forward': FORWARD_PATTERNS,
    }

    def _find_start(lines):
        """
        Find starting point of wrapped email. Returns a tuple containing
        (line_number, type) where type can be one of the following:
         * 'forward': A matching forwarding pattern was found
         * 'reply': A matching reply pattern was found
         * 'headers': Headers were found (usually a forwarded email)
         * 'quote': A quote was found
        Returns (None, None) if nothing was found.
        """

        # minimum number of headers that we recognize
        _min_headers = 2

        # minimum number of lines to recognize a quoted block
        _min_quoted = 3

        for n, line in enumerate(lines):
            if not line.strip():
                continue

            # Find a forward / reply start pattern
            for typ, regexes in pattern_map.items():
                for regex in regexes:
                    for m in range(MAX_WRAP_LINES):
                        match_line = ''.join(lines[n:n+1+m])
                        if match_line.startswith('>'):
                            match_line = match_line[1:].strip()
                        if re.match(regex, match_line.strip()):
                            return n+m, typ

            # Find a quote
            if line.startswith('>'):
                # Check if there are at least _min_quoted lines  that match
                matched_lines = 1
                for line in lines[n+1:]:
                    if not line.strip():
                        continue
                    if not line.startswith('>'):
                        break
                    else:
                        matched_lines += 1
                    if matched_lines == _min_quoted:
                        return n, 'quoted'

            # Find a header
            match = header_re.match(line)
            if match:
                if len(_extract_headers(lines[n:])[0]) >= _min_headers:
                    return n, 'headers'

        return None, None

    def _unindent(lines):
        unquoted = []
        for n, line in enumerate(lines):
            if line.startswith('> '):
                unquoted.append(line[2:])
            elif line.startswith('>'):
                unquoted.append(line[1:])
            else:
                break

        return unquoted, lines[n:]

    def _extract_headers(lines):
        hdrs = {}
        header_name = None

        # Track overlong headers that extend over multiple lines
        extend_lines = 0

        for n, line in enumerate(lines):
            if not line.strip():
                header_name = None
                continue

            match = header_re.match(line)
            if match:
                header_name, header_value = match.groups()
                header_name = header_name.strip().lower()
                extend_lines = 0

                if header_name in HEADER_MAP:
                    hdrs[HEADER_MAP[header_name]] = header_value.strip()
            else:
                extend_lines += 1
                if extend_lines < MAX_WRAP_LINES and header_name in HEADER_MAP:
                    hdrs[HEADER_MAP[header_name]] = ' '.join([hdrs[HEADER_MAP[header_name]], line.strip()]).strip()
                else:
                    # no more headers found
                    break

        return hdrs, lines[n:]

    def _unwrap(lines):
        start, typ = _find_start(lines)
        if typ in ('forward', 'reply'):
            main_type = typ
            start2, typ = _find_start(lines[start+1:])

            if typ == 'quoted':
                unquoted, rest = _unindent(lines[start+1+start2:])
                start3, typ = _find_start(unquoted)
                if typ == 'headers':
                    hdrs, rest2 = _extract_headers(unquoted[start3:])
                    return main_type, lines[:start], hdrs, rest2, rest
                else:
                    return main_type, lines[:start], None, unquoted, rest
            elif typ == 'headers':
                hdrs, rest = _extract_headers(lines[start+1:])
                return main_type, lines[:start], hdrs, rest, []
            else:
                return main_type, lines[:start], None, lines[start+(start2 or 0)+1:], []

        elif typ == 'headers':
            main_type = 'forward'
            hdrs, rest = _extract_headers(lines[start:])
            return main_type, lines[:start], hdrs, rest, ''

        elif typ == 'quoted':
            unquoted, rest = _unindent(lines[start:])
            start2, typ = _find_start(unquoted)
            if typ == 'headers':
                main_type = 'forward'
                hdrs, rest2 = _extract_headers(unquoted[start2:])
                return main_type, lines[:start], hdrs, rest2, rest
            else:
                main_type = 'quote'
                return main_type, lines[:start], None, unquoted, rest


    result = _unwrap(lines)
    if result:
        typ, text_top, hdrs, text, text_bottom = result

        result = {
            'type': typ,
        }

        text = '\n'.join(text).strip()
        text_top = '\n'.join(text_top).strip()
        text_bottom = '\n'.join(text_bottom).strip()

        if text:
            result['text'] = text
        if text_top:
            result['text_top'] = text_top
        if text_bottom:
            result['text_bottom'] = text_bottom

        if hdrs:
            result.update(hdrs)

        return result
