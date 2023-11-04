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

import pytest

from docstring_inheritance.docstring_inheritors.bases.inheritor import (
    BaseDocstringInheritor,
)
from docstring_inheritance.docstring_inheritors.bases.parser import BaseDocstringParser


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


ARGS_SECTION_NAME = "DummyArgs"
ARGS_SECTION_NAMES = {"DummyArgs"}
METHODS_SECTION_NAME = "MethodsArgs"
SECTION_NAMES_WITH_ITEMS = {ARGS_SECTION_NAME, METHODS_SECTION_NAME}
MISSING_ARG_TEXT = "dummy missing"


@pytest.mark.parametrize(
    ("parent_section", "child_section", "func", "expected"),
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
        (
            {METHODS_SECTION_NAME: {"parent_m": ""}},
            {},
            func_none,
            {METHODS_SECTION_NAME: {"parent_m": ""}},
        ),
        # Non-existing item in parent.
        (
            {},
            {METHODS_SECTION_NAME: {"child_m": ""}},
            func_none,
            {METHODS_SECTION_NAME: {"child_m": ""}},
        ),
        # Child item updates the parent one (no common items).
        (
            {METHODS_SECTION_NAME: {"parent_m": ""}},
            {METHODS_SECTION_NAME: {"child_m": ""}},
            func_none,
            {METHODS_SECTION_NAME: {"parent_m": "", "child_m": ""}},
        ),
        # Child item updates the parent one (common items).
        (
            {METHODS_SECTION_NAME: {"method": "parent"}},
            {METHODS_SECTION_NAME: {"method": "child"}},
            func_none,
            {METHODS_SECTION_NAME: {"method": "child"}},
        ),
        # Sections with args items.
        # Non-existing section in child for function without args.
        ({ARGS_SECTION_NAME: {"parent_a": ""}}, {}, func_none, {}),
        # Non-existing section in parent for function without args.
        ({}, {ARGS_SECTION_NAME: {"child_a": ""}}, func_none, {}),
        # Missing argument description.
        ({}, {}, func_args, {ARGS_SECTION_NAME: {"arg": MISSING_ARG_TEXT}}),
        (
            {},
            {ARGS_SECTION_NAME: {"child_a": ""}},
            func_args,
            {ARGS_SECTION_NAME: {"arg": MISSING_ARG_TEXT}},
        ),
        (
            {ARGS_SECTION_NAME: {"parent_a": ""}},
            {},
            func_args,
            {ARGS_SECTION_NAME: {"arg": MISSING_ARG_TEXT}},
        ),
        (
            {ARGS_SECTION_NAME: {"parent_a": ""}},
            {ARGS_SECTION_NAME: {"child_a": ""}},
            func_args,
            {ARGS_SECTION_NAME: {"arg": MISSING_ARG_TEXT}},
        ),
        # Argument description in parent.
        (
            {ARGS_SECTION_NAME: {"arg": "parent"}},
            {},
            func_args,
            {ARGS_SECTION_NAME: {"arg": "parent"}},
        ),
        (
            {ARGS_SECTION_NAME: {"arg": "parent"}},
            {ARGS_SECTION_NAME: {"child_a": ""}},
            func_args,
            {ARGS_SECTION_NAME: {"arg": "parent"}},
        ),
        # Argument description in child.
        (
            {},
            {ARGS_SECTION_NAME: {"arg": "child"}},
            func_args,
            {ARGS_SECTION_NAME: {"arg": "child"}},
        ),
        (
            {ARGS_SECTION_NAME: {"parent_a": ""}},
            {ARGS_SECTION_NAME: {"arg": "child"}},
            func_args,
            {ARGS_SECTION_NAME: {"arg": "child"}},
        ),
        # Argument description in both parent and child.
        (
            {ARGS_SECTION_NAME: {"arg": "parent"}},
            {ARGS_SECTION_NAME: {"arg": "child"}},
            func_args,
            {ARGS_SECTION_NAME: {"arg": "child"}},
        ),
        # Section ordering.
        (
            {},
            {"Returns": "", None: ""},
            func_none,
            {None: "", "Returns": ""},
        ),
        (
            {},
            {"Returns": "", ARGS_SECTION_NAME: {"arg": ""}, None: ""},
            func_args,
            {None: "", ARGS_SECTION_NAME: {"arg": ""}, "Returns": ""},
        ),
    ],
)
def test_inherit_items(parent_section, child_section, func, expected):
    BaseDocstringInheritor._inherit_sections(
        SECTION_NAMES_WITH_ITEMS,
        ARGS_SECTION_NAME,
        BaseDocstringParser.SECTION_NAMES,
        MISSING_ARG_TEXT,
        parent_section,
        child_section,
        func,
    )
    assert child_section == expected


@pytest.mark.parametrize(
    ("func", "section_items", "expected"),
    [
        (func_none, {}, {}),
        # Non-existing args are removed.
        (func_none, {"arg": ""}, {}),
        # Self arg is removed.
        (func_with_self, {"self": ""}, {}),
        # Missing arg description.
        (func_args_kwonlyargs, {"arg1": ""}, {"arg1": "", "arg2": MISSING_ARG_TEXT}),
        # Args are ordered according to the signature.
        (
            func_args_kwonlyargs,
            {"arg2": "", "arg1": ""},
            {"arg1": "", "arg2": ""},
        ),
        # Varargs alone.
        (func_varargs, {}, {"*varargs": MISSING_ARG_TEXT}),
        (
            func_varargs,
            {"*varargs": ""},
            {"*varargs": ""},
        ),
        # Varkw alone.
        (func_varkw, {}, {"**varkw": MISSING_ARG_TEXT}),
        (
            func_varkw,
            {"**varkw": ""},
            {"**varkw": ""},
        ),
        # Kwonlyargs alone.
        (func_kwonlyargs, {}, {"arg": MISSING_ARG_TEXT}),
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
        BaseDocstringInheritor._filter_args_section(
            MISSING_ARG_TEXT, func, section_items
        )
        == expected
    )
