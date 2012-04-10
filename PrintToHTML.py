import sublime
import sublime_plugin
import desktop
import tempfile
import re
import sys
import os

import pygments
import pygments.formatters
import pygments.lexers


# Pull in built-in plugin directory
# Apparently this approach is necessary because pygments uses __import__() to selectively import
# required modules on demand.
built_in_plugins = os.path.join(sublime.packages_path(), 'Print to HTML')
if not built_in_plugins in sys.path:
    sys.path.append(built_in_plugins)


class PrintToHtmlCommand(sublime_plugin.TextCommand):
    """Convert current file to HTML and view in browser or ST2 buffer."""

    def run(self, edit, target='browser'):

        # get the text to be converted and the buffer's filename
        region = sublime.Region(0, self.view.size())
        text = self.view.substr(region)
        filename = self.view.file_name()

        # determine output encoding
        encoding = self.view.encoding()
        if encoding == 'Undefined':
            encoding = 'UTF-8'
        elif encoding == 'Western (Windows 1252)':
            encoding = 'windows-1252'

        # determine buffer's syntax name, to be used as a hint for choosing a lexer
        syntax = self.view.settings().get('syntax')
        syntax = re.sub(r'.+/(.+).tmLanguage', r'\1', syntax).lower()

        # perform the conversion
        html, css = convert_to_html(filename, text, syntax, encoding)

        # build the html
        html_contents = '\n'.join([
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">',
            '<meta charset="%s">' % encoding,
            '<html>',
            '<head>',
            '<title>%s</title>' % filename,
            '<style>', css, '</style>',
            '</head>',
            '<body%s>' % ('onload="window.print()"' if target == 'browser' else ''),
            html,
            '</body>',
            '</html>'])

        # output
        if target == 'browser':
            tmp_html = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
            tmp_html.write(html_contents.encode(encoding))
            tmp_html.close()
            desktop.open(tmp_html.name)
        elif target == 'sublime':
            new_view = self.view.window().new_file()
            new_edit = new_view.begin_edit()
            new_view.insert(new_edit, 0, html_contents)
            new_view.end_edit(new_edit)


def get_lexer(filename, syntax, data):
    # special case for Plain Text syntax
    if syntax == 'plain text':
        print 'Plain text, using TextLexer'
        return pygments.lexers.TextLexer()

    # look for a lexer based on the ST2 syntax name
    try:
        lexer = pygments.lexers.get_lexer_by_name(syntax)
        print 'Guessed lexer from ST2 syntax setting:', lexer
        return lexer
    except pygments.util.ClassNotFound:
        pass

    # look for a lexer based on the ST2 sub-syntax name, e.g. 'Django' in 'HTML (Django)'
    if '(' in syntax:
        syntax = re.sub(r'.+\((.+)\)', r'\1', syntax)
        print syntax
        try:
            lexer = pygments.lexers.get_lexer_by_name(syntax)
            print 'Guessed lexer from ST2 sub-syntax setting:', lexer
            return lexer
        except pygments.util.ClassNotFound:
            pass

    # guess lexer by buffer's filename
    if filename is not None and len(filename) >= 3:
        try:
            lexer = pygments.lexers.guess_lexer_for_filename(filename, data)
            print 'Guessed lexer from filename:', lexer
            return lexer
        except pygments.util.ClassNotFound:
            pass

    # guess lexer by analyzing the text
    lexer = pygments.lexers.guess_lexer(data)
    print 'Guessed lexer from text:', lexer
    return lexer


def convert_with_pygments(lexer, formatter, data):
    html = pygments.highlight(data, lexer, formatter)
    css = formatter.get_style_defs('.highlight')
    return html, css


def convert_to_html(filename, data, syntax, encoding):
    formatter = pygments.formatters.HtmlFormatter(
        linenos='inline',
        encoding=encoding,
        nobackground=True,
        lineanchors='line')
    lexer = get_lexer(filename, syntax, data)
    return convert_with_pygments(lexer, formatter, data)
