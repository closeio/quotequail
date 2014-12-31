# -*- coding: utf-8 -*-

import unittest
from quotequail import quote, quote_html, unwrap

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

class HTMLQuoteTestCase(unittest.TestCase):
    def test_apple(self):
        self.assertEqual(
            quote_html('''<html><head><meta http-equiv="Content-Type" content="text/html charset=us-ascii"></head><body style="word-wrap: break-word; -webkit-nbsp-mode: space; -webkit-line-break: after-white-space;" class="">Some text<div class=""><br class=""></div><div class="">some more text</div><div class=""><br class=""></div><div class=""><br class=""><div><blockquote type="cite" class=""><div class="">On Nov 12, 2014, at 11:07 PM, Some One &lt;<a href="mailto:someone@example.com" class="">someone@example.com</a>&gt; wrote:</div><br class="Apple-interchange-newline"><div class=""><meta http-equiv="Content-Type" content="text/html charset=us-ascii" class=""><div style="word-wrap: break-word; -webkit-nbsp-mode: space; -webkit-line-break: after-white-space;" class="">Lorem ipsum dolor sit amet.<div class=""><br class=""></div></div></div></blockquote></div><br class=""></div></body></html>'''),
            [
                # Note that lxml removes Content-Type meta tags (see
                # lxml.html.tostring include_meta_content_type flag)
                (True, '''<html><head></head><body style="word-wrap: break-word; -webkit-nbsp-mode: space; -webkit-line-break: after-white-space;" class="">Some text<div class=""><br class=""></div><div class="">some more text</div><div class=""><br class=""></div><div class=""><br class=""><div><blockquote type="cite" class=""><div class="">On Nov 12, 2014, at 11:07 PM, Some One &lt;<a href="mailto:someone@example.com" class="">someone@example.com</a>&gt; wrote:</div></blockquote></div></div></body></html>'''),
                # Note we have an empty div stripped out here.
                (False, '''<html><body style="word-wrap: break-word; -webkit-nbsp-mode: space; -webkit-line-break: after-white-space;" class=""><div class=""><div><blockquote type="cite" class=""><br class="Apple-interchange-newline"><div class=""><div style="word-wrap: break-word; -webkit-nbsp-mode: space; -webkit-line-break: after-white-space;" class="">Lorem ipsum dolor sit amet.<div class=""><br class=""></div></div></div></blockquote></div><br class=""></div></body></html>'''),
            ]
        )

    def test_gmail(self):
        self.assertEqual(
            quote_html('''<div dir="ltr"><br><div class="gmail_quote">---------- Forwarded message ----------<br>From: <b class="gmail_sendername">Some One</b> <span dir="ltr">&lt;<a href="mailto:someone@example.com">someone@example.com</a>&gt;</span>
</div><br><br clear="all"><div><br></div>-- <br><div class="gmail_signature"><div>Some One</div></div>
</div>'''),
            [
                (True, '''<div dir="ltr"><br><div class="gmail_quote">---------- Forwarded message ----------</div></div>'''),
                (False, '''<div dir="ltr"><div class="gmail_quote"><br>From: <b class="gmail_sendername">Some One</b> <span dir="ltr">&lt;<a href="mailto:someone@example.com">someone@example.com</a>&gt;</span>
</div><br><br clear="all"><div><br></div>-- <br><div class="gmail_signature"><div>Some One</div></div>
</div>'''),
            ]
        )

    def test_gmail_2(self):
        self.assertEqual(
            quote_html(u'''<div dir="ltr">looks good\xa0</div><div class="gmail_extra"><br><div class="gmail_quote">On Thu, Dec 18, 2014 at 10:02 AM, foo <span dir="ltr">&lt;<a href="mailto:foo@example.com" target="_blank">foo@example.com</a>&gt;</span> wrote:<blockquote class="gmail_quote" style="margin:0 0 0 .8ex;border-left:1px #ccc solid;padding-left:1ex"><div dir="ltr">Hey Phil,\xa0<div><br><div>Sending you the report:\xa0</div></div><div><span class="HOEnZb"><font color="#888888"><br></font></span></div><span class="HOEnZb"><font color="#888888"><div><br></div><div class="gmail_extra">-- <br><div><div dir="ltr"><div>Cheers,</div><div>foo &amp; example Team</div><div><a href="http://www.example.com" target="_blank">www.example.com</a> ; - <a href="mailto:help@example.com" target="_blank">help@example.com</a>\xa0</div></div></div>\r\n</div></font></span></div>\r\n</blockquote></div></div>\r\n'''),
            [
                (True, u'''<div dir="ltr">looks good&#160;</div><div class="gmail_extra"><br><div class="gmail_quote">On Thu, Dec 18, 2014 at 10:02 AM, foo <span dir="ltr">&lt;<a href="mailto:foo@example.com" target="_blank">foo@example.com</a>&gt;</span> wrote:</div></div>'''),
                (False, u'''<div class="gmail_extra"><div class="gmail_quote"><blockquote class="gmail_quote" style="margin:0 0 0 .8ex;border-left:1px #ccc solid;padding-left:1ex"><div dir="ltr">Hey Phil,&#160;<div><br><div>Sending you the report:&#160;</div></div><div><span class="HOEnZb"><font color="#888888"><br></font></span></div><span class="HOEnZb"><font color="#888888"><div><br></div><div class="gmail_extra">-- <br><div><div dir="ltr"><div>Cheers,</div><div>foo &amp; example Team</div><div><a href="http://www.example.com" target="_blank">www.example.com</a> ; - <a href="mailto:help@example.com" target="_blank">help@example.com</a>&#160;</div></div></div>\r\n</div></font></span></div>\r\n</blockquote></div></div>\r\n'''),
            ]
        )

    def test_outlook(self):
        self.assertEqual(
            quote_html(u'''<html xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word" xmlns:m="http://schemas.microsoft.com/office/2004/12/omml" xmlns="http://www.w3.org/TR/REC-html40"><head></head><body lang=EN-US link=blue vlink=purple><div class=WordSection1><p class=MsoNormal><span style='font-size:11.0pt;font-family:"Calibri","sans-serif";color:#1F497D'>Thanks,<o:p></o:p></span></p><p class=MsoNormal><span style='font-size:11.0pt;font-family:"Calibri","sans-serif";color:#1F497D'><o:p>&nbsp;</o:p></span></p><p class=MsoNormal><span style='font-size:11.0pt;font-family:"Calibri","sans-serif";color:#1F497D'><o:p>&nbsp;</o:p></span></p><div><div style='border:none;border-top:solid #B5C4DF 1.0pt;padding:3.0pt 0in 0in 0in'><p class=MsoNormal><b><span style='font-size:10.0pt;font-family:"Tahoma","sans-serif"'>From:</span></b><span style='font-size:10.0pt;font-family:"Tahoma","sans-serif"'> John Doe [mailto:john@example.com] <br><b>Sent:</b> Tuesday, December 30, 2014 5:31 PM<br><b>To:</b> recipient@example.com<br><b>Subject:</b> Excited to have you on board!<o:p></o:p></span></p></div></div><p class=MsoNormal><o:p>&nbsp;</o:p></p><p>Hey,<o:p></o:p></p></div></body></html>'''),
            [
                (True, '<html xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word" xmlns:m="http://schemas.microsoft.com/office/2004/12/omml" xmlns="http://www.w3.org/TR/REC-html40"><head></head><body lang="EN-US" link="blue" vlink="purple"><div class="WordSection1"><p class="MsoNormal"><span style=\'font-size:11.0pt;font-family:"Calibri","sans-serif";color:#1F497D\'>Thanks,<p></p></span></p><p class="MsoNormal"><span style=\'font-size:11.0pt;font-family:"Calibri","sans-serif";color:#1F497D\'><p>&#160;</p></span></p><p class="MsoNormal"><span style=\'font-size:11.0pt;font-family:"Calibri","sans-serif";color:#1F497D\'><p>&#160;</p></span></p><div><div style="border:none;border-top:solid #B5C4DF 1.0pt;padding:3.0pt 0in 0in 0in"></div></div></div></body></html>'),
                (False, '<html xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word" xmlns:m="http://schemas.microsoft.com/office/2004/12/omml" xmlns="http://www.w3.org/TR/REC-html40"><body lang="EN-US" link="blue" vlink="purple"><div class="WordSection1"><div><div style="border:none;border-top:solid #B5C4DF 1.0pt;padding:3.0pt 0in 0in 0in"><p class="MsoNormal"><b><span style=\'font-size:10.0pt;font-family:"Tahoma","sans-serif"\'>From:</span></b><span style=\'font-size:10.0pt;font-family:"Tahoma","sans-serif"\'> John Doe [mailto:john@example.com] <br><b>Sent:</b> Tuesday, December 30, 2014 5:31 PM<br><b>To:</b> recipient@example.com<br><b>Subject:</b> Excited to have you on board!<p></p></span></p></div></div><p class="MsoNormal"><p>&#160;</p></p><p>Hey,<p></p></p></div></body></html>')
            ]
        )

    def test_no_wrap_tag(self):
        self.assertEqual(
            quote_html(u'''On Thu, Dec 18, 2014 at 10:02 AM, foo &lt;foo@example.com&gt; wrote:<blockquote>some stuff</blockquote>'''),
            [
                (True, 'On Thu, Dec 18, 2014 at 10:02 AM, foo &lt;foo@example.com&gt; wrote:'),
                (False, '<blockquote>some stuff</blockquote>'),
            ]
        )

    def test_images(self):
        self.assertEqual(
            quote_html('''<div>Well hello there Sir!!!<br><br><br>On Dec 23, 2014, at 04:35 PM, Steve Wiseman &lt;wiseman.steve@ymail.com&gt; wrote:<br><blockquote type=\"cite\"><div style=\"color:#000;\"><div dir=\"ltr\">Hi there&nbsp;<img src=\"https://s.yimg.com/ok/u/assets/img/emoticons/emo14.gif\" alt=\"*B-) cool\" title=\"*B-) cool\" class=\"fr-fin\"><img src=\"https://s.yimg.com/ok/u/assets/img/emoticons/emo7.gif\" alt=\"*:P tongue\" title=\"*:P tongue\" class=\"fr-fin\"><img src=\"https://s.yimg.com/ok/u/assets/img/emoticons/emo72.gif\" alt=\"*:->~~ spooky\" title=\"*:->~~ spooky\" class=\"fr-fin\"></div></div></blockquote></div>'''),
            [
                (True, u'''<div>Well hello there Sir!!!<br><br><br>On Dec 23, 2014, at 04:35 PM, Steve Wiseman &lt;wiseman.steve@ymail.com&gt; wrote:</div>'''),
                (False, u'''<div><br><blockquote type="cite"><div style="color:#000;"><div dir="ltr">Hi there&#160;<img src=\"https://s.yimg.com/ok/u/assets/img/emoticons/emo14.gif\" alt=\"*B-) cool\" title=\"*B-) cool\" class=\"fr-fin\"><img src=\"https://s.yimg.com/ok/u/assets/img/emoticons/emo7.gif\" alt=\"*:P tongue\" title=\"*:P tongue\" class=\"fr-fin\"><img src=\"https://s.yimg.com/ok/u/assets/img/emoticons/emo72.gif\" alt=\"*:-&gt;~~ spooky\" title=\"*:-&gt;~~ spooky\" class=\"fr-fin\"></div></div></blockquote></div>''')
            ]
        )

    def test_no_quote(self):
        self.assertEqual(
            quote_html(u'''<p>One</p><p>Two</p><p>Three</p>'''),
            [
                (True, '<p>One</p><p>Two</p><p>Three</p>'),
            ]
        )

    def test_limit(self):
        self.assertEqual(
            quote_html(u'''<p>One</p><p>Two</p><p>Three</p><p>Four</p>''', limit=3),
            [
                (True, '<p>One</p><p>Two</p><p>Three</p>'),
                (False, '<p>Four</p>'),
            ]
        )

    def test_empty(self):
        self.assertEqual(
            quote_html(u''),
            [
                (True, ''),
            ]
        )

    def test_comment(self):
        self.assertEqual(
            quote_html(u'''<!-- test -->'''),
            [
                (True, '<!-- test -->'),
            ]
        )

    def test_comment_2(self):
        self.assertEqual(
            quote_html(u'''A<!-- test -->B'''),
            [
                (True, 'A<!-- test -->B'),
            ]
        )

    def test_encoding(self):
        # We assume everything is UTF-8
        self.assertEqual(
            quote_html(u'''<?xml version="1.0" encoding="ISO-8859-1"?>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1" />
<title></title>
</head>
<body>
test ä
</body>
</html>'''), [
            (True, u'''<html xmlns="http://www.w3.org/1999/xhtml">
<head>

<title></title>
</head>
<body>
test &#228;
</body>
</html>'''),
        ])


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

