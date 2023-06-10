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
from __future__ import annotations

import textwrap

import pytest

from docstring_inheritance.docstring_inheritors.base import AbstractDocstringInheritor


@pytest.mark.parametrize(
    "section_body,expected",
    [
        ([], ""),
        (["foo"], "foo"),
        (["", "foo"], "foo"),
        (["bar", "foo"], "foo\nbar"),
    ],
)
def test_get_section_body(section_body, expected):
    assert AbstractDocstringInheritor._get_section_body(section_body) == expected


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
    assert (
        AbstractDocstringInheritor._parse_section_items(section_body)
        == expected_matches
    )


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


@pytest.fixture(scope="module")
def concrete_inheritor() -> type[AbstractDocstringInheritor]:
    """Return a concrete enough AbstractDocstringInheritor."""
    AbstractDocstringInheritor._ARGS_SECTION_NAMES = {"Args"}
    AbstractDocstringInheritor._SECTION_NAMES_WITH_ITEMS = {"Args", "Methods"}
    yield AbstractDocstringInheritor
    delattr(AbstractDocstringInheritor, "_ARGS_SECTION_NAMES")
    delattr(AbstractDocstringInheritor, "_SECTION_NAMES_WITH_ITEMS")


@pytest.mark.parametrize(
    "parent_section,child_section,func,expected",
    [
        ({}, {}, func_none, {}),
        # Non-existing section in child.
        ({"Section": "parent"}, {}, func_none, {"Section": "parent"}),
        # Non-existing section in parent.
        ({}, {"Section": "child"}, func_none, {"Section": "child"}),
        # Child section updates the parent one (no items).
        ({"Section": "parent"}, {"Section": "child"}, func_none, {"Section": "child"}),
        # Child section updates the parent one (no items),  with other sections.
        (
            {"Section": "parent", "ParentSection": "parent"},
            {"Section": "child", "ChildSection": "child"},
            func_none,
            {"Section": "child", "ParentSection": "parent", "ChildSection": "child"},
        ),
        # Section reordering.
        (
            {"Section": "parent", "Returns": "", "Parameters": ""},
            {},
            func_none,
            {"Parameters": "", "Returns": "", "Section": "parent"},
        ),
        # Sections with items (not Args).
        # Non-existing item in child.
        ({"Methods": {"parent_m": ""}}, {}, func_none, {"Methods": {"parent_m": ""}}),
        # Non-existing item in parent.
        ({}, {"Methods": {"child_m": ""}}, func_none, {"Methods": {"child_m": ""}}),
        # Child item updates the parent one (no common items).
        (
            {"Methods": {"parent_m": ""}},
            {"Methods": {"child_m": ""}},
            func_none,
            {"Methods": {"parent_m": "", "child_m": ""}},
        ),
        # Child item updates the parent one (common items).
        (
            {"Methods": {"method": "parent"}},
            {"Methods": {"method": "child"}},
            func_none,
            {"Methods": {"method": "child"}},
        ),
        # Sections with args items.
        # Non-existing section in child for function without args.
        ({"Args": {"parent_a": ""}}, {}, func_none, {"Args": {}}),
        # Non-existing section in parent for function without args.
        ({}, {"Args": {"child_a": ""}}, func_none, {"Args": {}}),
        # Missing argument description.
        (
            {"Args": {"parent_a": ""}},
            {"Args": {"child_a": ""}},
            func_args,
            {"Args": {"arg": "The description is missing."}},
        ),
        # Argument description in parent.
        (
            {"Args": {"arg": "parent"}},
            {"Args": {"child_a": ""}},
            func_args,
            {"Args": {"arg": "parent"}},
        ),
        # Argument description in child.
        (
            {"Args": {"parent_a": ""}},
            {"Args": {"arg": "child"}},
            func_args,
            {"Args": {"arg": "child"}},
        ),
        # Argument description in both parent and child.
        (
            {"Args": {"arg": "parent"}},
            {"Args": {"arg": "child"}},
            func_args,
            {"Args": {"arg": "child"}},
        ),
    ],
)
def test_inherit_items(
    concrete_inheritor, parent_section, child_section, func, expected
):
    concrete_inheritor._inherit_sections(parent_section, child_section, func)
    assert child_section == expected


@pytest.mark.parametrize(
    "func,section_items,expected",
    [
        (func_none, {}, {}),
        # Non-existing args are removed.
        (func_none, {"arg": ""}, {}),
        # Self arg is removed.
        (func_with_self, {"self": ""}, {}),
        # Missing arg description.
        (
            func_args_kwonlyargs,
            {"arg1": ""},
            {"arg1": "", "arg2": AbstractDocstringInheritor.MISSING_ARG_DESCRIPTION},
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
            {"*varargs": AbstractDocstringInheritor.MISSING_ARG_DESCRIPTION},
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
            {"**varkw": AbstractDocstringInheritor.MISSING_ARG_DESCRIPTION},
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
            {"arg": AbstractDocstringInheritor.MISSING_ARG_DESCRIPTION},
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
        AbstractDocstringInheritor._filter_args_section(func, section_items) == expected
    )


@pytest.mark.parametrize(
    "sections,expected",
    (
        ({}, {}),
        ({"": ""}, {"": ""}),
        ({"": {"": ""}}, {"": {"": ""}}),
        ({"": "__inherit_section_doc__"}, {}),
        ({"": "__inherit_section_doc__", "a": ""}, {"a": ""}),
        ({"": {"": "__inherit_section_doc__"}}, {"": {}}),
        ({"": {"": "__inherit_section_doc__", "a": ""}}, {"": {"a": ""}}),
    ),
)
def test_filter_sections(sections, expected):
    AbstractDocstringInheritor._filters_inherited_sections(sections)
    assert sections == expected
