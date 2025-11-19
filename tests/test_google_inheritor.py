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

from docstring_inheritance.docstring_inheritors.bases import SUMMARY_SECTION_NAME
from docstring_inheritance.docstring_inheritors.google import DocstringParser
from docstring_inheritance.docstring_inheritors.google import DocstringRenderer

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
Args:
    arg
""",
            {
                "Args": {"arg": ""},
            },
        ),
        (
            """Short summary.

Extended summary.

Args:
    arg
""",
            {
                SUMMARY_SECTION_NAME: """Short summary.

Extended summary.""",
                "Args": {"arg": ""},
            },
        ),
        (
            """Short summary.

Extended summary.

Args:
    arg

Notes:
    Section body.

        Indented line.
""",
            {
                SUMMARY_SECTION_NAME: """Short summary.

Extended summary.""",
                "Args": {"arg": ""},
                "Notes": """\
Section body.

    Indented line.""",
            },
        ),
    ],
)
def test_parse_sections(unindented_docstring, expected_sections):
    _test_parse_sections(
        DocstringParser.parse,
        unindented_docstring,
        expected_sections,
    )


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
Section name:
    Section body.

        Indented line.""",
        ),
        (
            "Section name",
            {"arg": ": Description."},
            """\
Section name:
    arg: Description.""",
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
            " Args",
            "  body",
        ),
        (
            " Args:",
            "  body",
        ),
        (
            "Args",
            "  body",
        ),
        (
            "Args:",
            " body",
        ),
        (
            "Dummy:",
            "  body",
        ),
        (
            "Dummy :",
            "  body",
        ),
        (
            "Dummy:",
            "   body",
        ),
    ],
)
def test_parse_one_section_no_section(line1, line2s):
    assert not DocstringParser._parse_one_section(line1, line2s, [])[0]


@pytest.mark.parametrize(
    ("line1", "line2s", "expected"),
    [
        ("Args:", "  body", ("Args", "body")),
        ("Args :", "  body", ("Args", "body")),
        ("Args:", "   body", ("Args", "body")),
    ],
)
def test_parse_one_section(line1, line2s, expected):
    assert DocstringParser._parse_one_section(line1, line2s, []) == expected


@pytest.mark.parametrize(
    ("sections", "expected"),
    [
        ({}, ""),
        (
            {SUMMARY_SECTION_NAME: "body"},
            """body""",
        ),
        (
            {SUMMARY_SECTION_NAME: "body", "Args": "body"},
            """body

Args:
    body""",
        ),
        (
            {"Args": "body"},
            """
Args:
    body""",
        ),
    ],
)
def test_render_docstring(sections, expected):
    assert DocstringRenderer.render(sections) == expected


# TODO: test section order and all sections items
