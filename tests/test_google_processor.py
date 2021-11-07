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
import pytest
from docstring_inheritance import GoogleDocstringProcessor
from test_base_processor import _test_parse_sections


@pytest.mark.parametrize(
    "unindented_docstring,expected_sections",
    [
        ("", {}),
        (
            "Short summary.",
            {
                None: "Short summary.",
            },
        ),
        (
            """Short summary.

Extended summary.
""",
            {
                None: """Short summary.

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
                None: """Short summary.

Extended summary.""",
                "Args": {"arg": ""},
            },
        ),
        (
            """Short summary.

Extended summary.

Args:
    arg

Section name:
    Section body.

        Indented line.
""",
            {
                None: """Short summary.

Extended summary.""",
                "Args": {"arg": ""},
                "Section name": """\
Section body.

    Indented line.""",
            },
        ),
    ],
)
def test_parse_sections(unindented_docstring, expected_sections):
    _test_parse_sections(
        GoogleDocstringProcessor._parse_sections,
        unindented_docstring,
        expected_sections,
    )


@pytest.mark.parametrize(
    "section_name,section_body,expected_docstring",
    [
        (
            None,
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
        GoogleDocstringProcessor._render_section(section_name, section_body)
        == expected_docstring
    )


@pytest.mark.parametrize(
    "section_body,expected",
    [
        ([], ""),
        ([" foo"], "foo"),
        (["", " foo"], "foo"),
        ([" bar", " foo"], "foo\nbar"),
    ],
)
def test_get_section_body(section_body, expected):
    assert GoogleDocstringProcessor._get_section_body(section_body) == expected


@pytest.mark.parametrize(
    "line1,line2s,expected",
    [
        (" name", "  body", (None, None)),
        (" name:", "  body", (None, None)),
        ("name", "  body", (None, None)),
        ("name:", " body", (None, None)),
        ("name:", "  body", ("name", "body")),
        ("name :", "  body", ("name", "body")),
        ("name:", "   body", ("name", "body")),
    ],
)
def test_parse_one_section(line1, line2s, expected):
    assert GoogleDocstringProcessor._parse_one_section(line1, line2s, []) == expected


@pytest.mark.parametrize(
    "sections,expected",
    [
        ({}, ""),
        (
            {None: "body"},
            """body""",
        ),
        (
            {None: "body", "name": "body"},
            """body

name:
    body""",
        ),
        (
            {"name": "body"},
            """
name:
    body""",
        ),
    ],
)
def test_render_docstring(sections, expected):
    assert GoogleDocstringProcessor._render_docstring(sections) == expected


def test_inherit_section_items_with_args():
    def func(arg):
        """"""

    expected = {"arg": GoogleDocstringProcessor.MISSING_ARG_DESCRIPTION}

    assert (
        GoogleDocstringProcessor._inherit_section_items_with_args(func, {}) == expected
    )


# TODO: test section order and all sections items
