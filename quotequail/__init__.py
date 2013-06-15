# -*- coding: utf-8 -*-
# quotequail
# a library that identifies quoted text in email messages

import re

__all__ = ['quote']

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

HEADER_MAP = {
    'from': 'from',
    'von': 'from',
    'de': 'from',

    'to': 'to',
    'an': 'to',
    'para': 'to',

    'cc': 'cc',
    'kopie': 'cc',

    'bcc': 'bcc',
    'blindkopie': 'bcc',

    'reply-to': 'reply-to',

    'date': 'date',
    'sent': 'date',
    'datum': 'date',
    'enviado el': 'date',
    'enviados': 'date',
    'fecha': 'date',

    'subject': 'subject',
    'betreff': 'subject',
    'asunto': 'subject',
}

"""
Takes a plain text message as an argument, returns a list of tuples.
The first argument of the tuple denotes whether the text should be expanded by default.
E.g. [(True, 'expanded text'), (False, 'Some quoted text')]
"""
def quote(text):
    lines = text.split('\n')

    regexes = REPLY_PATTERNS + FORWARD_PATTERNS
    
    found = None

    for n, line in enumerate(lines):
        if found != None:
            break
        for regex in regexes:
            if re.match(regex, line.strip()):
                found = n
                break

    if found != None:
        return [(True, '\n'.join(lines[:found+1])), (False, '\n'.join(lines[found+1:]))]

    return [(True, text)]


"""
If the passed text is the text body of a forwarded message, a dictionary with the following keys is returned:
- type: "reply", "forward" or "quote"
- text_top: Text at the top of the passed message (if found)
- text_bottom: Text at the bottom of the passed message (if found)
- from / to / subject / cc / bcc / reply-to: Corresponding header of the forwarded message, if it exists. (if found)
- text: Text of the forwarded message (if found)

Otherwise, this function returns None.

"""
def unwrap(text):
    result = {}

    lines = text.split('\n')

    header_re = re.compile(r'\*?([a-zA-Z- ]+):\*?(.*)$')

    pattern_map = {
        'reply': REPLY_PATTERNS,
        'forward': FORWARD_PATTERNS,
    }

    def _find_start(lines):
        """
        Find starting point of wrapped email. Returns a tuple containing
        (line_number, type) where type can be one of the following:
         * 'forward': A matching forwarding pattern was found
         * 'reply': A matching repy pattern was found
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
            for typ, regexes in pattern_map.iteritems():
                for regex in regexes:
                    if re.match(regex, line.strip()):
                        return n, typ

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
        for n, line in enumerate(lines):
            if not line.strip():
                continue

            match = header_re.match(line)
            if match:
                header_name, header_value = match.groups()
                header_name = header_name.strip().lower()

                if header_name in HEADER_MAP:
                    hdrs[HEADER_MAP[header_name]] = header_value.strip()
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
