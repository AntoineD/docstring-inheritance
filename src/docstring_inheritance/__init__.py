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

from typing import Any

from .class_docstrings_inheritor import ClassDocstringsInheritor
from .class_docstrings_inheritor import DocstringInheritor
from .docstring_inheritors.google import GoogleDocstringInheritor
from .docstring_inheritors.numpy import NumpyDocstringInheritor

inherit_numpy_docstring = NumpyDocstringInheritor()
inherit_google_docstring = GoogleDocstringInheritor()


class _BaseDocstringInheritanceMeta(type):
    """Base metaclass for inheriting class docstrings."""

    def __init__(
        cls,
        class_name: str,
        class_bases: tuple[type],
        class_dict: dict[str, Any],
        docstring_inheritor: DocstringInheritor,
        init_in_class: bool,
    ) -> None:
        super().__init__(class_name, class_bases, class_dict)
        if class_bases:
            ClassDocstringsInheritor.inherit_docstring(
                cls, docstring_inheritor, init_in_class
            )


class GoogleDocstringInheritanceMeta(_BaseDocstringInheritanceMeta):
    """Metaclass for inheriting docstrings in Google format."""

    def __init__(
        self,
        class_name: str,
        class_bases: tuple[type],
        class_dict: dict[str, Any],
    ) -> None:
        super().__init__(
            class_name,
            class_bases,
            class_dict,
            inherit_google_docstring,
            init_in_class=False,
        )


class GoogleDocstringInheritanceInitMeta(_BaseDocstringInheritanceMeta):
    """Metaclass for inheriting docstrings in Google format with ``__init__`` in the
    class docstring."""

    def __init__(
        self,
        class_name: str,
        class_bases: tuple[type],
        class_dict: dict[str, Any],
    ) -> None:
        super().__init__(
            class_name,
            class_bases,
            class_dict,
            inherit_google_docstring,
            init_in_class=True,
        )


class NumpyDocstringInheritanceMeta(_BaseDocstringInheritanceMeta):
    """Metaclass for inheriting docstrings in Numpy format."""

    def __init__(
        self,
        class_name: str,
        class_bases: tuple[type],
        class_dict: dict[str, Any],
    ) -> None:
        super().__init__(
            class_name,
            class_bases,
            class_dict,
            inherit_numpy_docstring,
            init_in_class=False,
        )


class NumpyDocstringInheritanceInitMeta(_BaseDocstringInheritanceMeta):
    """Metaclass for inheriting docstrings in Numpy format with ``__init__`` in the
    class docstring."""

    def __init__(
        self,
        class_name: str,
        class_bases: tuple[type],
        class_dict: dict[str, Any],
    ) -> None:
        super().__init__(
            class_name,
            class_bases,
            class_dict,
            inherit_numpy_docstring,
            init_in_class=True,
        )
