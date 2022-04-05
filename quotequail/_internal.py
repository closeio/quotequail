from ._patterns import (
    COMPILED_PATTERN_MAP,
    HEADER_MAP,
    HEADER_RE,
    REPLY_DATE_SPLIT_REGEX,
    STRIP_SPACE_CHARS,
)

"""
Internal methods. For max_wrap_lines, min_header_lines, min_quoted_lines
documentation see the corresponding constants in _patterns.py.
"""


def find_pattern_on_line(lines, n, max_wrap_lines):
    """
    Find a forward/reply pattern within the given lines on text on the given
    line number and return a tuple with the type ('reply' or 'forward') and
    line number of where the pattern ends. The returned line number may be
    different from the given line number in case the pattern wraps over
    multiple lines.

    Returns (None, None) if no pattern was found.
    """
    for typ, regexes in COMPILED_PATTERN_MAP.items():
        for regex in regexes:
            for m in range(max_wrap_lines):
                match_line = join_wrapped_lines(lines[n : n + 1 + m])
                if match_line.startswith(">"):
                    match_line = match_line[1:].strip()
                if regex.match(match_line.strip()):
                    return n + m, typ
    return None, None


def find_quote_position(lines, max_wrap_lines, limit=None):
    """
    Return the (ending) line number of a quoting pattern. If a limit is given
    and the limit is reached, the limit is returned.
    """
    for n in range(len(lines)):
        end, typ = find_pattern_on_line(lines, n, max_wrap_lines)
        if typ:
            return end
        if limit is not None and n >= limit - 1:
            return n

    return None


def join_wrapped_lines(lines):
    """
    Join one or multiple lines that wrapped. Returns the reconstructed line.
    Takes into account proper spacing between the lines (see
    STRIP_SPACE_CHARS).
    """
    if len(lines) == 1:
        return lines[0]

    joined = lines[0]
    for line in lines[1:]:
        if joined and joined[-1] in STRIP_SPACE_CHARS:
            joined += line
        else:
            joined += " "
            joined += line

    return joined


def extract_headers(lines, max_wrap_lines):
    """
    Extract email headers from the given lines. Returns a dict with the
    detected headers and the amount of lines that were processed.
    """
    hdrs = {}
    header_name = None

    # Track overlong headers that extend over multiple lines
    extend_lines = 0

    lines_processed = 0

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
            lines_processed = n + 1
        else:
            extend_lines += 1
            if extend_lines < max_wrap_lines and header_name in HEADER_MAP:
                hdrs[HEADER_MAP[header_name]] = join_wrapped_lines(
                    [hdrs[HEADER_MAP[header_name]], line.strip()]
                )
                lines_processed = n + 1
            else:
                # no more headers found
                break

    return hdrs, lines_processed


def parse_reply(line):
    """
    Parse the given reply line ("On DATE, USER wrote:") and returns a
    dictionary with the "Date" and "From" keys, or None, if couldn't parse.
    """
    if line.startswith(">"):
        line = line[1:].strip()

    date = user = None

    for pattern in COMPILED_PATTERN_MAP["reply"]:
        match = pattern.match(line)
        if match:
            groups = match.groups()
            if len(groups) == 2:
                # We're lucky and got both date and user split up.
                date, user = groups
            else:
                split_match = REPLY_DATE_SPLIT_REGEX.match(groups[0])
                if split_match:
                    split_groups = split_match.groups()
                    date = split_groups[0]
                    user = split_groups[-1]
                else:
                    # Try a simple comma split
                    split = groups[0].rsplit(",", 1)
                    if len(split) == 2:
                        date, user = split

    if date:
        date = date.strip()

    if user:
        user = user.strip()

    if date and user:
        return {
            "date": date.strip(),
            "from": user.strip(),
        }


def find_unwrap_start(lines, max_wrap_lines, min_header_lines, min_quoted_lines):
    """
    Find the starting point of a wrapped email. Returns a tuple containing
    (start_line_number, end_line_number, type), where type can be one of the
    following:

     * 'forward': A matching forwarding pattern was found
     * 'reply': A matching reply pattern was found
     * 'headers': Headers were found (usually a forwarded email)
     * 'quote': A quote was found

    start_line_number corresponds to the line number where the forwarding/reply
    pattern starts, or where the headers/quote starts. end_line_number is only
    different from start_line_number if the forwarding/reply pattern spans over
    multiple lines (it does not extend to the end of the headers or of the
    quoted section).

    Returns (None, None, None) if nothing was found.
    """
    for n, line in enumerate(lines):
        if not line.strip():
            continue

        # Find a forward / reply start pattern

        end, typ = find_pattern_on_line(lines, n, max_wrap_lines)
        if typ:
            return n, end, typ

        # Find a quote
        if line.startswith(">"):
            # Check if there are at least min_quoted_lines lines that match
            matched_lines = 1

            if matched_lines >= min_quoted_lines:
                return n, n, "quoted"

            for peek_line in lines[n + 1 :]:
                if not peek_line.strip():
                    continue
                if not peek_line.startswith(">"):
                    break
                else:
                    matched_lines += 1
                if matched_lines >= min_quoted_lines:
                    return n, n, "quoted"

        # Find a header
        match = HEADER_RE.match(line)
        if (
            match
            and len(extract_headers(lines[n:], max_wrap_lines)[0]) >= min_header_lines
        ):
            return n, n, "headers"

    return None, None, None


