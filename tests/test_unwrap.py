import pytest

from quotequail import unwrap


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        # Gmail forward
        (
            """Hello

---------- Forwarded message ----------
From: Someone <noreply@example.com>
Date: Fri, Apr 26, 2013 at 8:13 PM
Subject: Weekend Spanish classes
To: recipient@example.com

Spanish Classes
Learn Spanish
""",
            {
                "text_top": "Hello",
                "type": "forward",
                "from": "Someone <noreply@example.com>",
                "date": "Fri, Apr 26, 2013 at 8:13 PM",
                "subject": "Weekend Spanish classes",
                "to": "recipient@example.com",
                "text": "Spanish Classes\nLearn Spanish",
            },
        ),
        # Apple Mail (10.9 and earlier) forward
        (
            """Hello

Begin forwarded message:

> From: "Some One" <some.one@example.com>
> Date: 1. August 2011 23:28:15 GMT-07:00
> To: "Other Person" <other@example.com>
> Subject: AW: AW: Some subject
>
> Original text

Text bottom
""",
            {
                "text_top": "Hello",
                "type": "forward",
                "from": '"Some One" <some.one@example.com>',
                "date": "1. August 2011 23:28:15 GMT-07:00",
                "subject": "AW: AW: Some subject",
                "to": '"Other Person" <other@example.com>',
                "text": "Original text",
                "text_bottom": "Text bottom",
            },
        ),
        (
            # Apple Mail (10.10) forward
            """Hello

> Begin forwarded message:
>
> From: "Some One" <some.one@example.com>
> Date: 1. August 2011 23:28:15 GMT-07:00
> To: "Other Person" <other@example.com>
> Subject: AW: AW: Some subject
>
> Original text

Text bottom
""",
            {
                "text_top": "Hello",
                "type": "forward",
                "from": '"Some One" <some.one@example.com>',
                "date": "1. August 2011 23:28:15 GMT-07:00",
                "subject": "AW: AW: Some subject",
                "to": '"Other Person" <other@example.com>',
                "text": "Original text",
                "text_bottom": "Text bottom",
            },
        ),
        # Sparrow forward
        (
            """Hello

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
""",
            {
                "text_top": "Hello",
                "type": "forward",
                "from": "Some One <some.one@example.com>",
                "date": "Thursday, March 7, 2013 7:09:41 PM",
                "subject": "Re: Syncing Up",
                "to": "Other person <other@example.com>",
                "text": "OHAI\n\nGreat news!",
                "text_bottom": "Text bottom",
            },
        ),
        # Forward with *bold* text
        (
            """Hello

Forwarded message:

*From:* Some One <some@example.com>
*To:* Other Person <other@example.com>
*Date:* Wednesday, February 6, 2013 7:46:53 AM
*Subject:* Fwd: Hottest Startups

This is interesting.""",
            {
                "text_top": "Hello",
                "type": "forward",
                "from": "Some One <some@example.com>",
                "date": "Wednesday, February 6, 2013 7:46:53 AM",
                "subject": "Fwd: Hottest Startups",
                "to": "Other Person <other@example.com>",
                "text": "This is interesting.",
            },
        ),
        # No forwarding message text
        (
            """Hello

From: "Some One" <some.one@example.com>
Date: 1. August 2011 23:28:15 GMT-07:00
To: "Other Person" <other@example.com>
Subject: AW: AW: Some subject

Original text
""",
            {
                "text_top": "Hello",
                "type": "forward",
                "from": '"Some One" <some.one@example.com>',
                "date": "1. August 2011 23:28:15 GMT-07:00",
                "subject": "AW: AW: Some subject",
                "to": '"Other Person" <other@example.com>',
                "text": "Original text",
            },
        ),
        # No forwarding message text (quoted)
        (
            """Hello

> From: "Some One" <some.one@example.com>
> Date: 1. August 2011 23:28:15 GMT-07:00
> To: "Other Person" <other@example.com>
> Subject: AW: AW: Some subject
>
> Original text
""",
            {
                "text_top": "Hello",
                "type": "forward",
                "from": '"Some One" <some.one@example.com>',
                "date": "1. August 2011 23:28:15 GMT-07:00",
                "subject": "AW: AW: Some subject",
                "to": '"Other Person" <other@example.com>',
                "text": "Original text",
            },
        ),
        # Outlook
        (
            """-------- Original Message --------
Subject: \tSome Newsletter
Date: \tFri, 19 Jun 2009 19:16:04 +0200
From: \tfrom <from@example.com>
Reply-To: \treply <reply@example.com>
To: \tto@example.com

OHAI""",
            {
                "type": "forward",
                "from": "from <from@example.com>",
                "reply-to": "reply <reply@example.com>",
                "date": "Fri, 19 Jun 2009 19:16:04 +0200",
                "subject": "Some Newsletter",
                "to": "to@example.com",
                "text": "OHAI",
            },
        ),
        # Some clients (Blackberry?) have weird whitespace rules
        (
            """hello world

-----Original Message-----
From: "Some One" <some.one@example.com>

Date: Sat, 22 Mar 2008 12:16:06
To:<to@example.com>


Subject: Antw: FW: html


OHAI...
""",
            {
                "text_top": "hello world",
                "type": "forward",
                "from": '"Some One" <some.one@example.com>',
                "date": "Sat, 22 Mar 2008 12:16:06",
                "subject": "Antw: FW: html",
                "to": "<to@example.com>",
                "text": "OHAI...",
            },
        ),
        # Just a quote
        (
            """hello world

Hey: This is very important

> Lorem ipsum
> dolor sit amet
> adipiscing elit.

--
kthxbye
""",
            {
                "type": "quote",
                "text_top": "hello world\n\nHey: This is very important",
                "text": "Lorem ipsum\ndolor sit amet\nadipiscing elit.",
                "text_bottom": "--\nkthxbye",
            },
        ),
        # No message
        (
            """hello world

Hey: This is very important

> No quoted message (just one line).
""",
            None,
        ),
        # No quote / headers in forwarded message
        (
            """Begin forwarded message:
Hello
""",
            {
                "type": "forward",
                "text": "Hello",
            },
        ),
        # Confusing email signature
        (
            """Phone: 12345
Fax: 67890
Skype: foobar

---------- Forwarded message ----------
From: Someone <someone@example.com>
Subject: The email

Email text.
""",
            {
                "text_top": "Phone: 12345\nFax: 67890\nSkype: foobar",
                "type": "forward",
                "from": "Someone <someone@example.com>",
                "subject": "The email",
                "text": "Email text.",
            },
        ),
        # Long subject
        (
            """---------- Forwarded message ----------
From: Someone <someone@example.com>
Subject: The email has a very long and confusing subject with spans over
multiple lines.
To: Destination <to@example.com>

Email text.
""",
            {
                "type": "forward",
                "from": "Someone <someone@example.com>",
                "to": "Destination <to@example.com>",
                "subject": "The email has a very long and confusing subject with spans over multiple lines.",
                "text": "Email text.",
            },
        ),
        # Reply
        (
            """Hello world.

On 2012-10-16 at 17:02 , Someone <someone@example.com> wrote:

> Some quoted text
""",
            {
                "type": "reply",
                "date": "2012-10-16 at 17:02",
                "from": "Someone <someone@example.com>",
                "text_top": "Hello world.",
                "text": "Some quoted text",
            },
        ),
        # Reply with line break
        (
            """Hello world.

On 2012-10-16 at 17:02 , Someone <
someone@example.com> wrote:

> Some quoted text
""",
            {
                "type": "reply",
                "date": "2012-10-16 at 17:02",
                "from": "Someone <someone@example.com>",
                "text_top": "Hello world.",
                "text": "Some quoted text",
            },
        ),
        # French email
        (
            """
De : Someone <someone@example.com>
Répondre à : Reply <reply@example.com>
Date : Wednesday, 17 September 2014 4:24 pm
À : "Someone Else" <else@example.com>
Objet : Re: test subject

Hello, thanks for your reply
        """,
            {
                "type": "forward",
                "date": "Wednesday, 17 September 2014 4:24 pm",
                "from": "Someone <someone@example.com>",
                "reply-to": "Reply <reply@example.com>",
                "to": '"Someone Else" <else@example.com>',
                "subject": "Re: test subject",
                "text": "Hello, thanks for your reply",
            },
        ),
        # Forwarded French Apple Mail
        (
            """
Text before

Début du message réexpédié :

De: "Foo Bar" <from@example.com>
Date: 14 novembre 2015 15:14:53 UTC+1
À: "'Ham Spam'" <to@example.com>
Objet: RE: The subject

Text after
""",
            {
                "date": "14 novembre 2015 15:14:53 UTC+1",
                "from": '"Foo Bar" <from@example.com>',
                "subject": "RE: The subject",
                "text": "Text after",
                "text_top": "Text before",
                "to": "\"'Ham Spam'\" <to@example.com>",
                "type": "forward",
            },
        ),
        # Forwarded French Thunderbird
        (
            """
Text before

-------- Message transféré --------
Sujet :     Re: Some subject
Date :  Wed, 11 Nov 2015 12:31:25 +0100
De :    Foo Bar <from@example.com>
Pour :  Ham Spam <to@example.com>

Text after
""",
            {
                "date": "Wed, 11 Nov 2015 12:31:25 +0100",
                "from": "Foo Bar <from@example.com>",
                "subject": "Re: Some subject",
                "text": "Text after",
                "text_top": "Text before",
                "to": "Ham Spam <to@example.com>",
                "type": "forward",
            },
        ),
        # Forwarded Gmail Swedish
        (
            """Hello

---------- Vidarebefordrat meddelande ----------
Från: Someone <noreply@example.com>
Datum: 26 april 2013 20:13
Ämne: Weekend Spanish classes
Till: recipient@example.com

Spanish Classes
Learn Spanish
""",
            {
                "text_top": "Hello",
                "type": "forward",
                "from": "Someone <noreply@example.com>",
                "date": "26 april 2013 20:13",
                "subject": "Weekend Spanish classes",
                "to": "recipient@example.com",
                "text": "Spanish Classes\nLearn Spanish",
            },
        ),
    ],
)
def test_unwrap(text, expected):
    assert unwrap(text) == expected
