import pytest

from quotequail import quote


@pytest.mark.parametrize(
    ("text", "expected", "expected_quote_intro_line"),
    [
        # Reply patterns.
        (
            """Hello world.

On 2012-10-16 at 17:02 , Someone <someone@example.com> wrote:

> Some quoted text
""",
            [
                (
                    True,
                    "Hello world.\n\nOn 2012-10-16 at 17:02 , Someone <someone@example.com> wrote:",
                ),
                (False, "\n> Some quoted text\n"),
            ],
            [
                (
                    True,
                    "Hello world.\n",
                ),
                (
                    False,
                    "On 2012-10-16 at 17:02 , Someone <someone@example.com> wrote:\n\n> Some quoted text\n",
                ),
            ],
        ),
        (
            """Hello world.

On 2012-10-16 at 17:02 , Someone <
someone@example.com> wrote:

> Some quoted text
""",
            [
                (
                    True,
                    "Hello world.\n\nOn 2012-10-16 at 17:02 , Someone <\nsomeone@example.com> wrote:",
                ),
                (False, "\n> Some quoted text\n"),
            ],
            [
                (
                    True,
                    "Hello world.\n",
                ),
                (
                    False,
                    "On 2012-10-16 at 17:02 , Someone <\nsomeone@example.com> wrote:\n\n> Some quoted text\n",
                ),
            ],
        ),
        (
            """Hello world.

On 2012-10-16 at 17:02 , Someone <someone@example.com>
wrote:

> Some quoted text
""",
            [
                (
                    True,
                    "Hello world.\n\nOn 2012-10-16 at 17:02 , Someone <someone@example.com>\nwrote:",
                ),
                (False, "\n> Some quoted text\n"),
            ],
            [
                (
                    True,
                    "Hello world.\n",
                ),
                (
                    False,
                    "On 2012-10-16 at 17:02 , Someone <someone@example.com>\nwrote:\n\n> Some quoted text\n",
                ),
            ],
        ),
        # Forward patterns.
        (
            """Hello world.

Begin forwarded message:

> From: Someone <someone@example.com>
> Subject: The email
>
> Some quoted text.
""",
            [
                (True, "Hello world.\n\nBegin forwarded message:"),
                (
                    False,
                    "\n> From: Someone <someone@example.com>\n> Subject: The email\n>\n> Some quoted text.\n",
                ),
            ],
            [
                (True, "Hello world.\n"),
                (
                    False,
                    "Begin forwarded message:\n\n> From: Someone <someone@example.com>\n> Subject: The email\n>\n> Some quoted text.\n",
                ),
            ],
        ),
        (
            """Hello world.

---------- Forwarded message ----------
From: Someone <someone@example.com>
Subject: The email

Some quoted text.
""",
            [
                (
                    True,
                    "Hello world.\n\n---------- Forwarded message ----------",
                ),
                (
                    False,
                    "From: Someone <someone@example.com>\nSubject: The email\n\nSome quoted text.\n",
                ),
            ],
            [
                (
                    True,
                    "Hello world.\n",
                ),
                (
                    False,
                    "---------- Forwarded message ----------\nFrom: Someone <someone@example.com>\nSubject: The email\n\nSome quoted text.\n",
                ),
            ],
        ),
        (
            """Hello world.

> Begin forwarded message:
>
> From: Someone <someone@example.com>
> Subject: The email
>
> Some quoted text.
""",
            [
                (True, "Hello world.\n\n> Begin forwarded message:"),
                (
                    False,
                    ">\n> From: Someone <someone@example.com>\n> Subject: The email\n>\n> Some quoted text.\n",
                ),
            ],
            [
                (True, "Hello world.\n"),
                (
                    False,
                    "> Begin forwarded message:\n>\n> From: Someone <someone@example.com>\n> Subject: The email\n>\n> Some quoted text.\n",
                ),
            ],
        ),
    ],
)
def test_quote(text, expected, expected_quote_intro_line):
    assert quote(text) == expected
    assert quote(text, quote_intro_line=True) == expected_quote_intro_line


def test_limit():
    assert quote("Lorem\nIpsum\nDolor\nSit\nAmet", limit=2) == [
        (True, "Lorem\nIpsum"),
        (False, "Dolor\nSit\nAmet"),
    ]