def unindent_lines(lines):
    unquoted = []
    for line in lines:
        if line.startswith("> "):
            unquoted.append(line[2:])
        elif line.startswith(">"):
            unquoted.append(line[1:])
        else:
            break

    return unquoted


def unwrap(lines, max_wrap_lines, min_header_lines, min_quoted_lines):
    """
    Return a tuple of:
    - Type ('forward', 'reply', 'headers', 'quoted')
    - Range of the text at the top of the wrapped message (or None)
    - Headers dict (or None)
    - Range of the text of the wrapped message (or None)
    - Range of the text below the wrapped message (or None)
    - Whether the wrapped text needs to be unindented
    """
    headers = {}

    # Get line number and wrapping type.
    start, end, typ = find_unwrap_start(
        lines, max_wrap_lines, min_header_lines, min_quoted_lines
    )

    # We found a line indicating that it's a forward/reply.
    if typ in ("forward", "reply"):
        main_type = typ

        if typ == "reply":
            reply_headers = parse_reply(join_wrapped_lines(lines[start : end + 1]))
            if reply_headers:
                headers.update(reply_headers)

        # Find where the headers or the quoted section starts.
        # We can set min_quoted_lines to 1 because we expect a quoted section.
        start2, end2, typ = find_unwrap_start(
            lines[end + 1 :], max_wrap_lines, min_header_lines, 1
        )

        if typ == "quoted":
            # Quoted section starts. Unindent and check if there are headers.
            quoted_start = end + 1 + start2
            unquoted = unindent_lines(lines[quoted_start:])
            rest_start = quoted_start + len(unquoted)
            start3, end3, typ = find_unwrap_start(
                unquoted, max_wrap_lines, min_header_lines, min_quoted_lines
            )
            if typ == "headers":
                hdrs, hdrs_length = extract_headers(unquoted[start3:], max_wrap_lines)
                if hdrs:
                    headers.update(hdrs)
                rest2_start = quoted_start + start3 + hdrs_length
                return (
                    main_type,
                    (0, start),
                    headers,
                    (rest2_start, rest_start),
                    (rest_start, None),
                    True,
                )
            else:
                return (
                    main_type,
                    (0, start),
                    headers,
                    (quoted_start, rest_start),
                    (rest_start, None),
                    True,
                )

        elif typ == "headers":
            hdrs, hdrs_length = extract_headers(lines[start + 1 :], max_wrap_lines)
            if hdrs:
                headers.update(hdrs)
            rest_start = start + 1 + hdrs_length
            return main_type, (0, start), headers, (rest_start, None), None, False
        else:
            # Didn't find quoted section or headers, assume that everything
            # below is the qouted text.
            return (
                main_type,
                (0, start),
                headers,
                (start + (start2 or 0) + 1, None),
                None,
                False,
            )

    # We just found headers, which usually indicates a forwarding.
    elif typ == "headers":
        main_type = "forward"
        hdrs, hdrs_length = extract_headers(lines[start:], max_wrap_lines)
        rest_start = start + hdrs_length
        return main_type, (0, start), hdrs, (rest_start, None), None, False

    # We found quoted text. Headers may be within the quoted text.
    elif typ == "quoted":
        unquoted = unindent_lines(lines[start:])
        rest_start = start + len(unquoted)
        start2, end2, typ = find_unwrap_start(
            unquoted, max_wrap_lines, min_header_lines, min_quoted_lines
        )
        if typ == "headers":
            main_type = "forward"
            hdrs, hdrs_length = extract_headers(unquoted[start2:], max_wrap_lines)
            rest2_start = start + hdrs_length
            return (
                main_type,
                (0, start),
                hdrs,
                (rest2_start, rest_start),
                (rest_start, None),
                True,
            )
        else:
            main_type = "quote"
            return (
                main_type,
                (None, start),
                None,
                (start, rest_start),
                (rest_start, None),
                True,
            )
