# Changes

## v0.5.3

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

