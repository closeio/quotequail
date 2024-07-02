import pytest

from quotequail import quote_html


@pytest.mark.parametrize(
    ("html", "expected", "expected_quote_intro_line"),
    [
        # Apple
        (
            """<html><head><meta http-equiv="Content-Type" content="text/html charset=us-ascii"></head><body style="word-wrap: break-word; -webkit-nbsp-mode: space; -webkit-line-break: after-white-space;" class="">Some text<div class=""><br class=""></div><div class="">some more text</div><div class=""><br class=""></div><div class=""><br class=""><div><blockquote type="cite" class=""><div class="">On Nov 12, 2014, at 11:07 PM, Some One &lt;<a href="mailto:someone@example.com" class="">someone@example.com</a>&gt; wrote:</div><br class="Apple-interchange-newline"><div class=""><meta http-equiv="Content-Type" content="text/html charset=us-ascii" class=""><div style="word-wrap: break-word; -webkit-nbsp-mode: space; -webkit-line-break: after-white-space;" class="">Lorem ipsum dolor sit amet.<div class=""><br class=""></div></div></div></blockquote></div><br class=""></div></body></html>""",
            [
                # Note that lxml removes Content-Type meta tags (see
                # lxml.html.tostring include_meta_content_type flag)
                (
                    True,
                    """<html><head></head><body style="word-wrap: break-word; -webkit-nbsp-mode: space; -webkit-line-break: after-white-space;" class="">Some text<div class=""><br class=""></div><div class="">some more text</div><div class=""><br class=""></div><div class=""><br class=""><div><blockquote type="cite" class=""><div class="">On Nov 12, 2014, at 11:07 PM, Some One &lt;<a href="mailto:someone@example.com" class="">someone@example.com</a>&gt; wrote:</div></blockquote></div></div></body></html>""",
                ),
                # Note we have an empty div stripped out here.
                (
                    False,
                    """<html><head></head><body style="word-wrap: break-word; -webkit-nbsp-mode: space; -webkit-line-break: after-white-space;" class=""><div class=""><div><blockquote type="cite" class=""><br class="Apple-interchange-newline"><div class=""><div style="word-wrap: break-word; -webkit-nbsp-mode: space; -webkit-line-break: after-white-space;" class="">Lorem ipsum dolor sit amet.<div class=""><br class=""></div></div></div></blockquote></div><br class=""></div></body></html>""",
                ),
            ],
            [
                (
                    True,
                    '<html><head></head><body style="word-wrap: break-word; -webkit-nbsp-mode: space; -webkit-line-break: after-white-space;" class="">Some text<div class=""><br class=""></div><div class="">some more text</div><div class=""><br class=""></div><div class=""></div></body></html>',
                ),
                (
                    False,
                    '<html><head></head><body style="word-wrap: break-word; -webkit-nbsp-mode: space; -webkit-line-break: after-white-space;" class=""><div class=""><div><blockquote type="cite" class=""><div class="">On Nov 12, 2014, at 11:07 PM, Some One &lt;<a href="mailto:someone@example.com" class="">someone@example.com</a>&gt; wrote:</div><br class="Apple-interchange-newline"><div class=""><div style="word-wrap: break-word; -webkit-nbsp-mode: space; -webkit-line-break: after-white-space;" class="">Lorem ipsum dolor sit amet.<div class=""><br class=""></div></div></div></blockquote></div><br class=""></div></body></html>',
                ),
            ],
        ),
        # Gmail (1)
        (
            """<div dir="ltr"><br><div class="gmail_quote">---------- Forwarded message ----------<br>From: <b class="gmail_sendername">Some One</b> <span dir="ltr">&lt;<a href="mailto:someone@example.com">someone@example.com</a>&gt;</span>
</div><br><br clear="all"><div><br></div>-- <br><div class="gmail_signature"><div>Some One</div></div>
</div>""",
            [
                (
                    True,
                    """<div dir="ltr"><br><div class="gmail_quote">---------- Forwarded message ----------</div></div>""",
                ),
                (
                    False,
                    """<div dir="ltr"><div class="gmail_quote">From: <b class="gmail_sendername">Some One</b> <span dir="ltr">&lt;<a href="mailto:someone@example.com">someone@example.com</a>&gt;</span>
</div><br><br clear="all"><div><br></div>-- <br><div class="gmail_signature"><div>Some One</div></div>
</div>""",
                ),
            ],
            [
                (True, '<div dir="ltr"></div>'),
                (
                    False,
                    '<div dir="ltr"><div class="gmail_quote">---------- Forwarded message ----------<br>From: <b class="gmail_sendername">Some One</b> <span dir="ltr">&lt;<a href="mailto:someone@example.com">someone@example.com</a>&gt;</span>\n</div><br><br clear="all"><div><br></div>-- <br><div class="gmail_signature"><div>Some One</div></div>\n</div>',
                ),
            ],
        ),
        # Gmail (2)
        (
            """<div dir="ltr">looks good\xa0</div><div class="gmail_extra"><br><div class="gmail_quote">On Thu, Dec 18, 2014 at 10:02 AM, foo <span dir="ltr">&lt;<a href="mailto:foo@example.com" target="_blank">foo@example.com</a>&gt;</span> wrote:<blockquote class="gmail_quote" style="margin:0 0 0 .8ex;border-left:1px #ccc solid;padding-left:1ex"><div dir="ltr">Hey Phil,\xa0<div><br><div>Sending you the report:\xa0</div></div><div><span class="HOEnZb"><font color="#888888"><br></font></span></div><span class="HOEnZb"><font color="#888888"><div><br></div><div class="gmail_extra">-- <br><div><div dir="ltr"><div>Cheers,</div><div>foo &amp; example Team</div><div><a href="http://www.example.com" target="_blank">www.example.com</a> ; - <a href="mailto:help@example.com" target="_blank">help@example.com</a>\xa0</div></div></div>\r\n</div></font></span></div>\r\n</blockquote></div></div>\r\n""",
            [
                (
                    True,
                    """<div dir="ltr">looks good\xa0</div><div class="gmail_extra"><br><div class="gmail_quote">On Thu, Dec 18, 2014 at 10:02 AM, foo <span dir="ltr">&lt;<a href="mailto:foo@example.com" target="_blank">foo@example.com</a>&gt;</span> wrote:</div></div>""",
                ),
                (
                    False,
                    """<div class="gmail_extra"><div class="gmail_quote"><blockquote class="gmail_quote" style="margin:0 0 0 .8ex;border-left:1px #ccc solid;padding-left:1ex"><div dir="ltr">Hey Phil,\xa0<div><br><div>Sending you the report:\xa0</div></div><div><span class="HOEnZb"><font color="#888888"><br></font></span></div><span class="HOEnZb"><font color="#888888"><div><br></div><div class="gmail_extra">-- <br><div><div dir="ltr"><div>Cheers,</div><div>foo &amp; example Team</div><div><a href="http://www.example.com" target="_blank">www.example.com</a> ; - <a href="mailto:help@example.com" target="_blank">help@example.com</a>\xa0</div></div></div>\r\n</div></font></span></div>\r\n</blockquote></div></div>""",
                ),
            ],
            [
                (
                    True,
                    '<div dir="ltr">looks good\xa0</div><div class="gmail_extra"></div>',
                ),
                (
                    False,
                    '<div class="gmail_extra"><div class="gmail_quote">On Thu, Dec 18, 2014 at 10:02 AM, foo <span dir="ltr">&lt;<a href="mailto:foo@example.com" target="_blank">foo@example.com</a>&gt;</span> wrote:<blockquote class="gmail_quote" style="margin:0 0 0 .8ex;border-left:1px #ccc solid;padding-left:1ex"><div dir="ltr">Hey Phil,\xa0<div><br><div>Sending you the report:\xa0</div></div><div><span class="HOEnZb"><font color="#888888"><br></font></span></div><span class="HOEnZb"><font color="#888888"><div><br></div><div class="gmail_extra">-- <br><div><div dir="ltr"><div>Cheers,</div><div>foo &amp; example Team</div><div><a href="http://www.example.com" target="_blank">www.example.com</a> ; - <a href="mailto:help@example.com" target="_blank">help@example.com</a>\xa0</div></div></div>\r\n</div></font></span></div>\r\n</blockquote></div></div>',
                ),
            ],
        ),
        # Outlook
        (
            """<html xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word" xmlns:m="http://schemas.microsoft.com/office/2004/12/omml" xmlns="http://www.w3.org/TR/REC-html40"><head></head><body lang=EN-US link=blue vlink=purple><div class=WordSection1><p class=MsoNormal><span style='font-size:11.0pt;font-family:"Calibri","sans-serif";color:#1F497D'>Thanks,<o:p></o:p></span></p><p class=MsoNormal><span style='font-size:11.0pt;font-family:"Calibri","sans-serif";color:#1F497D'><o:p>&nbsp;</o:p></span></p><p class=MsoNormal><span style='font-size:11.0pt;font-family:"Calibri","sans-serif";color:#1F497D'><o:p>&nbsp;</o:p></span></p><div><div style='border:none;border-top:solid #B5C4DF 1.0pt;padding:3.0pt 0in 0in 0in'><p class=MsoNormal><b><span style='font-size:10.0pt;font-family:"Tahoma","sans-serif"'>From:</span></b><span style='font-size:10.0pt;font-family:"Tahoma","sans-serif"'> John Doe [mailto:john@example.com] <br><b>Sent:</b> Tuesday, December 30, 2014 5:31 PM<br><b>To:</b> recipient@example.com<br><b>Subject:</b> Excited to have you on board!<o:p></o:p></span></p></div></div><p class=MsoNormal><o:p>&nbsp;</o:p></p><p>Hey,<o:p></o:p></p></div></body></html>""",
            [
                (
                    True,
                    '<html xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word" xmlns:m="http://schemas.microsoft.com/office/2004/12/omml" xmlns="http://www.w3.org/TR/REC-html40"><head></head><body lang="EN-US" link="blue" vlink="purple"><div class="WordSection1"><p class="MsoNormal"><span style=\'font-size:11.0pt;font-family:"Calibri","sans-serif";color:#1F497D\'>Thanks,<o:p></o:p></span></p><p class="MsoNormal"><span style=\'font-size:11.0pt;font-family:"Calibri","sans-serif";color:#1F497D\'><o:p>\xa0</o:p></span></p><p class="MsoNormal"><span style=\'font-size:11.0pt;font-family:"Calibri","sans-serif";color:#1F497D\'><o:p>\xa0</o:p></span></p><div></div></div></body></html>',
                ),
                (
                    False,
                    '<html xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word" xmlns:m="http://schemas.microsoft.com/office/2004/12/omml" xmlns="http://www.w3.org/TR/REC-html40"><head></head><body lang="EN-US" link="blue" vlink="purple"><div class="WordSection1"><div><div style="border:none;border-top:solid #B5C4DF 1.0pt;padding:3.0pt 0in 0in 0in"><p class="MsoNormal"><b><span style=\'font-size:10.0pt;font-family:"Tahoma","sans-serif"\'>From:</span></b><span style=\'font-size:10.0pt;font-family:"Tahoma","sans-serif"\'> John Doe [mailto:john@example.com] <br><b>Sent:</b> Tuesday, December 30, 2014 5:31 PM<br><b>To:</b> recipient@example.com<br><b>Subject:</b> Excited to have you on board!<o:p></o:p></span></p></div></div><p class="MsoNormal"><o:p>\xa0</o:p></p><p>Hey,<o:p></o:p></p></div></body></html>',
                ),
            ],
            [
                (
                    True,
                    '<html xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word" xmlns:m="http://schemas.microsoft.com/office/2004/12/omml" xmlns="http://www.w3.org/TR/REC-html40"><head></head><body lang="EN-US" link="blue" vlink="purple"><div class="WordSection1"><p class="MsoNormal"><span style=\'font-size:11.0pt;font-family:"Calibri","sans-serif";color:#1F497D\'>Thanks,<o:p></o:p></span></p><p class="MsoNormal"><span style=\'font-size:11.0pt;font-family:"Calibri","sans-serif";color:#1F497D\'><o:p>\xa0</o:p></span></p><p class="MsoNormal"><span style=\'font-size:11.0pt;font-family:"Calibri","sans-serif";color:#1F497D\'><o:p>\xa0</o:p></span></p><div></div></div></body></html>',
                ),
                (
                    False,
                    '<html xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word" xmlns:m="http://schemas.microsoft.com/office/2004/12/omml" xmlns="http://www.w3.org/TR/REC-html40"><head></head><body lang="EN-US" link="blue" vlink="purple"><div class="WordSection1"><div><div style="border:none;border-top:solid #B5C4DF 1.0pt;padding:3.0pt 0in 0in 0in"><p class="MsoNormal"><b><span style=\'font-size:10.0pt;font-family:"Tahoma","sans-serif"\'>From:</span></b><span style=\'font-size:10.0pt;font-family:"Tahoma","sans-serif"\'> John Doe [mailto:john@example.com] <br><b>Sent:</b> Tuesday, December 30, 2014 5:31 PM<br><b>To:</b> recipient@example.com<br><b>Subject:</b> Excited to have you on board!<o:p></o:p></span></p></div></div><p class="MsoNormal"><o:p>\xa0</o:p></p><p>Hey,<o:p></o:p></p></div></body></html>',
                ),
            ],
        ),
        # Newline in "Am\r\n26. Mai" should not change the way we match.
        (
            """<html>\r\n<head>\r\n\r\n</head>\r\n<body>\r\n<div style="color: black;">\r\n<div style="color: black;">\r\n<p style="margin: 0 0 1em 0; color: black;">Here is spam.<br>\r\nHam</p>\r\n</div>\r\n<div style="color: black;">\r\n<p\r\nstyle="color: black; font-size: 10pt; font-family: Arial, sans-serif; margin: 10pt 0;">Am\r\n26. Mai 2015 19:20:17 schrieb Spam Foo &lt;spam@example.com&gt;:</p>\r\n<blockquote type="cite" class="gmail_quote"\r\nstyle="margin: 0 0 0 0.75ex; border-left: 1px solid #808080; padding-left: 0.75ex;">Hey\r\nHam,<br><br>I like spam.<br></blockquote>\r\n</div>\r\n</div>\r\n</body>\r\n</html>\r\n""",
            [
                (
                    True,
                    '<html>\r\n<head>\r\n\r\n</head>\r\n<body>\r\n<div style="color: black;">\r\n<div style="color: black;">\r\n<p style="margin: 0 0 1em 0; color: black;">Here is spam.<br>\r\nHam</p>\r\n</div>\r\n<div style="color: black;">\r\n<p style="color: black; font-size: 10pt; font-family: Arial, sans-serif; margin: 10pt 0;">Am\r\n26. Mai 2015 19:20:17 schrieb Spam Foo &lt;spam@example.com&gt;:</p></div></div></body></html>',
                ),
                (
                    False,
                    '<html><head>\r\n\r\n</head>\r\n<body><div style="color: black;"><div style="color: black;"><blockquote type="cite" class="gmail_quote" style="margin: 0 0 0 0.75ex; border-left: 1px solid #808080; padding-left: 0.75ex;">Hey\r\nHam,<br><br>I like spam.<br></blockquote>\r\n</div>\r\n</div>\r\n</body>\r\n</html>',
                ),
            ],
            [
                (
                    True,
                    '<html>\r\n<head>\r\n\r\n</head>\r\n<body>\r\n<div style="color: black;">\r\n<div style="color: black;">\r\n<p style="margin: 0 0 1em 0; color: black;">Here is spam.<br>\r\nHam</p></div></div></body></html>',
                ),
                (
                    False,
                    '<html><head>\r\n\r\n</head>\r\n<body><div style="color: black;"><div style="color: black;"><p style="color: black; font-size: 10pt; font-family: Arial, sans-serif; margin: 10pt 0;">Am\r\n26. Mai 2015 19:20:17 schrieb Spam Foo &lt;spam@example.com&gt;:</p>\r\n<blockquote type="cite" class="gmail_quote" style="margin: 0 0 0 0.75ex; border-left: 1px solid #808080; padding-left: 0.75ex;">Hey\r\nHam,<br><br>I like spam.<br></blockquote>\r\n</div>\r\n</div>\r\n</body>\r\n</html>',
                ),
            ],
        ),
        # No wrap tag.
        (
            """On Thu, Dec 18, 2014 at 10:02 AM, foo &lt;foo@example.com&gt; wrote:<blockquote>some stuff</blockquote>""",
            [
                (
                    True,
                    "On Thu, Dec 18, 2014 at 10:02 AM, foo &lt;foo@example.com&gt; wrote:",
                ),
                (False, "<blockquote>some stuff</blockquote>"),
            ],
            [
                (
                    True,
                    "",
                ),
                (
                    False,
                    "On Thu, Dec 18, 2014 at 10:02 AM, foo &lt;foo@example.com&gt; wrote:<blockquote>some stuff</blockquote>",
                ),
            ],
        ),
        # Images
        (
            """<div>Well hello there Sir!!!<br><br><br>On Dec 23, 2014, at 04:35 PM, Steve Wiseman &lt;wiseman.steve@ymail.com&gt; wrote:<br><blockquote type=\"cite\"><div style=\"color:#000;\"><div dir=\"ltr\">Hi there&nbsp;<img src=\"https://s.yimg.com/ok/u/assets/img/emoticons/emo14.gif\" alt=\"*B-) cool\" title=\"*B-) cool\" class=\"fr-fin\"><img src=\"https://s.yimg.com/ok/u/assets/img/emoticons/emo7.gif\" alt=\"*:P tongue\" title=\"*:P tongue\" class=\"fr-fin\"><img src=\"https://s.yimg.com/ok/u/assets/img/emoticons/emo72.gif\" alt=\"*:->~~ spooky\" title=\"*:->~~ spooky\" class=\"fr-fin\"></div></div></blockquote></div>""",
            [
                (
                    True,
                    """<div>Well hello there Sir!!!<br><br><br>On Dec 23, 2014, at 04:35 PM, Steve Wiseman &lt;wiseman.steve@ymail.com&gt; wrote:</div>""",
                ),
                (
                    False,
                    """<div><blockquote type="cite"><div style="color:#000;"><div dir="ltr">Hi there\xa0<img src=\"https://s.yimg.com/ok/u/assets/img/emoticons/emo14.gif\" alt=\"*B-) cool\" title=\"*B-) cool\" class=\"fr-fin\"><img src=\"https://s.yimg.com/ok/u/assets/img/emoticons/emo7.gif\" alt=\"*:P tongue\" title=\"*:P tongue\" class=\"fr-fin\"><img src=\"https://s.yimg.com/ok/u/assets/img/emoticons/emo72.gif\" alt=\"*:-&gt;~~ spooky\" title=\"*:-&gt;~~ spooky\" class=\"fr-fin\"></div></div></blockquote></div>""",
                ),
            ],
            [
                (
                    True,
                    """<div>Well hello there Sir!!!<br><br></div>""",
                ),
                (
                    False,
                    """<div>On Dec 23, 2014, at 04:35 PM, Steve Wiseman &lt;wiseman.steve@ymail.com&gt; wrote:<br><blockquote type="cite"><div style="color:#000;"><div dir="ltr">Hi there\xa0<img src=\"https://s.yimg.com/ok/u/assets/img/emoticons/emo14.gif\" alt=\"*B-) cool\" title=\"*B-) cool\" class=\"fr-fin\"><img src=\"https://s.yimg.com/ok/u/assets/img/emoticons/emo7.gif\" alt=\"*:P tongue\" title=\"*:P tongue\" class=\"fr-fin\"><img src=\"https://s.yimg.com/ok/u/assets/img/emoticons/emo72.gif\" alt=\"*:-&gt;~~ spooky\" title=\"*:-&gt;~~ spooky\" class=\"fr-fin\"></div></div></blockquote></div>""",
                ),
            ],
        ),
    ],
)
def test_quote_html(html, expected, expected_quote_intro_line):
    assert quote_html(html) == expected
    assert quote_html(html, quote_intro_line=True) == expected_quote_intro_line


