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
"""Docstrings inheritor class."""

from __future__ import annotations

from types import WrapperDescriptorType
from typing import TYPE_CHECKING
from typing import Any
from typing import Final

from docstring_inheritance.docstring_inheritors.bases.inheritor import (
    BaseDocstringInheritor,
)

if TYPE_CHECKING:
    from collections.abc import Callable

DocstringInheritorClass = type[BaseDocstringInheritor]


class ClassDocstringsInheritor:
    """A class for inheriting class docstrings."""

    __cls: type
    """The class to process."""

    __docstring_inheritor: DocstringInheritorClass
    """The docstring inheritor."""

    _init_in_class: bool
    """Whether the `__init__` arguments documentation is in the class docstring."""

    __mro_classes: list[type]
    """The MRO classes."""

    __object_init_doc: Final[str | None] = object.__init__.__doc__

    def __init__(
        self,
        cls: type,
        docstring_inheritor: DocstringInheritorClass,
        init_in_class: bool,
    ) -> None:
        """
        Args:
            cls: The class to process.
            docstring_inheritor: The docstring inheritor.
            init_in_class: Whether the `__init__` arguments documentation is in the
                class docstring.
        """  # noqa: D205, D212
        # Remove the new class itself and the object class from the mro,
        # object's docstrings have no interest.
        self.__mro_classes = cls.mro()[1:-1]
        self.__cls = cls
        self.__docstring_inheritor = docstring_inheritor
        self._init_in_class = init_in_class

    @classmethod
    def inherit_docstrings(
        cls,
        class_: type,
        docstring_inheritor: DocstringInheritorClass,
        init_in_class: bool,
    ) -> None:
        """Inherit all docstrings of the class.

        Args:
            class_: The class to process.
            docstring_inheritor: The docstring inheritor.
            init_in_class: Whether the `__init__` arguments documentation is in the
                class docstring.
        """
        inheritor = cls(class_, docstring_inheritor, init_in_class)
        inheritor.__inherit_methods_docstrings()
        inheritor.__inherit_class_docstring()

    def __inherit_class_docstring(self) -> None:
        """Create the inherited docstring for the class docstring."""
        func = None
        old_init_doc = None
        init_doc_changed = False

        if self._init_in_class:
            init_method: Callable[..., None] = self.__cls.__init__  # type: ignore[misc]
            # Ignore the case when __init__ is from object since there is no docstring
            # and its __doc__ cannot be assigned.
            if not isinstance(init_method, WrapperDescriptorType):
                old_init_doc = init_method.__doc__
                init_method.__doc__ = self.__cls.__doc__
                func = init_method
                init_doc_changed = True

        if func is None:
            func = _create_dummy_func_with_doc(self.__cls.__doc__)

        docstring_inheritor = self.__docstring_inheritor(func)

        for parent_cls in self.__mro_classes:
            # As opposed to the attribute inheritance, and following the way a class is
            # assembled by type(), the docstring of a class is the combination of the
            # docstrings of its parents.
            docstring_inheritor.inherit(parent_cls.__doc__)

        docstring_inheritor.render()

        self.__cls.__doc__ = func.__doc__

        if self._init_in_class and init_doc_changed:
            init_method.__doc__ = old_init_doc

    def __inherit_methods_docstrings(self) -> None:
        """Create the inherited docstrings for the class methods."""
        mro_classes = self.__mro_classes
        object_init_doc = self.__object_init_doc
        init_method_name = "__init__"
        create_inheritor = self.__docstring_inheritor.create

        for attr_name, attr in self.__cls.__dict__.items():
            inheritor = create_inheritor(attr)
            if inheritor is None:
                # This attribute is not a method or function.
                continue

            for parent_cls in mro_classes:
                parent_method = getattr(parent_cls, attr_name, None)
                if parent_method is None:
                    continue
                parent_doc = parent_method.__doc__
                if attr_name == init_method_name and parent_doc == object_init_doc:
                    # Do not inherit the object __init__ docstrings.
                    continue
                inheritor.inherit(parent_doc)
                if not inheritor.has_missing_descriptions:
                    # In case of multiple inheritance,
                    # when the parent that has docstring inheritance
                    # is not the first one or not in the hierarchy of the first one,
                    # some arguments docstring may need to be fetched
                    # beyond the first parent.
                    # Otherwise, the inheritance is done for that attribute.
                    break

            inheritor.render()


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
