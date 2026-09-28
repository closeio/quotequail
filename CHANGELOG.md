# Changes

## Unreleased

* Keep a header whose value wraps over several lines when another known
  header follows (`MAX_HEADER_WRAP_LINES`), such as a "To:" with several
  recipients. Past the second line such a header ended the header block, so
  the headers were re-detected further down and `from`, `date` and `to` were
  lost. A line only continues a header this way when a known header follows
  it, so the body after the last header is never absorbed.
* Drop the stray "*" left in front of values of bold headers written as
  "*From: *John".

## v0.5.4

* Keep quoted HTML when the quoted content is only an image. Previously
  `unwrap_html` dropped the quote and returned only `html_top`.
* Recognize "Origineel bericht" as an additional Dutch translation of
  "Original Message" in forward markers.

## v0.5.3

* Added support for Dutch reply and forward patterns.
* Flatten malformed tags whose names are not valid XML 1.0 Names in
  `get_html_tree()`. Previously only tags containing `:`, `@` or `=` were
  flattened.

## v0.5.2

* Strip XML-illegal characters from input HTML in `get_html_tree()`. `lxml`
  parses them into the tree but raises `ValueError: All strings must be XML
  compatible` when any text or attribute assignment later touches them. NULL
  bytes, previously replaced with U+FFFD by the parser are now removed.

## v0.5.1

* Fixes for lxml >=6 compatibility
* Declare lxml as a dependency (#74)
* Fix KeyError when HTML contains tags with '=' in their name

## v0.5.0

* On lxml >= 6 only: unescaped `<addr@domain>` pseudo-tags (common in
  quoted reply headers) now render as visible escaped text
  (`&lt;addr@domain&gt;`) instead of an invisible bogus element, and no
  longer trigger `KeyError: '@'` in `slice_tree`.

## v0.4.0
* Add `quote_intro_line` parameter to `quote` and `quote_html`.
* Modernize all tests.

## v0.3.1
* Fix `unwrap_html` when no result was found.

## v0.3.0

* Code quality improvements: linting, typing
* Supporting Python versions 3.10 - 3.12
* Improve Outlook forward detection

## v0.2.4

* First version using auto-release process
* Added support for russian, portuguese, and swedish reply patterns
* Fixed bug where newlines just before "wrote:" weren't detected
* updated repo to apply more modern linting + code style

