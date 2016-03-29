import re

import re
from ._patterns import COMPILED_PATTERNS, COMPILED_PATTERN_MAP, HEADER_RE, HEADER_MAP

"""
Internal methods. For max_wrap_lines, min_header_lines, min_quoted_lines
documentation see the corresponding constants in _patterns.py.
"""

def find_pattern_on_line(lines, n, max_wrap_lines):
    """
    Finds a forward/reply pattern within the given lines on text on the given
    line number and returns a tuple with the type ('reply' or 'forward') and
    line number of where the pattern ends. The returned line number may be
    different from the given line number in case the pattern wraps over
    multiple lines.
    """
    for typ, regexes in COMPILED_PATTERN_MAP.items():
        for regex in regexes:
            for m in range(max_wrap_lines):
                match_line = ''.join(lines[n:n+1+m])
                if match_line.startswith('>'):
                    match_line = match_line[1:].strip()
                if re.match(regex, match_line.strip()):
                    return n+m, typ

def find_quote_position(lines, max_wrap_lines, limit=None):
    """
    Returns the (ending) line number of a quoting pattern. If a limit is given
    and the limit is reached, the limit is returned.
    """

    for n in range(len(lines)):
        result = find_pattern_on_line(lines, n, max_wrap_lines)
        if result:
            return result[0]
        if limit != None and n >= limit-1:
            return n

    return None

def extract_headers(lines, max_wrap_lines):
    """
    Extracts email headers from the given lines. Returns a dict with the
    detected headers and the amount of lines that were processed.
    """
    hdrs = {}
    header_name = None

    # Track overlong headers that extend over multiple lines
    extend_lines = 0

    for n, line in enumerate(lines):
        if not line.strip():
            header_name = None
            continue

        match = HEADER_RE.match(line)
        if match:
            header_name, header_value = match.groups()
            header_name = header_name.strip().lower()
            extend_lines = 0

            if header_name in HEADER_MAP:
                hdrs[HEADER_MAP[header_name]] = header_value.strip()
        else:
            extend_lines += 1
            if extend_lines < max_wrap_lines and header_name in HEADER_MAP:
                hdrs[HEADER_MAP[header_name]] = ' '.join([hdrs[HEADER_MAP[header_name]], line.strip()]).strip()
            else:
                # no more headers found
                break

    return hdrs, n

def find_unwrap_start(lines, max_wrap_lines, min_header_lines, min_quoted_lines):
    """
    Find starting point of wrapped email. Returns a tuple containing
    (line_number, type) where type can be one of the following:
     * 'forward': A matching forwarding pattern was found
     * 'reply': A matching reply pattern was found
     * 'headers': Headers were found (usually a forwarded email)
     * 'quote': A quote was found
    Returns (None, None) if nothing was found.
    """

    for n, line in enumerate(lines):
        if not line.strip():
            continue

        # Find a forward / reply start pattern
        result = find_pattern_on_line(lines, n, max_wrap_lines)
        if result:
            return result

        # Find a quote
        if line.startswith('>'):
            # Check if there are at least min_quoted_lines lines that match
            matched_lines = 1

            if matched_lines >= min_quoted_lines:
                return n, 'quoted'

            for peek_line in lines[n+1:]:
                if not peek_line.strip():
                    continue
                if not peek_line.startswith('>'):
                    break
                else:
                    matched_lines += 1
                if matched_lines >= min_quoted_lines:
                    return n, 'quoted'

        # Find a header
        match = HEADER_RE.match(line)
        if match:
            if len(extract_headers(lines[n:], max_wrap_lines)[0]) >= min_header_lines:
                return n, 'headers'

    return None, None


def unindent_lines(lines):
    unquoted = []
    for n, line in enumerate(lines):
        if line.startswith('> '):
            unquoted.append(line[2:])
        elif line.startswith('>'):
            unquoted.append(line[1:])
        else:
            break

    return unquoted

def unwrap(lines, max_wrap_lines, min_header_lines, min_quoted_lines):
    """
    Returns a tuple of:
    - Type ('forward', 'reply', 'headers', 'quoted')
    - Range of the text at the top of the wrapped message (or None)
    - Headers dict (or None)
    - Range of the text of the wrapped message (or None)
    - Range of the text below the wrapped message (or None)
    - Whether the wrapped text needs to be unindented
    """
    # Get line number and wrapping type.
    start, typ = find_unwrap_start(lines, max_wrap_lines, min_header_lines, min_quoted_lines)

    # We found a line indicating that it's a forward/reply.
    if typ in ('forward', 'reply'):
        main_type = typ

        # Find where the headers or the quoted section starts.
        start2, typ = find_unwrap_start(lines[start+1:], max_wrap_lines, min_header_lines, min_quoted_lines)

        if typ == 'quoted':
            # Quoted section starts. Unindent and check if there are headers.
            quoted_start = start+1+start2
            unquoted = unindent_lines(lines[quoted_start:])
            rest_start = quoted_start + len(unquoted)
            start3, typ = find_unwrap_start(unquoted, max_wrap_lines, min_header_lines, min_quoted_lines)
            if typ == 'headers':
                hdrs, hdrs_length = extract_headers(unquoted[start3:], max_wrap_lines)
                #return main_type, lines[:start], hdrs, rest2, rest
                rest2_start = quoted_start+start3+hdrs_length
                return main_type, (0, start), hdrs, (rest2_start, rest_start), (rest_start, None), True
            else:
                return main_type, (0, start), None, (quoted_start, rest_start), (rest_start, None), True

        elif typ == 'headers':
            hdrs, hdrs_length = extract_headers(lines[start+1:], max_wrap_lines)
            rest_start = start + 1 + hdrs_length
            #return main_type, lines[:start], hdrs, rest, []
            return main_type, (0, start), hdrs, (rest_start, None), None, False
        else:
            #return main_type, lines[:start], None, lines[start+(start2 or 0)+1:], []

            # Didn't find quoted section or headers, assume that everything
            # below is the qouted text.
            return main_type, (0, start), None, (start+(start2 or 0)+1, None), None, False

    # We just found headers, which usually indicates a forwarding.
    elif typ == 'headers':
        main_type = 'forward'
        hdrs, hdrs_length = extract_headers(lines[start:], max_wrap_lines)
        rest_start = start + hdrs_length
        return main_type, (0, start), hdrs, (rest_start, None), None, False

    # We found quoted text. Headers may be within the quoted text.
    elif typ == 'quoted':
        unquoted = unindent_lines(lines[start:])
        rest_start = start + len(unquoted)
        start2, typ = find_unwrap_start(unquoted, max_wrap_lines, min_header_lines, min_quoted_lines)
        if typ == 'headers':
            main_type = 'forward'
            hdrs, hdrs_length = extract_headers(unquoted[start2:], max_wrap_lines)
            rest2_start = start + hdrs_length
            return main_type, (0, start), hdrs, (rest2_start, rest_start), (rest_start, None), True
        else:
            main_type = 'quote'
            #return main_type, lines[:start], None, unquoted, rest
            return main_type, (None, start), None, (start, rest_start), (rest_start, None), True
