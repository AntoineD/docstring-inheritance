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
from typing import Any
from typing import Callable
from typing import cast
from typing import ClassVar
from typing import Dict

from . import SectionsType
from .parser import BaseDocstringParser
from .renderer import BaseDocstringRenderer


class BaseDocstringInheritor:
    """Base class for inheriting a docstring.

    This class produces a functor, it has no state and can only be called.
    """

    MISSING_ARG_DESCRIPTION: ClassVar[str] = "The description is missing."
    """The fall back description for a method argument without a description."""

    INHERIT_SECTION_TAG: ClassVar[str] = "__inherit_section_doc__"
    """Placeholder used to indicate that a section docstring shall be inherited."""

    _MISSING_ARG_TEXT: ClassVar[str]
    """The actual formatted text bound to a missing method argument."""

    _DOCSTRING_PARSER: ClassVar[type[BaseDocstringParser]]
    """The docstring parser."""

    _DOCSTRING_RENDERER: ClassVar[type[BaseDocstringRenderer]]
    """The docstring renderer."""

    def __call__(
        self,
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

        parent_sections = self._DOCSTRING_PARSER.parse(parent_doc)
        child_sections = self._DOCSTRING_PARSER.parse(child_func.__doc__)
        self._filters_inherited_sections(child_sections)
        self._inherit_sections(
            self._DOCSTRING_PARSER.SECTION_NAMES_WITH_ITEMS,
            self._DOCSTRING_PARSER.ARGS_SECTION_NAME,
            self._DOCSTRING_PARSER.SECTION_NAMES,
            self._MISSING_ARG_TEXT,
            parent_sections,
            child_sections,
            child_func,
        )
        child_func.__doc__ = self._DOCSTRING_RENDERER.render(child_sections)

    @classmethod
    def _filters_inherited_sections(
        cls,
        sections: SectionsType | dict[str, str],
    ) -> None:
        """Filter the sections for item to be explicitly inherited.

        Args:
            sections: The sections to filter.
        """
        for key, item in tuple(sections.items()):
            if isinstance(item, dict):
                cls._filters_inherited_sections(item)
            elif item.strip().startswith(cls.INHERIT_SECTION_TAG):
                del sections[key]

    @classmethod
    def _inherit_sections(
        cls,
        section_names_with_items: set[str],
        args_section_name: str,
        section_names: list[str],
        missing_arg_text: str,
        parent_sections: SectionsType,
        child_sections: SectionsType,
        child_func: Callable[..., Any],
    ) -> None:
        """Inherit the sections of a child from the parent sections.

        Args:
            section_names_with_items: The names of the section with items.
            args_section_name: The name of the section with method arguments.
            section_names: The names of all the section.
            missing_arg_text: This text for the missing arguments.
            parent_sections: The parent docstring sections.
            child_sections: The child docstring sections.
            child_func: The child function which sections inherit from the parent.
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
        args_section = cls._filter_args_section(
            missing_arg_text,
            child_func,
            cast(Dict[str, str], temp_sections.get(args_section_name, {})),
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

    @staticmethod
    def _filter_args_section(
        missing_arg_text: str,
        func: Callable[..., Any],
        section_items: dict[str, str],
    ) -> dict[str, str]:
        """Filter the args section items with the args of a signature.

        The argument ``self`` is removed. The arguments are ordered according to the
        signature of ``func``. An argument of ``func`` missing in ``section_items`` gets
        a default description defined in :attr:`._MISSING_ARG_TEXT`.

        Args:
            missing_arg_text: This text for the missing arguments.
            func: The function that provides the signature.
            section_items: The docstring section items.

        Returns:
            The section items filtered with the function signature.
        """
        args, varargs, varkw, _, kwonlyargs = inspect.getfullargspec(func)[:5]

        all_args = args
        if "self" in all_args:
            all_args.remove("self")

        if varargs is not None:
            all_args += [f"*{varargs}"]

        all_args += kwonlyargs

        if varkw is not None:
            all_args += [f"**{varkw}"]

        ordered_section = dict()
        for arg in all_args:
            if arg in section_items:
                ordered_section[arg] = section_items[arg]
            else:
                ordered_section[arg] = missing_arg_text

        return ordered_section
