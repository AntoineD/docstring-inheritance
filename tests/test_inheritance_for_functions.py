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
import inspect

import pytest
from docstring_inheritance import inherit_google_docstring
from docstring_inheritance import inherit_numpy_docstring
from docstring_inheritance.metaclass import create_dummy_func_with_doc


def test_side_effect():
    def f(x, y=None, **kwargs):
        pass

    ref_signature = inspect.signature(f)

    inherit_numpy_docstring(None, f)
    assert inspect.signature(f) == ref_signature


def test_google():
    def parent(arg, *parent_varargs, **parent_kwargs):
        """Parent summary.

        Args:
            arg: desc
            *parent_varargs: Parent *args
            **parent_kwargs: Parent **kwargs

        Examples:
            Parent examples

        Returns:
            Parent returns

        See Also:
            Parent see also

        References:
            Parent references

        Todo:
            Parent todo

        Yields:
            Parent yields
        """

    def child(x, missing_doc, *child_varargs, **child_kwargs):
        """Child summary.

        Yields:
            Child yields

        Raises:
            Child raises

        Notes:
            Child notes

        Examples:
            Child examples

        Warns:
            Child warns

        Warnings:
            Child warnings

        Args:
            x: X
            child_varargs: Not *args
            *child_varargs: Child *args
            **child_kwargs: Child **kwargs
        """

    expected = """Child summary.

Args:
    x: X
    missing_doc: The description is missing.
    *child_varargs: Child *args
    **child_kwargs: Child **kwargs

Returns:
    Parent returns

Yields:
    Child yields

Raises:
    Child raises

Warns:
    Child warns

Warnings:
    Child warnings

See Also:
    Parent see also

Notes:
    Child notes

References:
    Parent references

Examples:
    Child examples

Todo:
    Parent todo
"""

    inherit_google_docstring(parent.__doc__, child)
    assert child.__doc__ == expected.strip("\n")


@pytest.mark.parametrize(
    "inherit_docstring", [inherit_numpy_docstring, inherit_google_docstring]
)
@pytest.mark.parametrize(
    "parent_docstring,child_docstring,expected_docstring",
    [(None, None, None), ("parent", None, "parent"), (None, "child", "child")],
)
def test_simple(
    inherit_docstring, parent_docstring, child_docstring, expected_docstring
):
    dummy_func = create_dummy_func_with_doc(child_docstring)
    inherit_docstring(parent_docstring, dummy_func)
    assert dummy_func.__doc__ == expected_docstring
