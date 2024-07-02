import pytest

from quotequail._internal import extract_headers, parse_reply


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        # German
        (
            "Am 24.02.2015 um 22:48 schrieb John Doe <john@doe.example>:",
            {
                "date": "24.02.2015 um 22:48",
                "from": "John Doe <john@doe.example>",
            },
        ),
        # English
        (
            "On Monday, March 7, 2016 10:19 AM, John Doe <john@doe.example> wrote:",
            {
                "date": "Monday, March 7, 2016 10:19 AM",
                "from": "John Doe <john@doe.example>",
            },
        ),
        (
            "On Feb 22, 2015, at 9:19 PM, John Doe <john@doe.example> wrote:",
            {
                "date": "Feb 22, 2015, at 9:19 PM",
                "from": "John Doe <john@doe.example>",
            },
        ),
        (
            "On 2016-03-14, at 20:26, John Doe <john@doe.example> wrote:",
            {
                "date": "2016-03-14, at 20:26",
                "from": "John Doe <john@doe.example>",
            },
        ),
        (
            "On 8 o'clock, John Doe wrote:",
            {"date": "8 o'clock", "from": "John Doe"},
        ),
        # French
        (
            "Le 6 janv. 2014 à 19:50, John Doe <john@doe.example> a écrit :",
            {
                "date": "6 janv. 2014 \xe0 19:50",
                "from": "John Doe <john@doe.example>",
            },
        ),
        (
            "Le 02.10.2013 à 11:13, John Doe <john@doe.example> a écrit :",
            {
                "date": "02.10.2013 \xe0 11:13",
                "from": "John Doe <john@doe.example>",
            },
        ),
        # Spanish
        (
            "El 11/07/2012 06:13 p.m., John Doe escribió:",
            {"date": "11/07/2012 06:13 p.m.", "from": "John Doe"},
        ),
        (
            "El 06/04/2010, a las 13:13, John Doe escribió:",
            {"date": "06/04/2010, a las 13:13", "from": "John Doe"},
        ),
        # Swedish
        (
            "Den 24 februari 2015 22:48 skrev John Doe <john@doe.example>:",
            {
                "date": "24 februari 2015 22:48",
                "from": "John Doe <john@doe.example>",
            },
        ),
        # Brazillian portuguese
        (
            "Em qui, 24 de jan de 2019 às 14:31, John Doe <john@doe.example> escreveu:",
            {
                "date": "qui, 24 de jan de 2019 às 14:31",
                "from": "John Doe <john@doe.example>",
            },
        ),
        # Other
        (
            "2009/5/12 John Doe <john@doe.example>",
            {"date": "2009/5/12", "from": "John Doe <john@doe.example>"},
        ),
    ],
)
def test_parse_reply(line, expected):
    assert parse_reply(line) == expected


def test_extract_headers():
    assert extract_headers([], 2) == ({}, 0)
    assert extract_headers(["test"], 2) == ({}, 0)
    assert extract_headers(["From: b", "To: c"], 2) == (
        {"from": "b", "to": "c"},
        2,
    )
    assert extract_headers(["From: b", "foo"], 2) == ({"from": "b foo"}, 2)
    assert extract_headers(["From: b", "foo"], 1) == ({"from": "b"}, 1)
    assert extract_headers(["From: b", "To: c", "", "other line"], 2) == (
        {"from": "b", "to": "c"},
        2,
    )
    assert extract_headers(
        [
            "From: some very very very long name <",
            "verylong@example.com>",
            "Subject: this is a very very very very long",
            "subject",
            "",
            "other line",
        ],
        2,
    ) == (
        {
            "from": "some very very very long name <verylong@example.com>",
            "subject": "this is a very very very very long subject",
        },
        4,
    )
    assert extract_headers(
        [
            "From: some very very very long name <",
            "verylong@example.com>",
        ],
        1,
    ) == (
        {
            "from": "some very very very long name <",
        },
        1,
    )
