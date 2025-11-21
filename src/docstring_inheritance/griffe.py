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
from typing import Any

from griffe import Alias
from griffe import Attribute
from griffe import Docstring
from griffe import Extension
from griffe import ObjectNode
from griffe import Parser
from griffe import dynamic_import
from griffe import get_logger

from docstring_inheritance import _BaseGoogleDocstringInheritanceMeta
from docstring_inheritance import _BaseNumpyDocstringInheritanceMeta

if TYPE_CHECKING:
    import ast
    from typing import Literal

    from griffe import Class
    from griffe import DocstringOptions
    from griffe import DocstringStyle
    from griffe import Inspector
    from griffe import Object
    from griffe import Visitor

    DocstringParser = DocstringStyle | Literal[""]

_logger = get_logger(__name__)


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
            # Skip runtime objects, their docstrings are already OK.
            return

        runtime_cls = self.__import_dynamically(cls)
        if runtime_cls is None:
            return

        docstring_parser_kind = self.__get_inherited_docstring_parser_kind(runtime_cls)
        if not docstring_parser_kind:
            return

        parser_options = agent.docstring_options

        # Inherit the class docstring.
        self.__set_docstring(cls, runtime_cls, docstring_parser_kind, parser_options)

        # Inherit the methods docstrings.
        for member in cls.members.values():
            if isinstance(member, Attribute):
                # Only methods can inherit docstrings.
                continue
            runtime_member = self.__import_dynamically(member)
            self.__set_docstring(
                member, runtime_member, docstring_parser_kind, parser_options
            )

    @staticmethod
    def __import_dynamically(obj: Object | Alias) -> Any:
        """Import dynamically and return an object."""
        try:
            return dynamic_import(obj.path)
        except ImportError:
            _logger.debug("Can not get the dynamic imported docstring for %s", obj.path)

    @classmethod
    def __set_docstring(
        cls,
        obj: Object | Alias,
        runtime_obj: Any,
        docstring_parser: DocstringStyle,
        parser_options: DocstringOptions,
    ) -> None:
        """Set the docstring from a runtime object.

        Args:
            obj: The griffe object.
            runtime_obj: The runtime object.
            docstring_parser: The docstring parser.
            parser_options: The parser options.
        """
        if runtime_obj is None:
            return

        try:
            docstring = runtime_obj.__doc__
        except AttributeError:
            _logger.debug("Object %s does not have a __doc__ attribute", obj.path)
            return

        if docstring is None:
            return

        # Update the object instance with the evaluated docstring.
        if obj.docstring:
            obj.docstring.value = inspect.cleandoc(docstring)
        else:
            assert not isinstance(obj, Alias)
            obj.docstring = Docstring(
                docstring,
                parent=obj,
                parser=docstring_parser,
                parser_options=parser_options,
            )

    @classmethod
    def __get_inherited_docstring_parser_kind(
        cls,
        class_: type[Any],
    ) -> DocstringParser:
        """Return the inherited docstring parser kind."""
        # Is it the first class that has a metaclass defined which has
        # DocstringInheritanceMeta in its hierarchy?
        # In other words, none of its - eventually multiple inherited - base classes
        # has a metaclass with DocstringInheritanceMeta.
        for base_class in class_.__mro__[1:]:
            if docstring_style := cls.__get_parser_kind(base_class):
                return docstring_style
        return ""

    @staticmethod
    def __get_parser_kind(
        class_: type[Any],
    ) -> DocstringParser:
        """Return the docstring parser kind."""
        for base_meta in class_.__class__.__mro__:
            if issubclass(base_meta, _BaseGoogleDocstringInheritanceMeta):
                return Parser.google.value
            if issubclass(base_meta, _BaseNumpyDocstringInheritanceMeta):
                return Parser.numpy.value
        return ""
