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

from docstring_inheritance import NumpyDocstringInheritor
from docstring_inheritance.docstring_inheritors.bases import SUMMARY_SECTION_NAME
from docstring_inheritance.docstring_inheritors.bases.parser import NoSectionFound
from docstring_inheritance.docstring_inheritors.numpy import DocstringParser
from docstring_inheritance.docstring_inheritors.numpy import DocstringRenderer

from .test_base_parser import _test_parse_sections


@pytest.mark.parametrize(
    ("unindented_docstring", "expected_sections"),
    [
        ("", {}),
        (
            "Short summary.",
            {
                SUMMARY_SECTION_NAME: "Short summary.",
            },
        ),
        (
            """Short summary.

Extended summary.
""",
            {
                SUMMARY_SECTION_NAME: """Short summary.

Extended summary.""",
            },
        ),
        (
            """
Parameters
----------
arg
""",
            {
                "Parameters": {"arg": ""},
            },
        ),
        (
            """Short summary.

Extended summary.

Parameters
----------
arg
""",
            {
                SUMMARY_SECTION_NAME: """Short summary.

Extended summary.""",
                "Parameters": {"arg": ""},
            },
        ),
        (
            """Short summary.

Extended summary.

Parameters
----------
arg

Section name
------------
Section body.

    Indented line.
""",
            {
                SUMMARY_SECTION_NAME: """Short summary.

Extended summary.""",
                "Parameters": {"arg": ""},
                "Section name": """\
Section body.

    Indented line.""",
            },
        ),
    ],
)
def test_parse_sections(unindented_docstring, expected_sections):
    _test_parse_sections(DocstringParser.parse, unindented_docstring, expected_sections)


@pytest.mark.parametrize(
    ("section_name", "section_body", "expected_docstring"),
    [
        (
            SUMMARY_SECTION_NAME,
            "Short summary.",
            "Short summary.",
        ),
        (
            "Section name",
            """\
Section body.

    Indented line.""",
            """\
Section name
------------
Section body.

    Indented line.""",
        ),
        (
            "Section name",
            {"arg": "\n    Description."},
            """\
Section name
------------
arg
    Description.""",
        ),
    ],
)
def test_render_section(section_name, section_body, expected_docstring):
    assert (
        DocstringRenderer._render_section(section_name, section_body)
        == expected_docstring
    )


@pytest.mark.parametrize(
    ("line1", "line2s"),
    [
        (
            "",
            "--",
        ),
        (
            "",
            "***",
        ),
        (
            "too long",
            "---",
        ),
        (
            "too long",
            "---    ",
        ),
        (
            "too long",
            "===",
        ),
        (
            "too long",
            "===    ",
        ),
    ],
)
def test_parse_one_section_no_section(line1, line2s):
    with pytest.raises(NoSectionFound):
        DocstringParser._parse_one_section(line1, line2s, [])


@pytest.mark.parametrize(
    ("line1", "line2s", "expected"),
    [
        ("name", "----", ("name", "")),
        ("name ", "----", ("name", "")),
        ("name", "-----", ("name", "")),
        ("name", "====", ("name", "")),
        ("name", "=====", ("name", "")),
    ],
)
def test_parse_one_section(line1, line2s, expected):
    assert DocstringParser._parse_one_section(line1, line2s, []) == expected


# The following are test for methods of AbstractDocstringInheritor that depend on
# concrete implementation of abstract methods.


@pytest.mark.parametrize(
    ("parent_sections", "child_sections", "expected_sections"),
    [
        # Section missing in child.
        ({0: "0"}, {}, {0: "0"}),
        # Section missing in parent.
        ({}, {0: "0"}, {0: "0"}),
        # Child override parent when section_items has no items.
        ({0: "0"}, {0: "1"}, {0: "1"}),
        # Merge sections that are not common.
        ({0: "0"}, {1: "0"}, {0: "0", 1: "0"}),
        # Section with items missing in child.
        ({"Methods": {0: "0"}}, {}, {"Methods": {0: "0"}}),
        # Section with items missing in parent.
        ({}, {"Methods": {0: "0"}}, {"Methods": {0: "0"}}),
        # Child override parent when section_items has items.
        (
            {"Methods": {0: "0"}},
            {"Methods": {0: "1"}},
            {"Methods": {0: "1"}},
        ),
        # Merge section_items with common items that are not args.
        (
            {"Methods": {0: "0"}},
            {"Methods": {1: "0"}},
            {"Methods": {0: "0", 1: "0"}},
        ),
        # Merge section_items with common items that are args.
        (
            {"Parameters": {}},
            {"Parameters": {}},
            {},
        ),
        # Standard section_items names come before non-standard ones.
        ({0: "0", "Notes": "0"}, {}, {"Notes": "0", 0: "0"}),
    ],
)
def test_inherit_sections(parent_sections, child_sections, expected_sections):
    NumpyDocstringInheritor(lambda: None)._inherit_sections(  # pragma: no cover
        parent_sections,
        child_sections,
    )
    assert child_sections == expected_sections
    # Verify the order of the keys.
    assert list(child_sections.keys()) == list(expected_sections.keys())


@pytest.mark.parametrize(
    ("sections", "expected"),
    [
        ({}, ""),
        (
            {SUMMARY_SECTION_NAME: "body"},
            """body""",
        ),
        (
            {SUMMARY_SECTION_NAME: "body", "name": "body"},
            """body

name
----
body""",
        ),
        (
            {"name": "body"},
            """
name
----
body""",
        ),
    ],
)
def test_render_docstring(sections, expected):
    assert DocstringRenderer.render(sections) == expected


# TODO: test section order and all sections items
