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

import sys
import textwrap
from contextlib import contextmanager
from importlib import import_module
from typing import TYPE_CHECKING
from uuid import uuid4

import pytest
from griffe import Extensions
from griffe import LinesCollection
from griffe import temporary_pyfile
from griffe import visit

from docstring_inheritance import GoogleDocstringInheritanceInitMeta
from docstring_inheritance import GoogleDocstringInheritanceMeta
from docstring_inheritance.griffe import DocstringInheritance

if TYPE_CHECKING:
    from collections.abc import Iterator
    from collections.abc import Sequence
    from types import ModuleType

    from griffe import Module

    from docstring_inheritance import _BaseGoogleDocstringInheritanceMeta


@contextmanager
def temporary_visited_module(code: str) -> Iterator[tuple[Module, ModuleType]]:
    """Create and visit a temporary module with the given code.

    Parameters:
        code: The code of the module.

    Yields:
        The visited module.
    """
    module_name = f"module{uuid4()}"
    code = textwrap.dedent(code)
    with temporary_pyfile(code, module_name=module_name) as (_, path):
        lines_collection = LinesCollection()
        lines_collection[path] = code.splitlines()
        sys.path.append(str(path.parent))
        module = visit(
            module_name,
            filepath=path,
            code=code,
            extensions=Extensions(DocstringInheritance()),
            lines_collection=lines_collection,
        )
        module.modules_collection[module_name] = module
        yield module, import_module(module_name)
        sys.path.remove(str(path.parent))


def assert_str(new: str, expected: str) -> None:
    assert textwrap.dedent(new).strip() == expected.strip()


ALL_META = (GoogleDocstringInheritanceMeta, GoogleDocstringInheritanceInitMeta)


@pytest.mark.parametrize(
    ("inheritance_classes", "code", "attr_to_expected"),
    [
        #################################################################################
        (
            ALL_META,
            '''
from docstring_inheritance import {metaclass_name}
class Parent(metaclass={metaclass_name}):
    def method(self, w, x, *args, y=None, **kwargs):
        """
        Args:
            w: will be removed
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
            ''',
            {
                "Child.method": """
Args:
    xx: int
    x: int
    *args: int
    yy: The description is missing.
    y: float
    **kwargs: int
            """,
            },
        ),
        #################################################################################
        (
            ALL_META,
            '''
from docstring_inheritance import {metaclass_name}
class Parent1(metaclass={metaclass_name}):
    def method(self, w, x, *args, y=None):
        """
        Args:
            w: will be removed
            x: int parent1
            *args: int
            y: float
        """

class Parent2:
    def method(self, w, x, y=None, **kwargs):
        """
        Args:
            w: will be removed
            x: int parent2
            y: float
            **kwargs: int
        """

class Child(Parent2, Parent1):
    def method(self, xx, x, *args, yy=None, y=None, **kwargs):
        """
        Args:
            xx: int
        """
            ''',
            {
                "Child.method": """
Args:
    xx: int
    x: int parent2
    *args: int
    yy: The description is missing.
    y: float
    **kwargs: int
            """,
            },
        ),
        ################################################################################
        (
            ALL_META,
            '''
from docstring_inheritance import {metaclass_name}
class GrandParent(metaclass={metaclass_name}):
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
            ''',
            {
                "Child": """
Class Child.

Attributes:
    a: From Child.
    b: From Parent.
    c : From Child.

Methods:
    a: From GrandParent.
    b: From Parent.

Notes:
    From Child.
            """,
            },
        ),
        #################################################################################
        (
            (GoogleDocstringInheritanceInitMeta,),
            '''
from docstring_inheritance import {metaclass_name}
class Parent(metaclass={metaclass_name}):
    """Class Parent.

    Args:
        a: a from Parent.
        b: b from Parent.
    """

    def __init__(self, a, b):
        pass

class Child(Parent):
    """Class Child.

    Args:
        c: c from Child.

    Notes:
        From Child.
    """

    def __init__(self, b, c):
        pass
            ''',
            {
                "Child": """
Class Child.

Args:
    b: b from Parent.
    c: c from Child.

Notes:
    From Child.
""",
                "Child.__init__": None,
            },
        ),
        #################################################################################
        (
            (GoogleDocstringInheritanceInitMeta,),
            '''
from docstring_inheritance import {metaclass_name}
class Parent(metaclass={metaclass_name}):
    """Class Parent.

    Args:
        a: a from Parent.
        b: b from Parent.

    Attributes:
        a: a attribute.
        b: b attribute.
    """

    def __init__(self, a, b):
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

    def __init__(self, b, c):
        pass
            ''',
            {
                "Child": """
Class Child.

Args:
    b: b from Parent.
    c: c from Child.

Attributes:
    a: a attribute.
    b: b attribute.
    c: c attribute.

Notes:
    From Child.
""",
                "Child.__init__": None,
            },
        ),
        #################################################################################
        (
            (GoogleDocstringInheritanceInitMeta,),
            '''
from docstring_inheritance import {metaclass_name}
class Parent(metaclass={metaclass_name}):
    def __init__(self, a, b):
        pass

class Child(Parent):
    def __init__(self, b, c):
        """
        Args:
            b: n
        """
''',
            {
                "Child.__init__": """
Args:
    b: n
    c: The description is missing.
"""
            },
        ),
        #################################################################################
        (
            ALL_META,
            """
from docstring_inheritance import {metaclass_name}
class Parent(metaclass={metaclass_name}):
    def __init__(self):
        pass
        """,
            {"Parent.__init__": None},
        ),
        #################################################################################
        (
            ALL_META,
            """
from docstring_inheritance import {metaclass_name}
class Parent(metaclass={metaclass_name}):
    pass
class Child(Parent):
    def __init__(self):
        pass
""",
            {"Child.__init__": None},
        ),
    ],
)
def test_args_inheritance(
    inheritance_classes: Sequence[type[_BaseGoogleDocstringInheritanceMeta]],
    code: str,
    attr_to_expected: dict[str, str],
):
    for inheritance_class in inheritance_classes:
        metaclass_name = inheritance_class.__name__
        code = code.format(metaclass_name=metaclass_name)
        with temporary_visited_module(code=code) as (griffe_module, module):
            for attr_spec, expected in attr_to_expected.items():
                griffe_docstring = griffe_module[attr_spec].docstring
                if expected is None:
                    assert griffe_docstring is None
                else:
                    assert_str(griffe_docstring.value, expected)

                splits = attr_spec.split(".")
                attr = module
                while splits:
                    item_name = splits.pop(0)
                    attr = getattr(attr, item_name)

                attr_docstring = attr.__doc__
                if expected is None:
                    assert attr_docstring is None
                else:
                    assert_str(attr_docstring, expected)
