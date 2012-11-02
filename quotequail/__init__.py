# quotequail
# a library that identifies quoted text in email messages

import re

__all__ = ['quote']

"""
Takes a plain text message as an argument, returns a list of tuples.
The first argument of the tuple denotes whether the text should be expanded by default.
E.g. [(True, 'expanded text'), (False, 'Some quoted text')]
"""
def quote(text):
    lines = text.split('\n')

    regexes = [
        '^On .*wrote:$', # apple mail/gmail reply
        '^Am .*schrieb .*:$', # German
        '[0-9]{4}/[0-9]{1,2}/[0-9]{1,2} .* <.*@.*>$', # gmail (?) reply
        '^________________________________$', # yahoo?
        '^Begin forwarded message:$', # apple mail forward
        '^---+ ?Forwarded message ?---+$', # gmail forward
        '^---+ ?Original Message ?---+$', # outlook?
    ]
    
    found = None

    for n, line in enumerate(lines):
        for regex in regexes:
            if re.match(regex, line.strip()):
                found = n
                break

    if found != None:
        return [(True, '\n'.join(lines[:found+1])), (False, '\n'.join(lines[found+1:]))]

    return [(True, text)]
