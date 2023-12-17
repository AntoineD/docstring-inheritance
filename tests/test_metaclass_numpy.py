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

from inspect import getdoc

import pytest

from docstring_inheritance import NumpyDocstringInheritanceInitMeta
from docstring_inheritance import NumpyDocstringInheritanceMeta

parametrize_inheritance = pytest.mark.parametrize(
    "inheritance_class",
    (NumpyDocstringInheritanceMeta, NumpyDocstringInheritanceInitMeta),
)


def assert_args_inheritance(cls):
    excepted = """
Parameters
----------
xx: int
x: int
*args: int
yy
    The description is missing.
y: float
**kwargs: int"""

    assert cls.method.__doc__ == excepted


@parametrize_inheritance
def test_args_inheritance_parent_meta(inheritance_class):
    class Parent(metaclass=inheritance_class):
        def method(self, w, x, *args, y=None, **kwargs):
            """
            Parameters
            ----------
            w
            x: int
            *args: int
            y: float
            **kwargs: int
            """

    class Child(Parent):
        def method(self, xx, x, *args, yy=None, y=None, **kwargs):
            """
            Parameters
            ----------
            xx: int
            """

    assert_args_inheritance(Child)


@parametrize_inheritance
def test_args_inheritance_child_meta(inheritance_class):
    class Parent:
        def method(self, w, x, *args, y=None, **kwargs):
            """
            Parameters
            ----------
            w
            x: int
            *args: int
            y: float
            **kwargs: int
            """

    class Child(Parent, metaclass=inheritance_class):
        def method(self, xx, x, *args, yy=None, y=None, **kwargs):
            """
            Parameters
            ----------
            xx: int
            """

    assert_args_inheritance(Child)


def assert_docstring(cls):
    excepted = "Summary"

    assert cls.method.__doc__ == excepted
    assert cls.class_method.__doc__ == excepted
    assert cls.static_method.__doc__ == excepted
    assert cls.prop.__doc__ == excepted


@parametrize_inheritance
def test_missing_parent_attr_parent_meta(inheritance_class):
    class Parent(metaclass=inheritance_class):
        pass

    class Child(Parent):
        def method(self, xx, x, *args, yy=None, y=None, **kwargs):
            """Summary"""

        @classmethod
        def class_method(cls):
            """Summary"""

        @staticmethod
        def static_method():
            """Summary"""

        @property
        def prop(self):
            """Summary"""

    assert_docstring(Child)


@parametrize_inheritance
def test_missing_parent_attr_child_meta(inheritance_class):
    class Parent:
        pass

    class Child(Parent, metaclass=inheritance_class):
        def method(self, xx, x, *args, yy=None, y=None, **kwargs):
            """Summary"""

        @classmethod
        def class_method(cls):
            """Summary"""

        @staticmethod
        def static_method():
            """Summary"""

        @property
        def prop(self):
            """Summary"""

    assert_docstring(Child)


@parametrize_inheritance
def test_missing_parent_doc_for_attr_parent_meta(inheritance_class):
    class Parent(metaclass=inheritance_class):
        def method(self):  # pragma: no cover
            pass

        @classmethod
        def class_method(cls):  # pragma: no cover
            pass

        @staticmethod
        def static_method():  # pragma: no cover
            pass

        @property
        def prop(self):  # pragma: no cover
            pass

    class Child(Parent):
        def method(self, xx, x, *args, yy=None, y=None, **kwargs):  # pragma: no cover
            """Summary"""

        @classmethod
        def class_method(cls):  # pragma: no cover
            """Summary"""

        @staticmethod
        def static_method():  # pragma: no cover
            """Summary"""

        @property
        def prop(self):  # pragma: no cover
            """Summary"""

    assert_docstring(Child)


