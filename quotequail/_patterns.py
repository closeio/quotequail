# -*- coding: utf-8 -*-

import re

REPLY_PATTERNS = [
    u'^On (.*) wrote:$', # apple mail/gmail reply
    u'^Am (.*) schrieb (.*):$', # German
    u'^Le (.*) a écrit :$', # French
    u'El (.*) escribió:$', # Spanish
    u'([0-9]{4}/[0-9]{1,2}/[0-9]{1,2}) (.* <.*@.*>)$', # gmail (?) reply
]

REPLY_DATE_SPLIT_REGEX = re.compile(r'^(.*(:[0-9]{2}( [apAP]\.?[mM]\.?)?)), (.*)?$')

FORWARD_MESSAGES = [
    # apple mail forward
    'Begin forwarded message', 'Anfang der weitergeleiteten E-Mail',
    u'Début du message réexpédié', 'Inicio del mensaje reenviado',

    # gmail/evolution forward
    'Forwarded [mM]essage', 'Mensaje reenviado',

    # outlook
    'Original [mM]essage', 'Ursprüngliche Nachricht', 'Mensaje [oO]riginal',

    # Thunderbird forward
    u'Message transféré',
]

# We yield this pattern to simulate Outlook forward styles. It is also used for
# some emails forwarded by Yahoo.
FORWARD_LINE = '________________________________'

FORWARD_PATTERNS = [
    '^{}$'.format(FORWARD_LINE),

] + ['^---+ ?%s ?---+$' % p for p in FORWARD_MESSAGES] \
  + ['^%s:$' % p for p in FORWARD_MESSAGES]

FORWARD_STYLES = [
    # Outlook
    'border:none;border-top:solid #B5C4DF 1.0pt;padding:3.0pt 0in 0in 0in',
]

HEADER_RE = re.compile(r'\*?([-\w ]+):\*?(.*)$', re.UNICODE)

HEADER_MAP = {
    'from': 'from',
    'von': 'from',
    'de': 'from',

    'to': 'to',
    'an': 'to',
    'para': 'to',
    u'à': 'to',
    u'pour': 'to',

    'cc': 'cc',
    'kopie': 'cc',

    'bcc': 'bcc',
    'cco': 'bcc',
    'blindkopie': 'bcc',

    'reply-to': 'reply-to',
    'antwort an': 'reply-to',
    u'répondre à': 'reply-to',
    'responder a': 'reply-to',

    'date': 'date',
    'sent': 'date',
    'received': 'date',
    'datum': 'date',
    'gesendet': 'date',
    'enviado el': 'date',
    'enviados': 'date',
    'fecha': 'date',

    'subject': 'subject',
    'betreff': 'subject',
    'asunto': 'subject',
    'objet': 'subject',
    'sujet': 'subject',
}

COMPILED_PATTERN_MAP = {
    'reply': [re.compile(regex) for regex in REPLY_PATTERNS],
    'forward': [re.compile(regex) for regex in FORWARD_PATTERNS],
}

COMPILED_PATTERNS = sum(COMPILED_PATTERN_MAP.values(), [])

MULTIPLE_WHITESPACE_RE = re.compile('\s+')

# Amount to lines to join to check for potential wrapped patterns in plain text
# messages.
MAX_WRAP_LINES = 2

# minimum number of headers that we recognize
MIN_HEADER_LINES = 2

# minimum number of lines to recognize a quoted block
MIN_QUOTED_LINES = 3

# Characters at the end of line where we join lines without adding a space.
# For example, "John <\njohn@example>" becomes "John <john@example>", but
# "John\nDoe" becomes "John Doe".
STRIP_SPACE_CHARS = '<([{"\''
