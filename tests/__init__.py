# -*- coding: utf-8 -*-

import unittest
from quotequail import quote, unwrap

class QuoteTestCase(unittest.TestCase):
    def test_quote_reply_1(self):
        self.assertEqual(
            quote(
"""Hello world.

On 2012-10-16 at 17:02 , Someone <someone@example.com> wrote:

> Some quoted text
"""),
            [(True, 'Hello world.\n\nOn 2012-10-16 at 17:02 , Someone <someone@example.com> wrote:'),
             (False, '\n> Some quoted text\n')]
        )

    def test_quote_reply_2(self):
        self.assertEqual(
            quote(
"""Hello world.

On 2012-10-16 at 17:02 , Someone <
someone@example.com> wrote:

> Some quoted text
"""),
            [(True, 'Hello world.\n\nOn 2012-10-16 at 17:02 , Someone <\nsomeone@example.com> wrote:'),
             (False, '\n> Some quoted text\n')]
        )

    def test_quote_forward_1(self):
        self.assertEqual(
            quote(
"""Hello world.

Begin forwarded message:

> From: Someone <someone@example.com>
> Subject: The email
>
> Some quoted text.
"""),
            [(True, 'Hello world.\n\nBegin forwarded message:'),
             (False, '\n> From: Someone <someone@example.com>\n> Subject: The email\n>\n> Some quoted text.\n')]
        )

    def test_quote_forward_2(self):
        self.assertEqual(
            quote(
"""Hello world.

---------- Forwarded message ----------
From: Someone <someone@example.com>
Subject: The email

Some quoted text.
"""),
            [(True, 'Hello world.\n\n---------- Forwarded message ----------'),
             (False, 'From: Someone <someone@example.com>\nSubject: The email\n\nSome quoted text.\n')]
        )

    def test_quote_forward_3(self):
        self.assertEqual(
            quote(
"""Hello world.

> Begin forwarded message:
>
> From: Someone <someone@example.com>
> Subject: The email
>
> Some quoted text.
"""),
            [(True, 'Hello world.\n\n> Begin forwarded message:'),
             (False, '>\n> From: Someone <someone@example.com>\n> Subject: The email\n>\n> Some quoted text.\n')]
        )


