# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from docutils import nodes, utils
from docutils.parsers.rst import directives, roles, Directive
from pygments.formatters import HtmlFormatter
from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer
import re


class Pygments(Directive):
    """ Source code syntax highlighting.
    """
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {
        'anchorlinenos': directives.flag,
        'classprefix': directives.unchanged,
        'hl_lines': directives.unchanged,
        'lineanchors': directives.unchanged,
        'linenos': directives.unchanged,
        'linenospecial': directives.nonnegative_int,
        'linenostart': directives.nonnegative_int,
        'linenostep': directives.nonnegative_int,
        'lineseparator': directives.unchanged,
        'linespans': directives.unchanged,
        'nobackground': directives.flag,
        'nowrap': directives.flag,
        'tagsfile': directives.unchanged,
        'tagurlformat': directives.unchanged,
    }
    has_content = True

    def run(self):
        self.assert_has_content()
        try:
            lexer = get_lexer_by_name(self.arguments[0])
        except ValueError:
            # no lexer found - use the text one instead of an exception
            lexer = TextLexer()

        if ('linenos' in self.options and
                self.options['linenos'] not in ('table', 'inline')):
            self.options['linenos'] = 'table'

        for flag in ('nowrap', 'nobackground', 'anchorlinenos'):
            if flag in self.options:
                self.options[flag] = True

        # noclasses should already default to False, but just in case...
        formatter = HtmlFormatter(noclasses=False, **self.options)
        parsed = highlight('\n'.join(self.content), lexer, formatter)
        return [nodes.raw('', parsed, format='html')]

directives.register_directive('code-block', Pygments)
directives.register_directive('sourcecode', Pygments)


class YouTube(Directive):
    """ Embed YouTube video in posts.

    Courtesy of Brian Hsu: https://gist.github.com/1422773

    VIDEO_ID is required, with / height are optional integer,
    and align could be left / center / right.

    Usage:
    .. youtube:: VIDEO_ID
        :width: 640
        :height: 480
        :align: center
    """

    def align(argument):
        """Conversion function for the "align" option."""
        return directives.choice(argument, ('left', 'center', 'right'))

    required_arguments = 1
    optional_arguments = 2
    option_spec = {
        'width': directives.positive_int,
        'height': directives.positive_int,
        'align': align
    }

    final_argument_whitespace = False
    has_content = False

    def run(self):
        videoID = self.arguments[0].strip()
        width = 420
        height = 315
        align = 'left'

        if 'width' in self.options:
            width = self.options['width']

        if 'height' in self.options:
            height = self.options['height']

        if 'align' in self.options:
            align = self.options['align']

        url = 'http://www.youtube.com/embed/%s' % videoID
        div_block = '<div class="youtube" align="%s">' % align
        embed_block = '<iframe width="%s" height="%s" src="%s" '\
                      'frameborder="0"></iframe>' % (width, height, url)

        return [
            nodes.raw('', div_block, format='html'),
            nodes.raw('', embed_block, format='html'),
            nodes.raw('', '</div>', format='html')]

directives.register_directive('youtube', YouTube)

_abbr_re = re.compile('\((.*)\)$')


class abbreviation(nodes.Inline, nodes.TextElement):
    pass


def abbr_role(typ, rawtext, text, lineno, inliner, options={}, content=[]):
    text = utils.unescape(text)
    m = _abbr_re.search(text)
    if m is None:
        return [abbreviation(text, text)], []
    abbr = text[:m.start()].strip()
    expl = m.group(1)
    return [abbreviation(abbr, abbr, explanation=expl)], []

roles.register_local_role('abbr', abbr_role)
