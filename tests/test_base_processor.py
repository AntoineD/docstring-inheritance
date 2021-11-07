# Copyright 2021 Antoine DECHAUME
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import textwrap

import pytest
from docstring_inheritance.processors import parse_section_items
from docstring_inheritance.processors.base import AbstractDocstringProcessor


def _test_parse_sections(parse_sections, unindented_docstring, expected_sections):
    """Verify the parsing of the sections of a docstring."""
    # Indent uniformly.
    docstring = textwrap.indent(unindented_docstring, " " * 4, lambda line: True)
    # But the first line.
    docstring = docstring.lstrip(" \t")
    outcome = parse_sections(docstring)
    assert outcome == expected_sections
    # Verify the order of the keys.
    assert list(outcome.keys()) == list(expected_sections.keys())


@pytest.mark.parametrize(
    "section_body,expected_matches",
    (
        ("foo", {"foo": ""}),
        ("foo : str\n    Foo.", {"foo": " : str\n    Foo."}),
        ("foo\nbar", {"foo": "", "bar": ""}),
        ("foo : str\n    Foo.\nbar", {"foo": " : str\n    Foo.", "bar": ""}),
        (
            "foo : str\n    Foo.\nbar : int\n    Bar.",
            {"foo": " : str\n    Foo.", "bar": " : int\n    Bar."},
        ),
    ),
)
def test_section_items_regex(section_body, expected_matches):
    assert parse_section_items(section_body) == expected_matches


def func_none():
    pass


def func_with_self(self):
    pass


def func_args(arg):
    pass


def func_args_kwonlyargs(arg1, arg2=None):
    pass


def func_kwonlyargs(arg=None):
    pass


def func_varargs(*varargs):
    pass


def func_varkw(**varkw):
    pass


def func_args_varargs(arg, *varargs):
    pass


def func_varargs_varkw(*varargs, **varkw):
    pass


def func_args_varkw(arg, **varkw):
    pass


def func_all(arg1, arg2=None, *varargs, **varkw):
    pass


@pytest.mark.parametrize(
    "func,section_items,expected",
    [
        (func_none, {}, {}),
        # Non existing args are removed.
        (func_none, {"arg": ""}, {}),
        # Self arg is removed.
        (func_with_self, {"self": ""}, {}),
        # Missing arg description.
        (
            func_args_kwonlyargs,
            {"arg1": ""},
            {"arg1": "", "arg2": AbstractDocstringProcessor.MISSING_ARG_DESCRIPTION},
        ),
        # Args are ordered according to the signature.
        (
            func_args_kwonlyargs,
            {"arg2": "", "arg1": ""},
            {"arg1": "", "arg2": ""},
        ),
        # Varargs alone.
        (
            func_varargs,
            {},
            {"*varargs": AbstractDocstringProcessor.MISSING_ARG_DESCRIPTION},
        ),
        (
            func_varargs,
            {"*varargs": ""},
            {"*varargs": ""},
        ),
        # Varkw alone.
        (
            func_varkw,
            {},
            {"**varkw": AbstractDocstringProcessor.MISSING_ARG_DESCRIPTION},
        ),
        (
            func_varkw,
            {"**varkw": ""},
            {"**varkw": ""},
        ),
        # Kwonlyargs alone.
        (
            func_kwonlyargs,
            {},
            {"arg": AbstractDocstringProcessor.MISSING_ARG_DESCRIPTION},
        ),
        (
            func_kwonlyargs,
            {"arg": ""},
            {"arg": ""},
        ),
        # Args and Kwonlyargs.
        (
            func_args_varkw,
            {"**varkw": "", "arg": ""},
            {"arg": "", "**varkw": ""},
        ),
        # Args and varargs.
        (
            func_args_varargs,
            {"*varargs": "", "arg": ""},
            {"arg": "", "*varargs": ""},
        ),
        # Args and varargs.
        (
            func_varargs_varkw,
            {"**varkw": "", "*varargs": ""},
            {"*varargs": "", "**varkw": ""},
        ),
        # All kinds of arguments.
        (
            func_all,
            {"**varkw": "", "*varargs": "", "arg2": "", "arg1": ""},
            {"arg1": "", "arg2": "", "*varargs": "", "**varkw": ""},
        ),
    ],
)
def test_inherit_section_items_with_args(func, section_items, expected):
    assert (
        AbstractDocstringProcessor._inherit_section_items_with_args(func, section_items)
        == expected
    )
