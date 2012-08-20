# coding=utf8

import sublime
import sublime_plugin
import desktop
import tempfile
import re

import pygments
import pygments.formatters
import pygments.lexers


class PrintToHtmlCommand(sublime_plugin.TextCommand):
    """Convert current file to HTML and view in browser or ST2 buffer."""

    def run(self, edit, target='browser'):
        settings = sublime.load_settings('Print to HTML.sublime-settings')

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

        # turn tabs into spaces per view's setting to ensure proper indentation
        spaces = ' ' * int(self.view.settings().get('tab_size', 8))
        text = re.sub(r'\t', spaces, text)

        # get buffer's syntax name, to be used as a hint for choosing a lexer
        syntax = self.view.settings().get('syntax')
        syntax = re.sub(r'.+/(.+).tmLanguage', r'\1', syntax).lower()

        # gather Pygment related option flags from plugin settings
        optlist = ['line_numbering', 'draw_background', 'line_anchors']
        options = dict(map(lambda x: (x, settings.get(x, False)), optlist))

        # perform the conversion to HTML
        body, css = convert_to_html(filename, text, syntax, encoding, options)

        # construct onload body attrib for print/close JS within browser
        if target == 'browser':
            onload = ' onload="'
            if settings.get('auto_print_in_browser', False):
                onload += 'window.print();'
                if settings.get('auto_close_in_browser', False):
                    onload += 'window.close();'
            onload += '"'
        else:
            onload = ''

        # force black and white styling if monochrome setting is on
        if settings.get('monochrome', False):
            css += '\n'.join(['',
                '.highlight * { color: black !important }',
                '.highlight .err { border: 1px solid black !important }'])

        # set font family
        if settings.get('font', False):
            css += '\n.highlight * { font-family: %s; }' % settings.get('font')

        # set font size
        if settings.get('font_size', None):
            css += '\n.highlight { font-size: %s; }' % settings.get('font_size')

        # set line height
        if settings.get('line_height', None):
            css += '\n.highlight { line-height: %s; }' % settings.get('line_height')

        # hide Pygments error borders unless requested to show
        if not settings.get('draw_error_borders', False):
            css += '\n.highlight .err { border: none !important }'

        # wrap long lines if requested
        if settings.get('word_wrap', False):
            css += '\n.highlight > pre { width: 100%; word-wrap: break-word; }'

        # prepare html for final output
        html = construct_html_document(encoding, filename, css, body, onload)

        # show html in browser or new buffer
        if target == 'browser':
            send_to_browser(html)
        elif target == 'sublime':
            send_to_new_buffer(self.view, html)
        else:
            raise Exception('Unsupported arg "target"')


def construct_html_document(encoding, title, css, body, body_attribs):
    """Populate simple boilerplate HTML with given arguments."""
    body = body.decode('utf-8').encode('ascii', 'xmlcharrefreplace')
    output = '\n'.join([
        '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">',
        '<meta charset="%s">' % encoding,
        '<html>',
        '<head>',
        '<title>%s</title>' % title,
        '<style>',
        css,
        '</style>',
        '</head>',
        '<body%s>' % body_attribs,
        body,
        '</body>',
        '</html>'])
    return output


def send_to_browser(html):
    """Create a temp file containing html and open it in the default web browser."""
    tmp_html = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
    tmp_html.write(html)
    tmp_html.close()
    desktop.open(tmp_html.name)


def send_to_new_buffer(view, html):
    """Load html into a new buffer in the same window as view."""
    new_view = view.window().new_file()
    new_edit = new_view.begin_edit()
    new_view.insert(new_edit, 0, html)
    new_view.end_edit(new_edit)


def get_lexer(filename, syntax, text):
    """Try to determine the appropriate lexer for the given file/syntax/text."""
    # special case for Plain Text syntax and empty files
    if syntax == 'plain text' or text == '':
        lexer = pygments.lexers.TextLexer()
        print 'Plain text or no text, defaulting to:', lexer
        return lexer

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
            lexer = pygments.lexers.guess_lexer_for_filename(filename, text)
            print 'Guessed lexer from filename:', lexer
            return lexer
        except pygments.util.ClassNotFound:
            pass

    # guess lexer by analyzing the text
    lexer = pygments.lexers.guess_lexer(text)
    print 'Guessed lexer from text analysis:', lexer
    return lexer


def convert_with_pygments(lexer, formatter, text):
    """Use Pygments to convert text using provided lexer and formatter."""
    html = pygments.highlight(text, lexer, formatter)
    css = formatter.get_style_defs('.highlight')
    return html, css


def convert_to_html(filename, text, syntax, encoding, options):
    """Convert text to HTML form, using filename and syntax as lexer hints."""
    formatter = pygments.formatters.HtmlFormatter(
        encoding=encoding,
        linenos='inline' if options['line_numbering'] else False,
        nobackground=not options['draw_background'],
        lineanchors='line' if options['line_anchors'] else False)
    lexer = get_lexer(filename, syntax, text)
    return convert_with_pygments(lexer, formatter, text)
