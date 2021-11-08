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


def assert_args_inheritance(cls):
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

    assert cls.meth.__doc__ == excepted


def test_args_inheritance_parent_meta():
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

    assert_args_inheritance(Child)


def test_args_inheritance_child_meta():
    class Parent:
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

    class Child(Parent, metaclass=NumpyDocstringInheritanceMeta):
        def meth(self, xx, x, *args, yy=None, y=None, **kwargs):
            """
            Parameters
            ----------
            xx: int
            """

    assert_args_inheritance(Child)


def assert_missing_attr(cls):
    excepted = "Summary"

    assert cls.method.__doc__ == excepted
    assert cls.classmethod.__doc__ == excepted
    assert cls.staticmethod.__doc__ == excepted
    assert cls.prop.__doc__ == excepted


def test_missing_parent_attr_parent_meta():
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

    assert_missing_attr(Child)


def test_missing_parent_attr_child_meta():
    class Parent:
        pass

    class Child(Parent, metaclass=NumpyDocstringInheritanceMeta):
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

    assert_missing_attr(Child)


def test_missing_parent_doc_for_attr_parent_meta():
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

    assert_missing_attr(Child)


def test_missing_parent_doc_for_attr_child_meta():
    class Parent:
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

    class Child(Parent, metaclass=NumpyDocstringInheritanceMeta):
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

    assert_missing_attr(Child)


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


def test_multiple_inheritance_parent_meta():
    class Parent1(metaclass=NumpyDocstringInheritanceMeta):
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


def test_multiple_inheritance_child_meta():
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

    class Child(Parent1, Parent2, metaclass=NumpyDocstringInheritanceMeta):
        """
        Attributes
        ----------
        attr2

        Methods
        -------
        method2
        """

    assert_multiple_inheritance(Child)


def test_several_parents_parent_meta():
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

    assert_multiple_inheritance(Child)


def test_several_parents_child_meta():
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

    class Child(Parent, metaclass=NumpyDocstringInheritanceMeta):
        """
        Attributes
        ----------
        attr2

        Methods
        -------
        method2
        """

    assert_multiple_inheritance(Child)


def test_do_not_inherit_object_parent_meta():
    class Parent(metaclass=NumpyDocstringInheritanceMeta):
        def __init__(self):
            pass

    class Child(Parent):
        pass

    assert Child.__init__.__doc__ is None


def test_do_not_inherit_object_child_meta():
    class Parent:
        def __init__(self):
            pass

    class Child(Parent, metaclass=NumpyDocstringInheritanceMeta):
        pass

    assert Child.__init__.__doc__ is None