def test_no_quote():
    assert quote_html("""<p>One</p><p>Two</p><p>Three</p>""") == [
        (True, "<p>One</p><p>Two</p><p>Three</p>"),
    ]


def test_limit():
    assert quote_html(
        """<p>One</p><p>Two</p><p>Three</p><p>Four</p>""", limit=3
    ) == [
        (True, "<p>One</p><p>Two</p><p>Three</p>"),
        (False, "<p>Four</p>"),
    ]


def test_empty():
    assert quote_html("") == [
        (True, ""),
    ]


def test_comment():
    assert quote_html("""<!-- test -->""") == [
        (True, "<!-- test -->"),
    ]


def test_comment_2():
    assert quote_html("""A<!-- test -->B""") == [
        (True, "A<!-- test -->B"),
    ]


def test_comment_3():
    assert quote_html(
        """<!-- test --><br><br>Begin forwarded message:<br><br><!-- test -->"""
    ) == [
        (True, "<!-- test --><br><br>Begin forwarded message:"),
        (False, "<br><!-- test -->"),
    ]


def test_prefix_tag():
    assert quote_html("""A<br>Begin forwarded message:<o:p></o:p>B""") == [
        (True, "A<br>Begin forwarded message:<o:p></o:p>B"),
    ]


def test_prefix_tag_2():
    # We can't preserve the exact markup due to lxml's parsing here.
    assert quote_html("""A<br>Begin forwarded message:<http://test>B""") == [
        (True, "A<br>Begin forwarded message:<http:>B</http:>"),
    ]


def test_encoding():
    # We assume everything is UTF-8
    assert quote_html("""<?xml version="1.0" encoding="ISO-8859-1"?>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1" />
<title></title>
</head>
<body>
test ä
</body>
</html>""") == [
        (
            True,
            """<html xmlns="http://www.w3.org/1999/xhtml">
<head>

<title></title>
</head>
<body>
test ä
</body>
</html>""",
        ),
    ]
