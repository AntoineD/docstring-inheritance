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
from typing import ClassVar
from typing import Iterable


def create_dummy_func_with_doc(docstring: str | None) -> Callable:
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


class AbstractDocstringInheritanceMeta(type):
    """Abstract metaclass for inheriting class docstrings."""

    docstring_processor: ClassVar[Callable[[str | None, Callable], None]]
    """The processor of the docstrings."""

    init_in_class: ClassVar[bool]
    """Whether the ``__init__`` arguments documentation is in the class docstring."""

    def __new__(
        cls, class_name: str, class_bases: tuple[type], class_dict: dict[str, Any]
    ) -> AbstractDocstringInheritanceMeta:
        if class_bases:
            classes = cls._get_classes_mro(class_bases)
            cls._inherit_class_docstring(classes, class_dict)
            cls._inherit_attrs_docstrings(classes, class_dict)
        return type.__new__(cls, class_name, class_bases, class_dict)

    @staticmethod
    def _get_classes_mro(classes: tuple[type]) -> list[type]:
        """Sort the classes according to the Method Resolution Order.

        The object class is removed because inheriting its docstring is useless.

        Args:
            classes: The classes to sort.

        Returns:
            The classes.
        """
        classes = list(
            dict.fromkeys([cls for base in classes for cls in base.__mro__])
        )
        classes.remove(object)
        return classes

    @classmethod
    def _inherit_class_docstring(
        cls, classes: list[type], class_dict: dict[str, Any]
    ) -> None:
        """Create the inherited docstring for the class docstring.

        Args:
            classes: The classes to inherit from.
            class_dict: The class definition.
        """
        func = cls._get_class_dummy_func(classes, class_dict.get("__doc__"))

        for cls_ in classes:
            cls.docstring_processor(cls_.__doc__, func)

        class_dict["__doc__"] = func.__doc__

    @classmethod
    def _inherit_attrs_docstrings(
        cls, classes: list[type], class_dict: dict[str, Any]
    ) -> None:
        """Create the inherited docstrings for the class attributes.

        Args:
            classes: The classes to inherit from.
            class_dict: The class definition.
        """
        for attr_name, attr in class_dict.items():
            if not isinstance(attr, FunctionType):
                continue

            for cls_ in classes:
                method = getattr(cls_, attr_name, None)
                if method is None:
                    continue
                parent_doc = method.__doc__
                if parent_doc is not None:
                    break
            else:
                continue

            cls.docstring_processor(parent_doc, attr)

    @classmethod
    def _get_class_dummy_func(
        cls, classes: Iterable[type], docstring: str | None
    ) -> Callable[..., None]:
        """Return a dummy function with a given docstring.

        If ``cls.ìnit_in_class`` is true then the function is a copy of ``__init__``.
        """
        if cls.init_in_class:
            for cls_ in classes:
                method = getattr(cls_, "__init__")  # noqa:B009
                if method is not None:
                    func = copy(method)
                    func.__doc__ = docstring
                    return func

        return create_dummy_func_with_doc(docstring)
