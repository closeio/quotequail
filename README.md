quotequail
==========

A library that identifies quoted text in plain text and HTML email messages.

```python
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
