import pytest

from quotequail import unwrap_html


@pytest.mark.parametrize(
    ("html", "expected"),
    [
        ("<p>html text</p>", None),
        (
            "Begin forwarded message:<br>\n<br>\nFrom: someone@example.com<br>\nTo: anyone@example.com<br>\nSubject: You won<br>\n",
            {
                "type": "forward",
                "from": "someone@example.com",
                "to": "anyone@example.com",
                "subject": "You won",
            },
        ),
    ],
)
def test_unwrap_html_simple(html, expected):
    assert unwrap_html(html) == expected


@pytest.mark.parametrize(
    ("file", "expected"),
    [
        (
            "apple_forward.html",
            {
                "type": "forward",
                "subject": "The Subject",
                "date": "March 24, 2016 at 20:16:25 GMT+1",
                "from": "Foo Bar <foo@bar.example>",
                "to": "John Doe <john@doe.example>",
                "html_top": '<html><head></head><body style="word-wrap: break-word; -webkit-nbsp-mode: space; -webkit-line-break: after-white-space;" class="">test<div class=""><br class=""></div><div class="">blah</div></body></html>',
                "html": '<html><head></head><body style="word-wrap: break-word; -webkit-nbsp-mode: space; -webkit-line-break: after-white-space;" class=""><div class=""><div><div><div><div class=""><div dir="ltr" class="">Text of the original email</div></div></div></div></div></div></body></html>',
            },
        ),
        (
            "gmail_forward.html",
            {
                "type": "forward",
                "subject": "The Subject",
                "date": "Thu, Mar 24, 2016 at 5:17 PM",
                "from": "Foo Bar <foo@bar.example>",
                "to": "John Doe <john@doe.example>",
                "html_top": '<html><head></head><body><div dir="ltr">test<div><br></div><div>blah</div></div></body></html>',
                "html": '<html><head></head><body><div dir="ltr"><div><div class="gmail_quote"><div dir="ltr">Some text</div></div></div></div></body></html>',
            },
        ),
        (
            "apple_reply.html",
            {
                "type": "reply",
                "from": "John Doe <john@doe.example>",
                "date": "2016-03-25, at 23:01",
                "html": '<html><head></head><body style="word-wrap: break-word; -webkit-nbsp-mode: space; -webkit-line-break: after-white-space;" class=""><div class=""><div><div><div class=""><div style="word-wrap: break-word; -webkit-nbsp-mode: space; -webkit-line-break: after-white-space;" class="">Some <b class="">important</b> email</div></div></div></div></div></body></html>',
                "html_top": '<html><head></head><body style="word-wrap: break-word; -webkit-nbsp-mode: space; -webkit-line-break: after-white-space;" class="">Foo<div class=""><br class=""></div><div class="">Bar</div></body></html>',
            },
        ),
        (
            "gmail_reply.html",
            {
                "type": "reply",
                "from": "Foo Bar <foo@bar.example>",
                "date": "Wed, Mar 16, 2016 at 12:49 AM",
                "html_top": '<html><head></head><body><div dir="ltr">foo<div><br></div><div>bar</div></div></body></html>',
                "html": '<html><head></head><body><div class="gmail_extra"><div class="gmail_quote"><div>Hi,<br>\n<br>This is the reply<br>\n<br>\nThanks a lot!<br>\n<span class="HOEnZb"><font color="#888888">Foo</font></span></div></div></div></body></html>',
                "html_bottom": '<html><head></head><body><div class="gmail_extra">-- <br><div class="gmail_signature"><div dir="ltr"><div><div dir="ltr"><b>John Doe</b></div><div dir="ltr"><b>Senior Director</b><div>Some Company</div></div></div></div></div>\n</div>\n</body></html>',
            },
        ),
    ],
)
def test_unwrap_html_file(read_file, file, expected):
    html = read_file(file)
    assert unwrap_html(html) == expected


def test_outlook_forward(read_file):
    data = read_file("outlook_forward.html")
    result = unwrap_html(data)
    assert result["type"] == "forward"
    assert result["from"] == "John Doe"
    assert result["to"] == "Foo Bar (foo@bar.example)"
    assert result["date"] == "Wednesday, July 09, 2014 10:27 AM"
    assert result["subject"] == "The subject!"
    assert result["html"] == read_file("outlook_forward_unwrapped.html")
    assert result["html_top"] == read_file(
        "outlook_forward_unwrapped_top.html"
    )
    assert "html_bottom" not in result


def test_thunderbird_forward(read_file):
    data = read_file("thunderbird_forward.html")
    result = unwrap_html(data)
    assert result["type"] == "forward"
    assert result["from"] == "John Doe <johndoe@example.com>"
    assert result["to"] == "Foo Bar <foobar@example.com>"
    assert result["date"] == "Tue, 3 May 2016 14:54:27 +0200 (CEST)"
    assert result["subject"] == "Re: Example subject"
    assert "html_top" not in result
    assert result["html"] == read_file("thunderbird_forward_unwrapped.html")
    assert "html_bottom" not in result


def test_unwrap_html_with_email_address_pseudo_tag():
    # Some quoted-reply headers contain bare ``Name <addr@domain>`` text. With
    # lxml >= 6.0 the HTML parser keeps ``<addr@domain>`` as an element with a
    # tag name containing ``@``. ``getelementpath()`` then emits that raw name
    # as a path component, which the elementpath tokenizer used by ``find()``
    # rejects (``@`` is the attribute axis token), raising ``KeyError: '@'``.
    # ``unwrap_html`` should be resilient to that.
    html = (
        "Hey Jane,<br><br>Some reply text.<br>Dan"
        '<div><span data-system-generated="meta">'
        "On Sep 04, 2025, 11:30 AM, "
        "Jane Roe <jane@example.com> wrote:<br>"
        "</span></div>"
        "<blockquote>Original message body</blockquote>"
    )

    # The important guarantee is that ``unwrap_html`` doesn't crash and
    # returns sensible top/quoted content. The detected ``type`` differs
    # slightly between lxml versions (lxml 5 strips the bogus ``<jane@...>``
    # tag at parse time, lxml 6 keeps it; we then coerce it to ``<span>``),
    # so we don't pin the exact value.
    result = unwrap_html(html)

    assert result is not None
    assert result["type"] in {"quote", "reply"}
    assert "Some reply text" in result["html_top"]
    assert "Original message body" in result["html"]


def test_mailru_forward(read_file):
    data = read_file("mailru_forward.html")
    result = unwrap_html(data)
    assert result["type"] == "forward"
    assert result["from"] == "Иван Иванов <ivanivanov@example.com>"
    assert result["to"] == "Петр Петров <petrpetrov@example.com>"
    assert result["date"] == "Среда, 14 июня 2017, 15:19 +03:00"
    assert result["subject"] == "Тестовая тема"
    assert "html_top" not in result
    assert result["html"] == read_file("mailru_forward_unwrapped.html")
    assert "html_bottom" not in result
