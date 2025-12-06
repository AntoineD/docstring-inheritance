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

import inspect
from typing import TYPE_CHECKING

from griffe import Docstring
from griffe import Extension
from griffe import ObjectNode
from griffe import Parser
from griffe import dynamic_import
from griffe import get_logger

from ._internal import BaseGoogleDocstringInheritanceMeta
from ._internal import BaseNumpyDocstringInheritanceMeta

if TYPE_CHECKING:
    import ast
    from typing import Any
    from typing import Literal

    from griffe import Alias
    from griffe import Class
    from griffe import DocstringStyle
    from griffe import Inspector
    from griffe import Object
    from griffe import Visitor

    DocstringParser = DocstringStyle | Literal[""]

_logger = get_logger(__name__)


def _import_dynamically(obj: Object | Alias) -> Any:
    """Import dynamically and return an object in a failsafe way."""
    try:
        return dynamic_import(obj.path)
    except ImportError:
        _logger.debug("Cannot get the dynamic imported docstring for %s", obj.path)


def _get_inherited_docstring_parser_kind(
    class_: type[Any],
) -> DocstringParser:
    """Return the inherited docstring parser kind of a class."""
    # Is it the first class that has a metaclass defined which has
    # DocstringInheritanceMeta in its hierarchy?
    # In other words, none of its - eventually multiple inherited - base classes
    # has a metaclass with DocstringInheritanceMeta.
    for base_class in class_.__mro__[1:]:
        if docstring_style := _get_parser_kind(base_class):
            return docstring_style
    return ""


def _get_parser_kind(
    class_: type[Any],
) -> DocstringParser:
    """Return the docstring parser kind of a class."""
    for base_meta in class_.__class__.__mro__:
        if issubclass(base_meta, BaseGoogleDocstringInheritanceMeta):
            return Parser.google.value
        if issubclass(base_meta, BaseNumpyDocstringInheritanceMeta):
            return Parser.numpy.value
    return ""


class DocstringInheritance(Extension):
    """Inherit docstrings when the package docstring-inheritance is used."""

    def on_class_members(  # noqa: D102
        self,
        *,
        node: ast.AST | ObjectNode,
        cls: Class,
        agent: Visitor | Inspector,
        **kwargs: Any,
    ) -> None:
        if isinstance(node, ObjectNode):
            # Skip runtime objects, their docstrings have already been inherited.
            return

        runtime_cls = _import_dynamically(cls)
        if runtime_cls is None:
            # Skip when the docstring has not been processed by docstring-inheritance,
            # as this only happens at runtime.
            return

        docstring_parser_kind = _get_inherited_docstring_parser_kind(runtime_cls)
        if not docstring_parser_kind:
            # If the docstring parser cannot be determined then new docstrings
            # cannot be created.
            return

        _DocstringUpdater(
            cls, runtime_cls, docstring_parser_kind, agent.docstring_options
        ).update()


class _DocstringUpdater:
    """Update the docstrings of a class from its runtime docstrings."""

    def __init__(self, cls, runtime_cls, parser, parser_options) -> None:
        self.__cls = cls
        self.__runtime_cls = runtime_cls
        self.__parser = parser
        self.__parser_options = parser_options

    def update(self) -> None:
        """Update the docstrings."""
        # Inherit the class docstring.
        self.__set_docstring(self.__cls, self.__runtime_cls)

        # Inherit the methods docstrings.
        for member in self.__cls.members.values():
            if member.is_function:
                runtime_member = _import_dynamically(member)
                if runtime_member is not None:
                    self.__set_docstring(member, runtime_member)

    def __set_docstring(
        self,
        obj: Object | Alias,
        runtime_obj: Any,
    ) -> None:
        """Set the docstring from a runtime object.

        Args:
            obj: The griffe object.
            runtime_obj: The runtime object.
        """
        try:
            docstring = runtime_obj.__doc__
        except AttributeError:
            _logger.debug("Object %s does not have a __doc__ attribute", obj.path)
            return

        if docstring is None:
            if runtime_obj.__name__ != "__init__":
                return
            # This is a constructor with no arguments,
            # thus prevent griffe_inherited_docstrings from inheriting
            # a docstring that is empty,
            # since griffe_inherited_docstrings looks for docstrings that are None.
            docstring = ""

        # Set the inherited docstring.
        if obj.docstring:
            obj.docstring.value = inspect.cleandoc(docstring)
        else:
            obj.docstring = Docstring(
                docstring,
                parent=obj,
                parser=self.__parser,
                parser_options=self.__parser_options,
            )
