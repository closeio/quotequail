==========
quotequail
==========

A library that identifies quoted text in plain text and HTML email messages.
quotequail has no mandatory dependencies, however using HTML methods require
libxml.


(Interested in working on projects like this? `Close.io`_ is looking for `great engineers`_ to join our team)

.. _Close.io: http://close.io
.. _great engineers: http://jobs.close.io


Introduction
------------

quotequail comes with the functions listed below which are documented in detail
in quotequail's ``__init__.py``.

* ``quote(text)``: Takes a plain text message as an argument, returns a list of
  tuples. The first argument of the tuple denotes whether the text should be
  expanded by default. The second argument is the unmodified corresponding
  text.
* ``quote_html(html)``: Like ``quote()``, but takes an HTML message as an
  argument.
* ``unwrap(text)``: If the passed text is the text body of a forwarded message,
  a reply, or contains quoted text, a dictionary is returned, containing the
  type (reply/forward/quote), the text at the top/bottom of the wrapped
  message, any parsed headers, and the text of the wrapped message.
* ``unwrap_html(text)``: Like ``unwrap()``, but takes an HTML message as an
  argument.


Examples
--------

.. code:: python

  In [1]: import quotequail

  In [2]: quotequail.quote("""Hello world.

  On 2012-10-16 at 17:02 , Someone <someone@example.com> wrote:

  > Some quoted text
  """)
  Out[2]:
  [(True, 'Hello world.\n\nOn 2012-10-16 at 17:02 , Someone <someone@example.com> wrote:'),
   (False, '\n> Some quoted text\n')]

  In [3]: quotequail.unwrap("""Hello

  Begin forwarded message:

  > From: "Some One" <some.one@example.com>
  > Date: 1. August 2011 23:28:15 GMT-07:00
  > To: "Other Person" <other@example.com>
  > Subject: AW: AW: Some subject
  >
  > Original text

  Text bottom
  """))
  Out[3]:
  {'date': '1. August 2011 23:28:15 GMT-07:00',
   'from': '"Some One" <some.one@example.com>',
   'subject': 'AW: AW: Some subject',
   'text': 'Original text',
   'text_bottom': 'Text bottom',
   'text_top': 'Hello',
   'to': '"Other Person" <other@example.com>',
   'type': 'forward'}
