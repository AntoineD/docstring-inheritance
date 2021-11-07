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
from docstring_inheritance.processors.numpy import NumpyDocstringProcessor
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
                None: """Short summary.

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
                None: """Short summary.

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
    _test_parse_sections(
        NumpyDocstringProcessor._parse_sections, unindented_docstring, expected_sections
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
        NumpyDocstringProcessor._render_section(section_name, section_body)
        == expected_docstring
    )


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
    assert NumpyDocstringProcessor._get_section_body(section_body) == expected


@pytest.mark.parametrize(
    "line1,line2s,expected",
    [
        ("", "--", (None, None)),
        ("", "***", (None, None)),
        ("too long", "---", (None, None)),
        ("too long", "---    ", (None, None)),
        ("too long", "===", (None, None)),
        ("too long", "===    ", (None, None)),
        ("name", "----", ("name", "")),
        ("name ", "----", ("name", "")),
        ("name", "-----", ("name", "")),
        ("name", "====", ("name", "")),
        ("name", "=====", ("name", "")),
    ],
)
def test_parse_one_section(line1, line2s, expected):
    assert NumpyDocstringProcessor._parse_one_section(line1, line2s, []) == expected


# The following are test for methods of AbstractDocstringProcessor that depend
# concrete implementation of abstract methods.


@pytest.mark.parametrize(
    "parent_sections,child_sections,expected_sections",
    [
        # Section missing in child.
        ({0: 0}, {}, {0: 0}),
        # Section missing in parent.
        ({}, {0: 0}, {0: 0}),
        # Child override parent when section_items has no items.
        ({0: 0}, {0: 1}, {0: 1}),
        # Merge sections that are not common.
        ({0: 0}, {1: 0}, {0: 0, 1: 0}),
        # Section with items missing in child.
        ({"Methods": {0: 0}}, {}, {"Methods": {0: 0}}),
        # Section with items missing in parent.
        ({}, {"Methods": {0: 0}}, {"Methods": {0: 0}}),
        # Child override parent when section_items has items.
        (
            {"Methods": {0: 0}},
            {"Methods": {0: 1}},
            {"Methods": {0: 1}},
        ),
        # Merge section_items with common items that are not args.
        (
            {"Methods": {0: 0}},
            {"Methods": {1: 0}},
            {"Methods": {0: 0, 1: 0}},
        ),
        # Merge section_items with common items that are args.
        (
            {"Parameters": {}},
            {"Parameters": {}},
            {"Parameters": {}},
        ),
        # Standard section_items names come before non standard ones.
        ({0: 0, "Notes": 0}, {}, {"Notes": 0, 0: 0}),
    ],
)
def test_inherit_sections(parent_sections, child_sections, expected_sections):
    new_child_sections = NumpyDocstringProcessor._inherit_sections(
        parent_sections, child_sections, lambda: None
    )
    assert new_child_sections == expected_sections
    # Verify the order of the keys.
    assert list(new_child_sections.keys()) == list(expected_sections.keys())


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
    assert NumpyDocstringProcessor._render_docstring(sections) == expected


def test_inherit_section_items_with_args():
    def func(arg):
        """"""

    expected = {"arg": NumpyDocstringProcessor.MISSING_ARG_DESCRIPTION}

    assert (
        NumpyDocstringProcessor._inherit_section_items_with_args(func, {}) == expected
    )


# TODO: test section order and all sections items
