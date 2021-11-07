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
from inspect import getdoc

from docstring_inheritance import NumpyDocstringInheritanceMeta


def test_inheritance():
    class Parent(metaclass=NumpyDocstringInheritanceMeta):
        def meth(self, w, x, *args, y=None, **kwargs):
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
        def meth(self, xx, x, *args, yy=None, y=None, **kwargs):
            """
            Parameters
            ----------
            xx: int
            """

    excepted = """
Parameters
----------
xx: int
x: int
*args: int
yy:
The description is missing.
y: float
**kwargs: int"""

    assert Child.meth.__doc__ == excepted


def test_missing_parent_attr():
    class Parent(metaclass=NumpyDocstringInheritanceMeta):
        pass

    class Child(Parent):
        def method(self, xx, x, *args, yy=None, y=None, **kwargs):
            """Summary"""

        @classmethod
        def classmethod(cls):
            """Summary"""

        @staticmethod
        def staticmethod():
            """Summary"""

        @property
        def prop(self):
            """Summary"""

    excepted = "Summary"

    assert Child.method.__doc__ == excepted.strip("\n")
    assert Child.classmethod.__doc__ == excepted.strip("\n")
    assert Child.staticmethod.__doc__ == excepted.strip("\n")
    assert Child.prop.__doc__ == excepted.strip("\n")


def test_missing_parent_doc_for_attr():
    class Parent(metaclass=NumpyDocstringInheritanceMeta):
        def method(self):
            pass

        @classmethod
        def classmethod(cls):
            pass

        @staticmethod
        def staticmethod():
            pass

        @property
        def prop(self):
            pass

    class Child(Parent):
        def method(self, xx, x, *args, yy=None, y=None, **kwargs):
            """Summary"""

        @classmethod
        def classmethod(cls):
            """Summary"""

        @staticmethod
        def staticmethod():
            """Summary"""

        @property
        def prop(self):
            """Summary"""

    excepted = "Summary"

    assert Child.method.__doc__ == excepted.strip("\n")
    assert Child.classmethod.__doc__ == excepted.strip("\n")
    assert Child.staticmethod.__doc__ == excepted.strip("\n")
    assert Child.prop.__doc__ == excepted.strip("\n")


def test_multiple_inheritance():
    class Parent1(metaclass=NumpyDocstringInheritanceMeta):
        """Parent1 summary

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

    excepted = """
Parent1 summary

Attributes
----------
attr1
attr2

Methods
-------
method1
method2
"""
    assert getdoc(Child) == excepted.strip("\n")


def test_several_parents():
    class GrandParent(metaclass=NumpyDocstringInheritanceMeta):
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

    excepted = """
Parent summary

Attributes
----------
attr1
attr2

Methods
-------
method1
method2
"""
    assert getdoc(Child) == excepted.strip("\n")


def test_do_not_inherit_object():
    class Parent(metaclass=NumpyDocstringInheritanceMeta):
        def __init__(self):
            pass

    class Child(Parent):
        pass

    assert Child.__init__.__doc__ is None
