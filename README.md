Sublime Text 2 Print to HTML
============================

A simple ST2 plugin to convert code files into HTML with color syntax highlighting and line numbers.

Colorization and HTML conversion is currently performed by [Pygments][0], which supports a range of [languages and syntaxes][3].

**Installation:**

 - Install [Package Manager][2].
 - Use `cmd+shift+P` or `ctrl+shift+P` then `Package Control: Install Package`.
 - Look for `Print to HTML` and install it.

**Usage:**

 - For best results, save your file with an appropriate extension beforehand.
 - Use `shift+alt+P` to print current file as HTML and open in your browser, or
 - From File menu, use `Print as HTML to Browser` or `Print as HTML to New Buffer`.

**Uses:**

 - [Pygments][0] for code-to-HTML conversion

**Future goals:**

 - Use ST2's internal scope and color data from a buffer to produce an exact replica of a file from ST2 in HTML form. The current approach using Pygments has limitations regarding formats unknown by Pygments (e.g. Markdown) and documents with mixed syntaxes (e.g. PHP embedded in HTML).
 - Add options for toggling line-numbering output, embedding HTML A anchors for each line, et al.
 - Support different color schemes.
 - Only print current selection(s) OR print selected text with a highlighted background.

This code is available on [Github][1]. Pull requests are welcome.


 [0]: http://pygments.org/
 [1]: https://github.com/joelpt/sublimetext-print-to-html
 [2]: http://wbond.net/sublime_packages/package_control
 [3]: http://pygments.org/languages/