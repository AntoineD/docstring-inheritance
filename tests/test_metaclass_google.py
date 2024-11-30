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

from docstring_inheritance import GoogleDocstringInheritanceInitMeta
from docstring_inheritance import GoogleDocstringInheritanceMeta

parametrize_inheritance = pytest.mark.parametrize(
    "inheritance_class",
    [GoogleDocstringInheritanceMeta, GoogleDocstringInheritanceInitMeta],
)


@parametrize_inheritance
def test_args_inheritance(inheritance_class):
    class Parent(metaclass=inheritance_class):
        def method(self, w, x, *args, y=None, **kwargs):
            """
            Args:
                w
                x: int
                *args: int
                y: float
                **kwargs: int
            """

    class Child(Parent):
        def method(self, xx, x, *args, yy=None, y=None, **kwargs):
            """
            Args:
                xx: int
            """

    expected = """
Args:
    xx: int
    x: int
    *args: int
    yy: The description is missing.
    y: float
    **kwargs: int"""

    assert Child.method.__doc__ == expected


@parametrize_inheritance
def test_class_doc_inheritance(inheritance_class):
    class GrandParent(metaclass=inheritance_class):
        """Class GrandParent.

        Attributes:
            a: From GrandParent.

        Methods:
            a: From GrandParent.

        Notes:
            From GrandParent.
        """

    class Parent(GrandParent):
        """Class Parent.

        Attributes:
            b: From Parent.

        Methods:
            b: From Parent.
        """

    class Child(Parent):
        """Class Child.

        Attributes:
            a: From Child.
            c : From Child.

        Notes:
            From Child.
        """

    expected = """\
Class Child.

Attributes:
    a: From Child.
    b: From Parent.
    c : From Child.

Methods:
    a: From GrandParent.
    b: From Parent.

Notes:
    From Child.\
"""

    assert Child.__doc__ == expected


@parametrize_inheritance
def test_do_not_inherit_from_object(inheritance_class):
    class Parent(metaclass=inheritance_class):
        def __init__(self):  # pragma: no cover
            pass

    assert Parent.__init__.__doc__ is None


def test_class_doc_inheritance_with_init():
    class Parent(metaclass=GoogleDocstringInheritanceInitMeta):
        """Class Parent.

        Args:
            a: a from Parent.
            b: b from Parent.
        """

        def __init__(self, a, b):  # pragma: no cover
            pass

    class Child(Parent):
        """Class Child.

        Args:
            c: c from Child.

        Notes:
            From Child.
        """

        def __init__(self, b, c):  # pragma: no cover
            pass

    expected = """\
Class Child.

Args:
    b: b from Parent.
    c: c from Child.

Notes:
    From Child.\
"""

    assert Child.__doc__ == expected
    assert Child.__init__.__doc__ is None


def test_class_doc_inheritance_with_init_attr():
    class Parent(metaclass=GoogleDocstringInheritanceInitMeta):
        """Class Parent.

        Args:
            a: a from Parent.
            b: b from Parent.

        Attributes:
            a: a attribute.
            b: b attribute.
        """

        def __init__(self, a, b):  # pragma: no cover
            pass

    class Child(Parent):
        """Class Child.

        Args:
            c: c from Child.

        Attributes:
            c: c attribute.

        Notes:
            From Child.
        """

        def __init__(self, b, c):  # pragma: no cover
            pass

    expected = """\
Class Child.

Args:
    b: b from Parent.
    c: c from Child.

Attributes:
    a: a attribute.
    b: b attribute.
    c: c attribute.

Notes:
    From Child.\
"""

    assert Child.__doc__ == expected
    assert Child.__init__.__doc__ is None


def test_class_doc_inheritance_with_empty_parent_doc():
    class Parent(metaclass=GoogleDocstringInheritanceInitMeta):
        def __init__(self, a, b):  # pragma: no cover
            pass

    class Child(Parent):
        def __init__(self, b, c):  # pragma: no cover
            """
            Args:
                b: n
            """

    expected = """
Args:
    b: n
"""
    assert textwrap.dedent(Child.__init__.__doc__) == expected