class UnwrapTestCase(unittest.TestCase):
    # TODO: Test this function with replies

    def test_gmail_forward(self):
        # Gmail forward
        self.assertEqual(unwrap("""Hello

---------- Forwarded message ----------
From: Someone <noreply@example.com>
Date: Fri, Apr 26, 2013 at 8:13 PM
Subject: Weekend Spanish classes
To: recipient@example.com

Spanish Classes
Learn Spanish
"""), {
            'text_top': 'Hello',
            'type': 'forward',
            'from': 'Someone <noreply@example.com>',
            'date': 'Fri, Apr 26, 2013 at 8:13 PM',
            'subject': 'Weekend Spanish classes',
            'to': 'recipient@example.com',
            'text': 'Spanish Classes\nLearn Spanish',
        })

    def test_apple_forward(self):
        # Apple Mail (10.9 and earlier) forward
        self.assertEqual(unwrap("""Hello

Begin forwarded message:

> From: "Some One" <some.one@example.com>
> Date: 1. August 2011 23:28:15 GMT-07:00
> To: "Other Person" <other@example.com>
> Subject: AW: AW: Some subject
> 
> Original text

Text bottom
"""), {
            'text_top': 'Hello',
            'type': 'forward',
            'from': '"Some One" <some.one@example.com>',
            'date': '1. August 2011 23:28:15 GMT-07:00',
            'subject': 'AW: AW: Some subject',
            'to': '"Other Person" <other@example.com>',
            'text': 'Original text',
            'text_bottom': 'Text bottom',
        })

    def test_apple_forward_2(self):
        # Apple Mail (10.10) forward
        self.assertEqual(unwrap("""Hello

> Begin forwarded message:
>
> From: "Some One" <some.one@example.com>
> Date: 1. August 2011 23:28:15 GMT-07:00
> To: "Other Person" <other@example.com>
> Subject: AW: AW: Some subject
> 
> Original text

Text bottom
"""), {
            'text_top': 'Hello',
            'type': 'forward',
            'from': '"Some One" <some.one@example.com>',
            'date': '1. August 2011 23:28:15 GMT-07:00',
            'subject': 'AW: AW: Some subject',
            'to': '"Other Person" <other@example.com>',
            'text': 'Original text',
            'text_bottom': 'Text bottom',
        })

    def test_sparrow_forward(self):
        # Sparrow forward
        self.assertEqual(unwrap("""Hello

Forwarded message:

> From: Some One <some.one@example.com>
> To: Other person <other@example.com>
> Date: Thursday, March 7, 2013 7:09:41 PM
> Subject: Re: Syncing Up
>
> OHAI
>
> Great news!

Text bottom
"""), {
            'text_top': 'Hello',
            'type': 'forward',
            'from': 'Some One <some.one@example.com>',
            'date': 'Thursday, March 7, 2013 7:09:41 PM',
            'subject': 'Re: Syncing Up',
            'to': 'Other person <other@example.com>',
            'text': 'OHAI\n\nGreat news!',
            'text_bottom': 'Text bottom',
        })

    def test_bold_headers(self):
        # Forwrad with *bold* text
        self.assertEqual(unwrap("""Hello

Forwarded message:

*From:* Some One <some@example.com>
*To:* Other Person <other@example.com>
*Date:* Wednesday, February 6, 2013 7:46:53 AM
*Subject:* Fwd: Hottest Startups

This is interesting."""), {
            'text_top': 'Hello',
            'type': 'forward',
            'from': 'Some One <some@example.com>',
            'date': 'Wednesday, February 6, 2013 7:46:53 AM',
            'subject': 'Fwd: Hottest Startups',
            'to': 'Other Person <other@example.com>',
            'text': 'This is interesting.',
        })

    def test_no_forward_text(self):
        # No forwarding message text
        self.assertEqual(unwrap("""Hello

From: "Some One" <some.one@example.com>
Date: 1. August 2011 23:28:15 GMT-07:00
To: "Other Person" <other@example.com>
Subject: AW: AW: Some subject

Original text
"""), {
            'text_top': 'Hello',
            'type': 'forward',
            'from': '"Some One" <some.one@example.com>',
            'date': '1. August 2011 23:28:15 GMT-07:00',
            'subject': 'AW: AW: Some subject',
            'to': '"Other Person" <other@example.com>',
            'text': 'Original text',
        })

    def test_no_forward_text_quoted(self):
        # No forwarding message text
        self.assertEqual(unwrap("""Hello

> From: "Some One" <some.one@example.com>
> Date: 1. August 2011 23:28:15 GMT-07:00
> To: "Other Person" <other@example.com>
> Subject: AW: AW: Some subject
>
> Original text
"""), {
            'text_top': 'Hello',
            'type': 'forward',
            'from': '"Some One" <some.one@example.com>',
            'date': '1. August 2011 23:28:15 GMT-07:00',
            'subject': 'AW: AW: Some subject',
            'to': '"Other Person" <other@example.com>',
            'text': 'Original text',
        })

    def test_outlook_forward(self):
        # Outlook?
        self.assertEqual(unwrap("""-------- Original Message --------
Subject: \tSome Newsletter
Date: \tFri, 19 Jun 2009 19:16:04 +0200
From: \tfrom <from@example.com>
Reply-To: \treply <reply@example.com>
To: \tto@example.com

OHAI"""), {
            'type': 'forward',
            'from': 'from <from@example.com>',
            'reply-to': 'reply <reply@example.com>',
            'date': 'Fri, 19 Jun 2009 19:16:04 +0200',
            'subject': 'Some Newsletter',
            'to': 'to@example.com',
            'reply-to': 'reply <reply@example.com>',
            'text': 'OHAI',
        })


    def test_spacing(self):
        # Some clients (Blackberry?) have weird whitespace rules
        self.assertEqual(unwrap("""hello world

-----Original Message-----
From: "Some One" <some.one@example.com>

Date: Sat, 22 Mar 2008 12:16:06 
To:<to@example.com>


Subject: Antw: FW: html


OHAI...
"""), {
            'text_top': 'hello world',
            'type': 'forward',
            'from': '"Some One" <some.one@example.com>',
            'date': 'Sat, 22 Mar 2008 12:16:06',
            'subject': 'Antw: FW: html',
            'to': '<to@example.com>',
            'text': 'OHAI...',
        })

    def test_quote(self):
        # Just a quote
        self.assertEqual(unwrap("""hello world

Hey: This is very important

> Lorem ipsum
> dolor sit amet
> adipiscing elit.

--
kthxbye
"""), {
            'type': 'quote',
            'text_top': 'hello world\n\nHey: This is very important',
            'text': 'Lorem ipsum\ndolor sit amet\nadipiscing elit.',
            'text_bottom': '--\nkthxbye',
        })


    def test_no_message(self):
        # No message
        self.assertEqual(unwrap("""hello world

Hey: This is very important

> No quoted message (just one line).
"""), None)


    def test_forward_no_headers(self):
        # No quote / headers in forwarded message
        self.assertEqual(unwrap("""Begin forwarded message:
Hello
"""), {
            'type': 'forward',
            'text': 'Hello',
        })

    def test_confusing_email_signature(self):
        self.assertEqual(unwrap("""Phone: 12345
Fax: 67890
Skype: foobar

---------- Forwarded message ----------
From: Someone <someone@example.com>
Subject: The email

Email text.
"""), {
            'text_top': 'Phone: 12345\nFax: 67890\nSkype: foobar',
            'type': 'forward',
            'from': 'Someone <someone@example.com>',
            'subject': 'The email',
            'text': 'Email text.',
        })

    def test_long_subject(self):
        self.assertEqual(unwrap("""---------- Forwarded message ----------
From: Someone <someone@example.com>
Subject: The email has a very long and confusing subject with spans over
multiple lines.
To: Destination <to@example.com>

Email text.
"""), {
            'type': 'forward',
            'from': 'Someone <someone@example.com>',
            'to': 'Destination <to@example.com>',
            'subject': 'The email has a very long and confusing subject with spans over multiple lines.',
            'text': 'Email text.',
        })

    def test_reply_1(self):
        data = unwrap("""Hello world.

On 2012-10-16 at 17:02 , Someone <someone@example.com> wrote:

> Some quoted text
""")
        # TODO: parsing replies is not fully implemented
        self.assertEqual(data['type'], 'reply')

    def test_reply_2(self):
        data = unwrap("""Hello world.

On 2012-10-16 at 17:02 , Someone <
someone@example.com> wrote:

> Some quoted text
""")
        # TODO: parsing replies is not fully implemented
        self.assertEqual(data['type'], 'reply')

    def test_french(self):
        self.assertEqual(unwrap(u"""
De : Someone <someone@example.com>
Répondre à : Reply <reply@example.com>
Date : Wednesday, 17 September 2014 4:24 pm
À : "Someone Else" <else@example.com>
Objet : Re: test subject

Hello, thanks for your reply
        """), {
            'type': 'forward',
            'date': u'Wednesday, 17 September 2014 4:24 pm',
            'from': u'Someone <someone@example.com>',
            'reply-to': 'Reply <reply@example.com>',
            'to': u'"Someone Else" <else@example.com>',
            'subject': u'Re: test subject',
            'text': u'Hello, thanks for your reply',
        })

if __name__ == '__main__':
    unittest.main()