@parametrize_inheritance
def test_missing_parent_doc_for_attr_child_meta(inheritance_class):
    class Parent:
        def method(self):  # pragma: no cover
            pass

        @classmethod
        def class_method(cls):  # pragma: no cover
            pass

        @staticmethod
        def static_method():  # pragma: no cover
            pass

        @property
        def prop(self):  # pragma: no cover
            pass

    class Child(Parent, metaclass=inheritance_class):
        def method(self, xx, x, *args, yy=None, y=None, **kwargs):  # pragma: no cover
            """Summary"""

        @classmethod
        def class_method(cls):  # pragma: no cover
            """Summary"""

        @staticmethod
        def static_method():  # pragma: no cover
            """Summary"""

        @property
        def prop(self):  # pragma: no cover
            """Summary"""

    assert_docstring(Child)


def assert_multiple_inheritance(cls):
    excepted = """Parent summary

Attributes
----------
attr1
attr2

Methods
-------
method1
method2"""
    assert getdoc(cls) == excepted


@parametrize_inheritance
def test_multiple_inheritance_parent_meta(inheritance_class):
    class Parent1(metaclass=inheritance_class):
        """Parent summary

        Attributes
        ----------
        attr1
        """

    class Parent2:
        """Parent2 summary

        Methods
        -------
        method1
        """

    class Child(Parent1, Parent2):
        """
        Attributes
        ----------
        attr2

        Methods
        -------
        method2
        """

    assert_multiple_inheritance(Child)


@parametrize_inheritance
def test_multiple_inheritance_child_meta(inheritance_class):
    class Parent1:
        """Parent summary

        Attributes
        ----------
        attr1
        """

    class Parent2:
        """Parent2 summary

        Methods
        -------
        method1
        """

    class Child(Parent1, Parent2, metaclass=inheritance_class):
        """
        Attributes
        ----------
        attr2

        Methods
        -------
        method2
        """

    assert_multiple_inheritance(Child)


@parametrize_inheritance
def test_multiple_inheritance_child_meta_method(inheritance_class):
    class Parent1:
        def method(self, w, x):  # pragma: no cover
            """Summary 1

            Parameters
            ----------
            w: w doc
            x: x doc

            Returns
            -------
            int
            """

    class Child(Parent1, metaclass=inheritance_class):
        def method(self, w, x, *args, y=None, **kwargs):  # pragma: no cover
            pass

    excepted = """Summary 1

Parameters
----------
w: w doc
x: x doc
*args
    The description is missing.
y
    The description is missing.
**kwargs
    The description is missing.

Returns
-------
int"""

    assert Child.method.__doc__ == excepted


@parametrize_inheritance
def test_several_parents_parent_meta(inheritance_class):
    class GrandParent(metaclass=inheritance_class):
        """GrandParent summary

        Attributes
        ----------
        attr1
        """

    class Parent(GrandParent):
        """Parent summary

        Methods
        -------
        method1
        """

    class Child(Parent):
        """
        Attributes
        ----------
        attr2

        Methods
        -------
        method2
        """

    assert_multiple_inheritance(Child)


@parametrize_inheritance
def test_several_parents_child_meta(inheritance_class):
    class GrandParent:
        """GrandParent summary

        Attributes
        ----------
        attr1
        """

    class Parent(GrandParent):
        """Parent summary

        Methods
        -------
        method1
        """

    class Child(Parent, metaclass=inheritance_class):
        """
        Attributes
        ----------
        attr2

        Methods
        -------
        method2
        """

    assert_multiple_inheritance(Child)


@parametrize_inheritance
def test_do_not_inherit_object_child_meta(inheritance_class):
    class Parent:
        def __init__(self):  # pragma: no cover
            pass

    class Child(Parent, metaclass=inheritance_class):
        pass

    assert Child.__init__.__doc__ is None


@parametrize_inheritance
def test_do_not_inherit_from_object(inheritance_class):
    class Parent(metaclass=inheritance_class):
        def __init__(self):  # pragma: no cover
            pass

    assert Parent.__init__.__doc__ is None
