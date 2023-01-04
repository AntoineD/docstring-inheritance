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

from copy import copy
from types import FunctionType
from typing import Any
from typing import Callable
from typing import Optional

DocstringInheritor = Callable[[Optional[str], Callable[..., Any]], None]


class ClassDocstringsInheritor:
    """A class for inheriting class docstrings."""

    _cls: type
    """The class to process."""

    _docstring_inheritor: DocstringInheritor
    """The docstring inheritor."""

    _init_in_class: bool
    """Whether the ``__init__`` arguments documentation is in the class docstring."""

    __mro_classes: list[type]
    """The MRO classes."""

    def __init__(
        self,
        cls: type,
        docstring_inheritor: DocstringInheritor,
    ) -> None:
        """
        Args:
            cls: The class to process.
            docstring_inheritor: The docstring inheritor.
        """
        # Remove the new class itself and the object class from the mro,
        # we do not want to inherit from object's docstrings.
        self.__mro_classes = cls.mro()[1:-1]
        self._cls = cls
        self._docstring_inheritor = docstring_inheritor
        self._init_in_class = False

    def inherit_class_docstring(
        self,
    ) -> None:
        """Create the inherited docstring for the class docstring."""
        func = self._get_class_dummy_func()

        for cls_ in self.__mro_classes:
            self._docstring_inheritor(cls_.__doc__, func)

        self._cls.__doc__ = func.__doc__

    def inherit_attrs_docstrings(
        self,
    ) -> None:
        """Create the inherited docstrings for the class attributes."""
        for attr_name, attr in self._cls.__dict__.items():
            if not isinstance(attr, FunctionType):
                continue

            for cls_ in self.__mro_classes:
                method = getattr(cls_, attr_name, None)
                if method is None:
                    continue
                parent_doc = method.__doc__
                if parent_doc is not None:
                    break
            else:
                continue

            self._docstring_inheritor(parent_doc, attr)

    def _get_class_dummy_func(
        self,
    ) -> Callable[..., None]:
        """Return a dummy function with a given docstring.

        If ``self._ìnit_in_class`` is true then the function is a copy of ``__init__``.

        Returns:
            The function with the class docstring.
        """
        if self._init_in_class:
            # for cls_ in self.__mro_classes:
            #     # Since object is no longer in the MRO classes,
            #     # there may be not __init__.
            #     method: Callable[..., None] = getattr(cls_, "__init__")  # noqa:B009
            #     if method is not None:
            #         func = copy(method)
            #         func.__doc__ = self._cls.__doc__
            #         return func
            # Since object is no longer in the MRO classes,
            # there may be not __init__.
            method: Callable[..., None] = getattr(self._cls, "__init__")  # noqa:B009
            if method is not None:
                func = copy(method)
                func.__doc__ = self._cls.__doc__
                return func

        return self._create_dummy_func_with_doc(self._cls.__doc__)

    @staticmethod
    def _create_dummy_func_with_doc(docstring: str | None) -> Callable[..., Any]:
        """Create a dummy function with a given docstring.

        Args:
            docstring: The docstring to be assigned.

        Returns:
            The function with the given docstring.
        """

        def func() -> None:  # pragma: no cover
            pass

        func.__doc__ = docstring
        return func
