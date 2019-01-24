# -*- coding: utf-8 -*-

import os
import unittest
from quotequail import *

class FileMixin(object):
    def read_file(self, name):
        with open(os.path.join(os.path.dirname(__file__), 'files', name), 'rb') as f:
            return f.read().decode('utf8')

    def assert_equal_to_file(self, string, name):
        expected = self.read_file(name)
        self.assertEqual(string, expected)

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

    def test_quote_reply_3(self):
        self.assertEqual(
            quote(
"""Hello world.

On 2012-10-16 at 17:02 , Someone <someone@example.com>
wrote:

> Some quoted text
"""),
            [(True, 'Hello world.\n\nOn 2012-10-16 at 17:02 , Someone <someone@example.com>\nwrote:'),
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

    def test_limit(self):
        self.assertEqual(
            quote("Lorem\nIpsum\nDolor\nSit\nAmet", limit=2),
            [(True, 'Lorem\nIpsum'), (False, 'Dolor\nSit\nAmet')]
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
                (False, '''<html><head></head><body style="word-wrap: break-word; -webkit-nbsp-mode: space; -webkit-line-break: after-white-space;" class=""><div class=""><div><blockquote type="cite" class=""><br class="Apple-interchange-newline"><div class=""><div style="word-wrap: break-word; -webkit-nbsp-mode: space; -webkit-line-break: after-white-space;" class="">Lorem ipsum dolor sit amet.<div class=""><br class=""></div></div></div></blockquote></div><br class=""></div></body></html>'''),
            ]
        )

    def test_gmail(self):
        self.assertEqual(
            quote_html('''<div dir="ltr"><br><div class="gmail_quote">---------- Forwarded message ----------<br>From: <b class="gmail_sendername">Some One</b> <span dir="ltr">&lt;<a href="mailto:someone@example.com">someone@example.com</a>&gt;</span>
</div><br><br clear="all"><div><br></div>-- <br><div class="gmail_signature"><div>Some One</div></div>
</div>'''),
            [
                (True, '''<div dir="ltr"><br><div class="gmail_quote">---------- Forwarded message ----------</div></div>'''),
                (False, '''<div dir="ltr"><div class="gmail_quote">From: <b class="gmail_sendername">Some One</b> <span dir="ltr">&lt;<a href="mailto:someone@example.com">someone@example.com</a>&gt;</span>
</div><br><br clear="all"><div><br></div>-- <br><div class="gmail_signature"><div>Some One</div></div>
</div>'''),
            ]
        )

    def test_gmail_2(self):
        self.assertEqual(
            quote_html(u'''<div dir="ltr">looks good\xa0</div><div class="gmail_extra"><br><div class="gmail_quote">On Thu, Dec 18, 2014 at 10:02 AM, foo <span dir="ltr">&lt;<a href="mailto:foo@example.com" target="_blank">foo@example.com</a>&gt;</span> wrote:<blockquote class="gmail_quote" style="margin:0 0 0 .8ex;border-left:1px #ccc solid;padding-left:1ex"><div dir="ltr">Hey Phil,\xa0<div><br><div>Sending you the report:\xa0</div></div><div><span class="HOEnZb"><font color="#888888"><br></font></span></div><span class="HOEnZb"><font color="#888888"><div><br></div><div class="gmail_extra">-- <br><div><div dir="ltr"><div>Cheers,</div><div>foo &amp; example Team</div><div><a href="http://www.example.com" target="_blank">www.example.com</a> ; - <a href="mailto:help@example.com" target="_blank">help@example.com</a>\xa0</div></div></div>\r\n</div></font></span></div>\r\n</blockquote></div></div>\r\n'''),
            [
                (True, u'''<div dir="ltr">looks good\xa0</div><div class="gmail_extra"><br><div class="gmail_quote">On Thu, Dec 18, 2014 at 10:02 AM, foo <span dir="ltr">&lt;<a href="mailto:foo@example.com" target="_blank">foo@example.com</a>&gt;</span> wrote:</div></div>'''),
                (False, u'''<div class="gmail_extra"><div class="gmail_quote"><blockquote class="gmail_quote" style="margin:0 0 0 .8ex;border-left:1px #ccc solid;padding-left:1ex"><div dir="ltr">Hey Phil,\xa0<div><br><div>Sending you the report:\xa0</div></div><div><span class="HOEnZb"><font color="#888888"><br></font></span></div><span class="HOEnZb"><font color="#888888"><div><br></div><div class="gmail_extra">-- <br><div><div dir="ltr"><div>Cheers,</div><div>foo &amp; example Team</div><div><a href="http://www.example.com" target="_blank">www.example.com</a> ; - <a href="mailto:help@example.com" target="_blank">help@example.com</a>\xa0</div></div></div>\r\n</div></font></span></div>\r\n</blockquote></div></div>'''),
            ]
        )

    def test_outlook(self):
        self.assertEqual(
            quote_html(u'''<html xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word" xmlns:m="http://schemas.microsoft.com/office/2004/12/omml" xmlns="http://www.w3.org/TR/REC-html40"><head></head><body lang=EN-US link=blue vlink=purple><div class=WordSection1><p class=MsoNormal><span style='font-size:11.0pt;font-family:"Calibri","sans-serif";color:#1F497D'>Thanks,<o:p></o:p></span></p><p class=MsoNormal><span style='font-size:11.0pt;font-family:"Calibri","sans-serif";color:#1F497D'><o:p>&nbsp;</o:p></span></p><p class=MsoNormal><span style='font-size:11.0pt;font-family:"Calibri","sans-serif";color:#1F497D'><o:p>&nbsp;</o:p></span></p><div><div style='border:none;border-top:solid #B5C4DF 1.0pt;padding:3.0pt 0in 0in 0in'><p class=MsoNormal><b><span style='font-size:10.0pt;font-family:"Tahoma","sans-serif"'>From:</span></b><span style='font-size:10.0pt;font-family:"Tahoma","sans-serif"'> John Doe [mailto:john@example.com] <br><b>Sent:</b> Tuesday, December 30, 2014 5:31 PM<br><b>To:</b> recipient@example.com<br><b>Subject:</b> Excited to have you on board!<o:p></o:p></span></p></div></div><p class=MsoNormal><o:p>&nbsp;</o:p></p><p>Hey,<o:p></o:p></p></div></body></html>'''),
            [
                (True, u'<html xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word" xmlns:m="http://schemas.microsoft.com/office/2004/12/omml" xmlns="http://www.w3.org/TR/REC-html40"><head></head><body lang="EN-US" link="blue" vlink="purple"><div class="WordSection1"><p class="MsoNormal"><span style=\'font-size:11.0pt;font-family:"Calibri","sans-serif";color:#1F497D\'>Thanks,<o:p></o:p></span></p><p class="MsoNormal"><span style=\'font-size:11.0pt;font-family:"Calibri","sans-serif";color:#1F497D\'><o:p>\xa0</o:p></span></p><p class="MsoNormal"><span style=\'font-size:11.0pt;font-family:"Calibri","sans-serif";color:#1F497D\'><o:p>\xa0</o:p></span></p><div></div></div></body></html>'),
                (False, u'<html xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word" xmlns:m="http://schemas.microsoft.com/office/2004/12/omml" xmlns="http://www.w3.org/TR/REC-html40"><head></head><body lang="EN-US" link="blue" vlink="purple"><div class="WordSection1"><div><div style="border:none;border-top:solid #B5C4DF 1.0pt;padding:3.0pt 0in 0in 0in"><p class="MsoNormal"><b><span style=\'font-size:10.0pt;font-family:"Tahoma","sans-serif"\'>From:</span></b><span style=\'font-size:10.0pt;font-family:"Tahoma","sans-serif"\'> John Doe [mailto:john@example.com] <br><b>Sent:</b> Tuesday, December 30, 2014 5:31 PM<br><b>To:</b> recipient@example.com<br><b>Subject:</b> Excited to have you on board!<o:p></o:p></span></p></div></div><p class="MsoNormal"><o:p>\xa0</o:p></p><p>Hey,<o:p></o:p></p></div></body></html>')
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
                (False, u'''<div><blockquote type="cite"><div style="color:#000;"><div dir="ltr">Hi there\xa0<img src=\"https://s.yimg.com/ok/u/assets/img/emoticons/emo14.gif\" alt=\"*B-) cool\" title=\"*B-) cool\" class=\"fr-fin\"><img src=\"https://s.yimg.com/ok/u/assets/img/emoticons/emo7.gif\" alt=\"*:P tongue\" title=\"*:P tongue\" class=\"fr-fin\"><img src=\"https://s.yimg.com/ok/u/assets/img/emoticons/emo72.gif\" alt=\"*:-&gt;~~ spooky\" title=\"*:-&gt;~~ spooky\" class=\"fr-fin\"></div></div></blockquote></div>''')
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

    def test_comment_3(self):
        self.assertEqual(
            quote_html(u'''<!-- test --><br><br>Begin forwarded message:<br><br><!-- test -->'''),
            [
                (True, '<!-- test --><br><br>Begin forwarded message:'),
                (False, '<br><!-- test -->'),
            ]
        )

    def test_prefix_tag(self):
        self.assertEqual(
            quote_html(u'''A<br>Begin forwarded message:<o:p></o:p>B'''),
            [
                (True, 'A<br>Begin forwarded message:<o:p></o:p>B'),
            ]
        )

    def test_prefix_tag_2(self):
        # We can't preserve the exact markup due to lxml's parsing here.
        self.assertEqual(
            quote_html(u'''A<br>Begin forwarded message:<http://test>B'''),
            [
                (True, 'A<br>Begin forwarded message:<http:>B</http:>'),
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
test ä
</body>
</html>'''),
        ])

    def test_newline(self):
        # Newline in "Am\r\n26. Mai" should not change the way we match.
        self.assertEqual(
            quote_html(u'''<html>\r\n<head>\r\n\r\n</head>\r\n<body>\r\n<div style="color: black;">\r\n<div style="color: black;">\r\n<p style="margin: 0 0 1em 0; color: black;">Here is spam.<br>\r\nHam</p>\r\n</div>\r\n<div style="color: black;">\r\n<p\r\nstyle="color: black; font-size: 10pt; font-family: Arial, sans-serif; margin: 10pt 0;">Am\r\n26. Mai 2015 19:20:17 schrieb Spam Foo &lt;spam@example.com&gt;:</p>\r\n<blockquote type="cite" class="gmail_quote"\r\nstyle="margin: 0 0 0 0.75ex; border-left: 1px solid #808080; padding-left: 0.75ex;">Hey\r\nHam,<br><br>I like spam.<br></blockquote>\r\n</div>\r\n</div>\r\n</body>\r\n</html>\r\n'''), [
            (True, '<html>\r\n<head>\r\n\r\n</head>\r\n<body>\r\n<div style="color: black;">\r\n<div style="color: black;">\r\n<p style="margin: 0 0 1em 0; color: black;">Here is spam.<br>\r\nHam</p>\r\n</div>\r\n<div style="color: black;">\r\n<p style="color: black; font-size: 10pt; font-family: Arial, sans-serif; margin: 10pt 0;">Am\r\n26. Mai 2015 19:20:17 schrieb Spam Foo &lt;spam@example.com&gt;:</p></div></div></body></html>'),
            (False, '<html><head>\r\n\r\n</head>\r\n<body><div style="color: black;"><div style="color: black;"><blockquote type="cite" class="gmail_quote" style="margin: 0 0 0 0.75ex; border-left: 1px solid #808080; padding-left: 0.75ex;">Hey\r\nHam,<br><br>I like spam.<br></blockquote>\r\n</div>\r\n</div>\r\n</body>\r\n</html>')
        ])

class UnwrapTestCase(unittest.TestCase):
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
        self.assertEqual(data, {
            'type': 'reply',
            'date': '2012-10-16 at 17:02',
            'from': 'Someone <someone@example.com>',
            'text_top': 'Hello world.',
            'text': 'Some quoted text',
        })

    def test_reply_2(self):
        data = unwrap("""Hello world.

On 2012-10-16 at 17:02 , Someone <
someone@example.com> wrote:

> Some quoted text
""")
        self.assertEqual(data, {
            'type': 'reply',
            'date': '2012-10-16 at 17:02',
            'from': 'Someone <someone@example.com>',
            'text_top': 'Hello world.',
            'text': 'Some quoted text',
        })

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

    def test_forward_french_apple_mail(self):
        self.assertEqual(unwrap(u'''
Text before

Début du message réexpédié :

De: "Foo Bar" <from@example.com>
Date: 14 novembre 2015 15:14:53 UTC+1
À: "'Ham Spam'" <to@example.com>
Objet: RE: The subject

Text after
'''), {
            'date': u'14 novembre 2015 15:14:53 UTC+1',
            'from': u'"Foo Bar" <from@example.com>',
            'subject': 'RE: The subject',
            'text': u'Text after',
            'text_top': u'Text before',
            'to': u'"\'Ham Spam\'" <to@example.com>',
            'type': 'forward'
        })

    def test_forward_french_thunderbird(self):
        self.assertEqual(unwrap(u'''
Text before

-------- Message transféré --------
Sujet :     Re: Some subject
Date :  Wed, 11 Nov 2015 12:31:25 +0100
De :    Foo Bar <from@example.com>
Pour :  Ham Spam <to@example.com>

Text after
'''), {
            'date': u'Wed, 11 Nov 2015 12:31:25 +0100',
            'from': u'Foo Bar <from@example.com>',
            'subject': 'Re: Some subject',
            'text': u'Text after',
            'text_top': u'Text before',
            'to': u'Ham Spam <to@example.com>',
            'type': 'forward'
        })

    def test_gmail_forward_swedish(self):
        # Gmail forward
        self.assertEqual(unwrap(u"""Hello

---------- Vidarebefordrat meddelande ----------
Från: Someone <noreply@example.com>
Datum: 26 april 2013 20:13
Ämne: Weekend Spanish classes
Till: recipient@example.com

Spanish Classes
Learn Spanish
"""), {
            'text_top': u'Hello',
            'type': u'forward',
            'from': u'Someone <noreply@example.com>',
            'date': u'26 april 2013 20:13',
            'subject': u'Weekend Spanish classes',
            'to': u'recipient@example.com',
            'text': u'Spanish Classes\nLearn Spanish',
        })

class HTMLUnwrapTestCase(FileMixin, unittest.TestCase):
    def test_simple_forward(self):
        html = u'Begin forwarded message:<br>\n<br>\nFrom: someone@example.com<br>\nTo: anyone@example.com<br>\nSubject: You won<br>\n'
        self.assertEqual(unwrap_html(html), {
            'type': 'forward',
            'from': 'someone@example.com',
            'to': 'anyone@example.com',
            'subject': 'You won',
        })

    def test_apple_forward(self):
        html = '<html><head><meta http-equiv="Content-Type" content="text/html charset=utf-8"></head><body style="word-wrap: break-word; -webkit-nbsp-mode: space; -webkit-line-break: after-white-space;" class="">test<div class=""><br class=""></div><div class="">blah<br class=""><div><br class=""><div><br class=""><blockquote type="cite" class=""><div class="">Begin forwarded message:</div><br class="Apple-interchange-newline"><div style="margin-top: 0px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px;" class=""><span style="font-family: -webkit-system-font, Helvetica Neue, Helvetica, sans-serif; color:rgba(0, 0, 0, 1.0);" class=""><b class="">From: </b></span><span style="font-family: -webkit-system-font, Helvetica Neue, Helvetica, sans-serif;" class="">Foo Bar &lt;<a href="mailto:foo@bar.example" class="">foo@bar.example</a>&gt;<br class=""></span></div><div style="margin-top: 0px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px;" class=""><span style="font-family: -webkit-system-font, Helvetica Neue, Helvetica, sans-serif; color:rgba(0, 0, 0, 1.0);" class=""><b class="">Subject: </b></span><span style="font-family: -webkit-system-font, Helvetica Neue, Helvetica, sans-serif;" class=""><b class="">The Subject</b><br class=""></span></div><div style="margin-top: 0px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px;" class=""><span style="font-family: -webkit-system-font, Helvetica Neue, Helvetica, sans-serif; color:rgba(0, 0, 0, 1.0);" class=""><b class="">Date: </b></span><span style="font-family: -webkit-system-font, Helvetica Neue, Helvetica, sans-serif;" class="">March 24, 2016 at 20:16:25 GMT+1<br class=""></span></div><div style="margin-top: 0px; margin-right: 0px; margin-bottom: 0px; margin-left: 0px;" class=""><span style="font-family: -webkit-system-font, Helvetica Neue, Helvetica, sans-serif; color:rgba(0, 0, 0, 1.0);" class=""><b class="">To: </b></span><span style="font-family: -webkit-system-font, Helvetica Neue, Helvetica, sans-serif;" class="">John Doe &lt;<a href="mailto:john@doe.example" class="">john@doe.example</a>&gt;<br class=""></span></div><br class=""><div class=""><div dir="ltr" class="">Text of the original email</div>'

        self.assertEqual(unwrap_html(html), {
            'type': 'forward',
            'subject': 'The Subject',
            'date': 'March 24, 2016 at 20:16:25 GMT+1',
            'from': 'Foo Bar <foo@bar.example>',
            'to': 'John Doe <john@doe.example>',
            'html_top': '<html><head></head><body style="word-wrap: break-word; -webkit-nbsp-mode: space; -webkit-line-break: after-white-space;" class="">test<div class=""><br class=""></div><div class="">blah</div></body></html>',
            'html': '<html><head></head><body style="word-wrap: break-word; -webkit-nbsp-mode: space; -webkit-line-break: after-white-space;" class=""><div class=""><div><div><div><div class=""><div dir="ltr" class="">Text of the original email</div></div></div></div></div></div></body></html>',

        })

    def test_gmail_forward(self):
         html = '<html><head></head><body><div dir="ltr">test<div><br></div><div>blah</div><div><br><div class="gmail_quote">---------- Forwarded message ----------<br>From: <b class="gmail_sendername">Foo Bar</b> <span dir="ltr">&lt;<a href="mailto:foo@bar.example">foo@bar.example</a>&gt;</span><br>Date: Thu, Mar 24, 2016 at 5:17 PM<br>Subject: The Subject<br>To: John Doe &lt;<a href="mailto:john@doe.example">john@doe.example</a>&gt;<br><br><br><div dir="ltr">Some text<div><br></div><div><br></div></div></div><br></div></div></body></html>'

         self.assertEqual(unwrap_html(html), {
            'type': 'forward',
            'subject': 'The Subject',
            'date': 'Thu, Mar 24, 2016 at 5:17 PM',
            'from': 'Foo Bar <foo@bar.example>',
            'to': 'John Doe <john@doe.example>',
            'html_top': '<html><head></head><body><div dir="ltr">test<div><br></div><div>blah</div></div></body></html>',
            'html': '<html><head></head><body><div dir="ltr"><div><div class="gmail_quote"><div dir="ltr">Some text</div></div></div></div></body></html>',
         })

    def test_apple_reply(self):
        html = '<html><head><meta http-equiv="Content-Type" content="text/html charset=us-ascii"></head><body style="word-wrap: break-word; -webkit-nbsp-mode: space; -webkit-line-break: after-white-space;" class="">Foo<div class=""><br class=""></div><div class="">Bar</div><div class=""><br class=""></div><div class=""><div><blockquote type="cite" class=""><div class="">On 2016-03-25, at 23:01, John Doe &lt;<a href="mailto:john@doe.example" class="">john@doe.example</a>&gt; wrote:</div><br class="Apple-interchange-newline"><div class=""><meta http-equiv="Content-Type" content="text/html charset=us-ascii" class=""><div style="word-wrap: break-word; -webkit-nbsp-mode: space; -webkit-line-break: after-white-space;" class="">Some <b class="">important</b> email<br class=""></div></div></blockquote></div><br class=""></div></body></html>'

        self.assertEqual(unwrap_html(html), {
            'type': 'reply',
            'from': 'John Doe <john@doe.example>',
            'date': '2016-03-25, at 23:01',
            'html': '<html><head></head><body style="word-wrap: break-word; -webkit-nbsp-mode: space; -webkit-line-break: after-white-space;" class=""><div class=""><div><div><div class=""><div style="word-wrap: break-word; -webkit-nbsp-mode: space; -webkit-line-break: after-white-space;" class="">Some <b class="">important</b> email</div></div></div></div></div></body></html>',
            'html_top': '<html><head></head><body style="word-wrap: break-word; -webkit-nbsp-mode: space; -webkit-line-break: after-white-space;" class="">Foo<div class=""><br class=""></div><div class="">Bar</div></body></html>',
        })

    def test_gmail_reply(self):
        html = '''<html><head></head><body><div dir="ltr">foo<div><br></div><div>bar</div></div><div class="gmail_extra"><br><div class="gmail_quote">On Wed, Mar 16, 2016 at 12:49 AM, Foo Bar <span dir="ltr">&lt;<a href="mailto:foo@bar.example" target="_blank">foo@bar.example</a>&gt;</span> wrote:<br><blockquote class="gmail_quote" style="margin:0 0 0 .8ex;border-left:1px #ccc solid;padding-left:1ex">Hi,<br>
<br>This is the reply<br>
<br>
Thanks a lot!<br>
<span class="HOEnZb"><font color="#888888">Foo<br>
<br>
</font></span></blockquote></div><br><br clear="all"><div><br></div>-- <br><div class="gmail_signature"><div dir="ltr"><div><div dir="ltr"><b>John Doe</b></div><div dir="ltr"><b>Senior Director</b><div>Some Company</div></div></div></div></div>
</div>
</body></html>'''

        self.assertEqual(unwrap_html(html), {
            'type': 'reply',
            'from': 'Foo Bar <foo@bar.example>',
            'date': 'Wed, Mar 16, 2016 at 12:49 AM',
            'html_top': '<html><head></head><body><div dir="ltr">foo<div><br></div><div>bar</div></div></body></html>',
            'html': '<html><head></head><body><div class="gmail_extra"><div class="gmail_quote"><div>Hi,<br>\n<br>This is the reply<br>\n<br>\nThanks a lot!<br>\n<span class="HOEnZb"><font color="#888888">Foo</font></span></div></div></div></body></html>',
            'html_bottom': '<html><head></head><body><div class="gmail_extra">-- <br><div class="gmail_signature"><div dir="ltr"><div><div dir="ltr"><b>John Doe</b></div><div dir="ltr"><b>Senior Director</b><div>Some Company</div></div></div></div></div>\n</div>\n</body></html>',
        })

    def test_outlook_forward(self):
        data = self.read_file('outlook_forward.html')
        result = unwrap_html(data)
        self.assertEqual(result['type'], 'forward')
        self.assertEqual(result['from'], 'John Doe')
        self.assertEqual(result['to'], 'Foo Bar (foo@bar.example)')
        self.assertEqual(result['date'], 'Wednesday, July 09, 2014 10:27 AM')
        self.assertEqual(result['subject'], 'The subject!')
        self.assert_equal_to_file(result['html'],
                                  'outlook_forward_unwrapped.html')
        self.assert_equal_to_file(result['html_top'],
                                  'outlook_forward_unwrapped_top.html')
        self.assertNotIn('html_bottom', result)

    def test_thunderbird_forward(self):
        data = self.read_file('thunderbird_forward.html')
        result = unwrap_html(data)
        self.assertEqual(result['type'], 'forward')
        self.assertEqual(result['from'], 'John Doe <johndoe@example.com>')
        self.assertEqual(result['to'], 'Foo Bar <foobar@example.com>')
        self.assertEqual(result['date'], 'Tue, 3 May 2016 14:54:27 +0200 (CEST)')
        self.assertEqual(result['subject'], 'Re: Example subject')
        self.assertNotIn('html_top', result)
        self.assert_equal_to_file(result['html'],
                                  'thunderbird_forward_unwrapped.html')
        self.assertNotIn('html_bottom', result)

    def test_mailru_forward(self):
        data = self.read_file('mailru_forward.html')
        result = unwrap_html(data)
        self.assertEqual(result['type'], 'forward')
        self.assertEqual(result['from'], u'Иван Иванов <ivanivanov@example.com>')
        self.assertEqual(result['to'], u'Петр Петров <petrpetrov@example.com>')
        self.assertEqual(result['date'], u'Среда, 14 июня 2017, 15:19 +03:00')
        self.assertEqual(result['subject'], u'Тестовая тема')
        self.assertNotIn('html_top', result)
        self.assert_equal_to_file(result['html'],
                                  'mailru_forward_unwrapped.html')
        self.assertNotIn('html_bottom', result)

class InternalTestCase(unittest.TestCase):
    def test_parse_reply(self):

        from quotequail._internal import parse_reply

        data = parse_reply(u'Am 24.02.2015 um 22:48 schrieb John Doe <john@doe.example>:')
        self.assertEqual(data, {
            'date': u'24.02.2015 um 22:48',
            'from': u'John Doe <john@doe.example>'
        })

        data = parse_reply(u'On Monday, March 7, 2016 10:19 AM, John Doe <john@doe.example> wrote:')
        self.assertEqual(data, {
            'date': u'Monday, March 7, 2016 10:19 AM',
            'from': u'John Doe <john@doe.example>'
        })

        data = parse_reply(u'On Feb 22, 2015, at 9:19 PM, John Doe <john@doe.example> wrote:')
        self.assertEqual(data, {
            'date': u'Feb 22, 2015, at 9:19 PM',
            'from': u'John Doe <john@doe.example>'
        })

        data = parse_reply(u'On 2016-03-14, at 20:26, John Doe <john@doe.example> wrote:')
        self.assertEqual(data, {
            'date': u'2016-03-14, at 20:26',
            'from': u'John Doe <john@doe.example>'
        })

        data = parse_reply(u'Le 6 janv. 2014 à 19:50, John Doe <john@doe.example> a écrit :')
        self.assertEqual(data, {
            'date': u'6 janv. 2014 \xe0 19:50',
            'from': u'John Doe <john@doe.example>'
        })

        data = parse_reply(u'Le 02.10.2013 à 11:13, John Doe <john@doe.example> a écrit :')
        self.assertEqual(data, {
            'date': u'02.10.2013 \xe0 11:13',
            'from': u'John Doe <john@doe.example>'
        })

        data = parse_reply(u'El 11/07/2012 06:13 p.m., John Doe escribió:')
        self.assertEqual(data, {
            'date': u'11/07/2012 06:13 p.m.',
            'from': u'John Doe'
        })

        data = parse_reply(u'El 06/04/2010, a las 13:13, John Doe escribió:')
        self.assertEqual(data, {
            'date': u'06/04/2010, a las 13:13',
            'from': u'John Doe'
        })

        data = parse_reply(u'2009/5/12 John Doe <john@doe.example>')
        self.assertEqual(data, {
            'date': u'2009/5/12',
            'from': u'John Doe <john@doe.example>'
        })

        data = parse_reply(u"On 8 o'clock, John Doe wrote:")
        self.assertEqual(data, {
            'date': u"8 o'clock",
            'from': u'John Doe'
        })

        # Swedish
        data = parse_reply(u'Den 24 februari 2015 22:48 skrev John Doe <john@doe.example>:')
        self.assertEqual(data, {
            'date': u'24 februari 2015 22:48',
            'from': u'John Doe <john@doe.example>'
        })

        # Brazillian portuguese
        data = parse_reply(u'Em qui, 24 de jan de 2019 às 14:31, John Doe <john@doe.example> escreveu:')
        self.assertEqual(data, {
            'date': u'qui, 24 de jan de 2019 às 14:31',
            'from': u'John Doe <john@doe.example>'
        })


class InternalHTMLTestCase(unittest.TestCase):
    def test_extract_headers(self):
        from quotequail._internal import extract_headers
        self.assertEqual(
            extract_headers([], 2),
            ({}, 0)
        )
        self.assertEqual(
            extract_headers(['test'], 2),
            ({}, 0)
        )
        self.assertEqual(
            extract_headers(['From: b', 'To: c'], 2),
            ({'from': 'b', 'to': 'c'}, 2)
        )
        self.assertEqual(
            extract_headers(['From: b', 'foo'], 2),
            ({'from': 'b foo'}, 2)
        )
        self.assertEqual(
            extract_headers(['From: b', 'foo'], 1),
            ({'from': 'b'}, 1)
        )
        self.assertEqual(
            extract_headers(['From: b', 'To: c', '', 'other line'], 2),
            ({'from': 'b', 'to': 'c'}, 2)
        )
        self.assertEqual(
            extract_headers(['From: some very very very long name <',
                             'verylong@example.com>',
                             'Subject: this is a very very very very long',
                             'subject',
                             '',
                             'other line'], 2),
            ({'from': 'some very very very long name <verylong@example.com>',
              'subject': 'this is a very very very very long subject'}, 4)
        )
        self.assertEqual(
            extract_headers(['From: some very very very long name <',
                             'verylong@example.com>'], 1),
            ({'from': 'some very very very long name <',}, 1)
        )

    def test_tree_line_generator(self):
        from quotequail import _html

        tree = _html.get_html_tree('<div>foo <span>bar</span><br>baz</div>')
        data = [result for result in _html.tree_line_generator(tree)]
        div = tree.xpath('div')[0]
        br = tree.xpath('div/br')[0]
        span = tree.xpath('div/span')[0]
        self.assertEqual(data, [
            ((div, 'begin'), (br, 'begin'), 0, 'foo bar'),
            ((br, 'end'), (div, 'end'), 0, 'baz'),
        ])
        data = [result for result in _html.tree_line_generator(tree, max_lines=1)]
        div = tree.xpath('div')[0]
        br = tree.xpath('div/br')[0]
        self.assertEqual(data, [
            ((div, 'begin'), (br, 'begin'), 0, 'foo bar'),
        ])

        tree = _html.get_html_tree('<div><h1>foo</h1>bar</div>')
        data = [result for result in _html.tree_line_generator(tree)]
        div = tree.xpath('div')[0]
        h1 = tree.xpath('div/h1')[0]
        self.assertEqual(data, [
            ((h1, 'begin'), (h1, 'end'), 0, 'foo'),
            ((h1, 'end'), (div, 'end'), 0, 'bar'),
        ])

        tree = _html.get_html_tree(
                '<div><blockquote>hi</blockquote>world</div>')
        data = [result for result in _html.tree_line_generator(tree)]
        div = tree.xpath('div')[0]
        blockquote = tree.xpath('div/blockquote')[0]
        self.assertEqual(data, [
            ((blockquote, 'begin'), (blockquote, 'end'), 1, 'hi'),
            ((blockquote, 'end'), (div, 'end'), 0, 'world'),
        ])

        tree = _html.get_html_tree('''
            <table>
                <tr><td>Subject: </td><td>the subject</td></tr>
                <tr><td>From: </td><td>from line</td></tr>
            </table>''')
        data = [result for result in _html.tree_line_generator(tree)]
        tr1, tr2 = tree.xpath('table/tr')
        self.assertEqual(data, [
            ((tr1, 'begin'), (tr1, 'end'), 0, 'Subject: the subject'),
            ((tr2, 'begin'), (tr2, 'end'), 0, 'From: from line'),
        ])

    def test_trim_after(self):
        from quotequail import _html

        html = '<div>A<span>B</span>C<span>D</span>E</div>'

        tree = _html.get_html_tree(html)
        _html.trim_tree_after(tree.find('div/span'))
        self.assertEqual(_html.render_html_tree(tree), '<div>A<span>B</span></div>')

        tree = _html.get_html_tree(html)
        _html.trim_tree_after(tree.find('div/span[2]'))
        self.assertEqual(_html.render_html_tree(tree), '<div>A<span>B</span>C<span>D</span></div>')

        tree = _html.get_html_tree(html)
        _html.trim_tree_after(tree.find('div/span'), include_element=False)
        self.assertEqual(_html.render_html_tree(tree), '<div>A</div>')

        tree = _html.get_html_tree(html)
        _html.trim_tree_after(tree.find('div/span[2]'), include_element=False)
        self.assertEqual(_html.render_html_tree(tree), '<div>A<span>B</span>C</div>')

    def test_trim_before(self):
        from quotequail import _html

        html = '<div>A<span>B</span>C<span>D</span>E</div>'

        tree = _html.get_html_tree(html)
        _html.trim_tree_before(tree.find('div/span'))
        self.assertEqual(_html.render_html_tree(tree), '<div><span>B</span>C<span>D</span>E</div>')

        tree = _html.get_html_tree(html)
        _html.trim_tree_before(tree.find('div/span[2]'))
        self.assertEqual(_html.render_html_tree(tree), '<div><span>D</span>E</div>')

        tree = _html.get_html_tree(html)
        _html.trim_tree_before(tree.find('div/span'), include_element=False)
        self.assertEqual(_html.render_html_tree(tree), '<div>C<span>D</span>E</div>')

        tree = _html.get_html_tree(html)
        _html.trim_tree_before(tree.find('div/span[2]'), include_element=False)
        self.assertEqual(_html.render_html_tree(tree), '<div>E</div>')

if __name__ == '__main__':
    unittest.main()

