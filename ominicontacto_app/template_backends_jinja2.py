from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils import translation
from jinja2 import Environment
from jinja2.utils import markupsafe
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from yaml import safe_dump


def yaml_repr(data):
    return markupsafe.Markup(
        highlight(
            safe_dump(data, allow_unicode=True, width=240),
            get_lexer_by_name("yaml"),
            HtmlFormatter(noclasses=True),
        )
    )


def environment(**options):
    env = Environment(**options, extensions=["jinja2.ext.i18n"])
    env.install_gettext_translations(translation)
    env.globals.update({
        "static": staticfiles_storage.url,
        "yaml_repr": yaml_repr,
    })
    return env
