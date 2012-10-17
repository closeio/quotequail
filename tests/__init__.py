import unittest
from quotequail import quote

class QuoteTestCase(unittest.TestCase):
    def test_quote(self):
        self.assertEqual(
            quote(
"""Hello world.

On 2012-10-16 at 17:02 , Someone <someone@example.com> wrote:

> Some quoted text
"""),
            [(True, 'Hello world.\n\nOn 2012-10-16 at 17:02 , Someone <someone@example.com> wrote:'),
             (False, '\n> Some quoted text\n')]
        )

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

if __name__ == '__main__':
    unittest.main()

