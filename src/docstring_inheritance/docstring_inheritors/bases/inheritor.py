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
"""Base class for docstrings inheritors."""

from __future__ import annotations

import difflib
import inspect
import os
import warnings
from textwrap import indent
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import ClassVar
from typing import Dict
from typing import Sequence
from typing import cast

if TYPE_CHECKING:
    from . import SectionsType
    from .parser import BaseDocstringParser
    from .renderer import BaseDocstringRenderer

SIMILARITY_RATIO = float(os.environ.get("DOCSTRING_INHERITANCE_SIMILARITY_RATIO", 0.0))
SIMILARITY_RATIO = 0.9

if not (0 <= SIMILARITY_RATIO <= 1):
    raise ValueError("The docstring inheritance similarity ration must be in [0,1].")


class DocstringInheritanceWarning(UserWarning):
    """A warning for docstring inheritance."""


class BaseDocstringInheritor:
    """Base class for inheriting a docstring.

    This class produces a functor, it has no state and can only be called.
    """

    MISSING_ARG_DESCRIPTION: ClassVar[str] = "The description is missing."
    """The fall back description for a method argument without a description."""

    _MISSING_ARG_TEXT: ClassVar[str]
    """The actual formatted text bound to a missing method argument."""

    _DOCSTRING_PARSER: ClassVar[type[BaseDocstringParser]]
    """The docstring parser."""

    _DOCSTRING_RENDERER: ClassVar[type[BaseDocstringRenderer]]
    """The docstring renderer."""

    __child_func: Callable[..., Any]
    """The function or method to inherit the docstrings of."""

    def __init__(
        self,
        child_func: Callable[..., Any],
    ) -> None:
        self.__child_func = child_func

    @classmethod
    def inherit(
        cls,
        parent_doc: str | None,
        child_func: Callable[..., Any],
    ) -> None:
        """
        Args:
            parent_doc: The docstring of the parent.
            child_func: The child function which docstring inherit from the parent.
        """
        if parent_doc is None:
            return

        inheritor = cls(child_func)

        parent_sections = inheritor._DOCSTRING_PARSER.parse(parent_doc)
        child_sections = inheritor._DOCSTRING_PARSER.parse(child_func.__doc__)
        inheritor._warn_similar_sections(parent_sections, child_sections)
        inheritor._inherit_sections(
            inheritor._DOCSTRING_PARSER.SECTION_NAMES_WITH_ITEMS,
            inheritor._DOCSTRING_PARSER.ARGS_SECTION_NAME,
            inheritor._DOCSTRING_PARSER.SECTION_NAMES,
            inheritor._MISSING_ARG_TEXT,
            parent_sections,
            child_sections,
        )
        inheritor.__child_func.__doc__ = inheritor._DOCSTRING_RENDERER.render(
            child_sections
        )

    def _warn_similar_sections(
        self,
        parent_sections: SectionsType | dict[str, str],
        child_sections: SectionsType | dict[str, str],
        section_path: Sequence[str] = (),
    ) -> None:
        """Issue a warning when the parent and child sections are similar.

        Args:
            parent_sections: The parent sections.
            child_sections: The child sections.
            section_path: The hierarchy of section names.
        """
        if SIMILARITY_RATIO == 0.0:
            return

        for section_name, child_section in child_sections.items():
            parent_section = parent_sections.get(section_name)
            if parent_section is None:
                continue

            # TODO: add Raises section?
            if section_name in self._DOCSTRING_PARSER.SECTION_NAMES_WITH_ITEMS:
                self._warn_similar_sections(
                    cast(Dict[str, str], parent_section),
                    cast(Dict[str, str], child_section),
                    section_path=[section_name],
                )
            else:
                self._warn_similar_section(
                    cast(str, parent_section),
                    cast(str, child_section),
                    section_path=[*section_path, section_name],
                )

    def _warn_similar_section(
        self,
        parent_doc: str,
        child_doc: str,
        section_path: list[str],
    ) -> None:
        """Issue a warning when the parent and child docs are similar.

        Args:
            parent_doc: The parent documentation.
            child_doc: The child documentation.
            section_path: The hierarchy of section names.
        """
        ratio = difflib.SequenceMatcher(None, parent_doc, child_doc).ratio()
        if ratio > SIMILARITY_RATIO:
            msg = (
                f"the docstrings have a similarity ration of {ratio}, "
                f"the parent doc is\n{indent(parent_doc, ' ' * 4)}\n"
                f"the child doc is\n{indent(child_doc, ' ' * 4)}"
            )
            if section_path[0] is None:
                section_path[0] = "Summary"
            self._warn(section_path, msg)

    def _warn(self, section_path: list[str], msg: str) -> None:
        """Issue a warning.

        Args:
            section_path: The hierarchy of section names.
            msg: The warning message.
        """
        msg = (
            f"File {inspect.getfile(self.__child_func)}: "
            f"Function {self.__child_func.__qualname__}: "
            f"Section {'/'.join(section_path)}: " + msg
        )
        warnings.warn(msg, category=DocstringInheritanceWarning, stacklevel=2)

    def _inherit_sections(
        self,
        section_names_with_items: set[str],
        args_section_name: str,
        section_names: list[str],
        missing_arg_text: str,
        parent_sections: SectionsType,
        child_sections: SectionsType,
    ) -> None:
        """Inherit the sections of a child from the parent sections.

        Args:
            section_names_with_items: The names of the section with items.
            args_section_name: The name of the section with method arguments.
            section_names: The names of all the section.
            missing_arg_text: This text for the missing arguments.
            parent_sections: The parent docstring sections.
            child_sections: The child docstring sections.
        """
        # TODO:
        # prnt_only_raises = "Raises" in parent_sections and not (
        #     "Returns" in parent_sections or "Yields" in parent_sections
        # )
        #
        # if prnt_only_raises and (
        #     "Returns" in sections or "Yields" in sections
        # ):
        #     parent_sections["Raises"] = None
        parent_section_names = parent_sections.keys()
        child_section_names = child_sections.keys()

        temp_sections = {}

        # Sections in parent but not child.
        parent_section_names_to_copy = parent_section_names - child_section_names
        for section_name in parent_section_names_to_copy:
            temp_sections[section_name] = parent_sections[section_name]

        # Remaining sections in child.
        child_sections_names_to_copy = (
            child_section_names - parent_section_names_to_copy
        )
        for section_name in child_sections_names_to_copy:
            temp_sections[section_name] = child_sections[section_name]

        # For sections with items, the sections common to parent and child are merged.
        common_section_names_with_items = (
            parent_section_names & child_section_names & section_names_with_items
        )

        for section_name in common_section_names_with_items:
            temp_section_items = cast(
                Dict[str, str], parent_sections[section_name]
            ).copy()
            temp_section_items.update(
                cast(Dict[str, str], child_sections[section_name])
            )

            temp_sections[section_name] = temp_section_items

        # Args section shall be filtered.
        args_section = self._filter_args_section(
            missing_arg_text,
            cast(Dict[str, str], temp_sections.get(args_section_name, {})),
            args_section_name,
        )

        if args_section:
            temp_sections[args_section_name] = args_section
        elif args_section_name in temp_sections:
            # The args section is empty, there is nothing to document.
            del temp_sections[args_section_name]

        # Reorder the standard sections.
        child_sections.clear()
        child_sections.update(
            {
                section_name: temp_sections.pop(section_name)
                for section_name in section_names
                if section_name in temp_sections
            }
        )

        # Add the remaining non-standard sections.
        child_sections.update(temp_sections)

    def _filter_args_section(
        self,
        missing_arg_text: str,
        section_items: dict[str, str],
        section_name: str = "",
    ) -> dict[str, str]:
        """Filter the args section items with the args of a signature.

        The argument ``self`` is removed. The arguments are ordered according to the
        signature of ``func``. An argument of ``func`` missing in ``section_items`` gets
        a default description defined in :attr:`._MISSING_ARG_TEXT`.

        Args:
            missing_arg_text: This text for the missing arguments.
            section_name: The name of the section.
            section_items: The docstring section items.

        Returns:
            The section items filtered with the function signature.
        """
        full_arg_spec = inspect.getfullargspec(self.__child_func)

        all_args = full_arg_spec.args
        if "self" in all_args:
            all_args.remove("self")

        if full_arg_spec.varargs is not None:
            all_args += [f"*{full_arg_spec.varargs}"]

        all_args += full_arg_spec.kwonlyargs

        if full_arg_spec.varkw is not None:
            all_args += [f"**{full_arg_spec.varkw}"]

        ordered_section = {}
        for arg in all_args:
            self._warn(
                [section_name], f"The docstring for the argument '{arg}' is missing."
            )
            ordered_section[arg] = section_items.get(arg, missing_arg_text)

        return ordered_section
