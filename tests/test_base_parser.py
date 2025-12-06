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

from docstring_inheritance._internal.docstring_inheritors.bases.parser import (
    BaseDocstringParser,
)


@pytest.mark.parametrize(
    ("section_body", "expected"),
    [
        ([], ""),
        (["foo"], "foo"),
        (["", "foo"], "foo"),
        (["bar", "foo"], "foo\nbar"),
    ],
)
def test_get_section_body(section_body, expected):
    assert BaseDocstringParser._get_section_body(section_body) == expected


@pytest.mark.parametrize(
    ("section_body", "expected_matches"),
    [
        ("foo", {"foo": ""}),
        ("foo : str\n    Foo.", {"foo": " : str\n    Foo."}),
        ("foo\nbar", {"foo": "", "bar": ""}),
        ("foo : str\n    Foo.\nbar", {"foo": " : str\n    Foo.", "bar": ""}),
        (
            "foo : str\n    Foo.\nbar : int\n    Bar.",
            {"foo": " : str\n    Foo.", "bar": " : int\n    Bar."},
        ),
    ],
)
def test_section_items_regex(section_body, expected_matches):
    assert BaseDocstringParser._parse_section_items(section_body) == expected_matches


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
