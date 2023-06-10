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

import abc
import inspect
import re
import sys
from itertools import dropwhile
from itertools import tee
from typing import Any
from typing import Callable
from typing import cast
from typing import ClassVar
from typing import Dict
from typing import Optional
from typing import Union

SectionsType = Dict[Optional[str], Union[str, Dict[str, str]]]


if sys.version_info >= (3, 10):  # pragma: >=3.10 cover
    from itertools import pairwise
else:  # pragma: <3.10 cover
    # See https://docs.python.org/3/library/itertools.html#itertools.pairwise
    def pairwise(iterable):
        a, b = tee(iterable)
        next(b, None)
        return zip(a, b)


class AbstractDocstringInheritor:
    """Abstract base class for inheriting a docstring.

    This class produces a functor, it has no state and can only be called.
    """

    _SECTION_NAMES: ClassVar[list[str | None]] = [
        None,
        "Parameters",
        "Returns",
        "Yields",
        "Receives",
        "Other Parameters",
        "Attributes",
        "Methods",
        "Raises",
        "Warns",
        "Warnings",
        "See Also",
        "Notes",
        "References",
        "Examples",
    ]
    """Names of the sections."""

    _ARGS_SECTION_NAMES: ClassVar[set[str]]
    """Names of the sections for method and function arguments."""

    _SECTION_NAMES_WITH_ITEMS: ClassVar[set[str]]
    """Names of the sections with items."""

    MISSING_ARG_DESCRIPTION: ClassVar[str] = "The description is missing."
    """Fall back description for an argument without a given description."""

    def __call__(self, parent_doc: str | None, child_func: Callable[..., Any]) -> None:
        """
        Args:
            parent_doc: The docstring of the parent.
            child_func: The child function which docstring inherit from the parent.
        """
        if parent_doc is None:
            return

        parent_sections = self._parse_sections(parent_doc)
        child_sections = self._parse_sections(child_func.__doc__)
        self._filters_sections(child_sections)
        self._inherit_sections(
            parent_sections, child_sections, child_func
        )
        child_func.__doc__ = self._render_docstring(child_sections)

    @classmethod
    def _get_section_body(cls, reversed_section_body_lines: list[str]) -> str:
        """Create the docstring of a section.

        Args:
            reversed_section_body_lines: The lines of docstrings in reversed order.

        Returns:
            The docstring of a section.
        """
        reversed_section_body_lines = list(
            dropwhile(lambda x: not x, reversed_section_body_lines)
        )
        reversed_section_body_lines.reverse()
        return "\n".join(reversed_section_body_lines)

    @classmethod
    @abc.abstractmethod
    def _parse_one_section(
        cls, line1: str, line2_rstripped: str, reversed_section_body_lines: list[str]
    ) -> tuple[str, str] | tuple[None, None]:
        """Parse the name and body of a docstring section.

        It does not parse section_items items.

        Returns:
            The name and docstring body parts of a section,
            or ``(None, None)`` if no section is found.
        """

    @classmethod
    @abc.abstractmethod
    def _render_section(
        cls, section_name: str | None, section_body: str | dict[str, str]
    ) -> str:
        """Return a rendered docstring section.

        Args:
            section_name: The name of a docstring section.
            section_body: The body of a docstring section.

        Returns:
            The rendered docstring.
        """

    @classmethod
    def _parse_sections(cls, docstring: str | None) -> SectionsType:
        """Parse the sections of a docstring.

        Args:
            docstring: The docstring to parse.

        Returns:
            The parsed sections.
        """
        if not docstring:
            return {}

        lines = inspect.cleandoc(docstring).splitlines()

        # It seems easier to work reversed.
        lines_pairs = iter(pairwise(reversed(lines)))

        reversed_section_body_lines: list[str] = []
        reversed_sections: dict[str, str | dict[str, str]] = {}

        # Iterate 2 lines at a time to look for the section_items headers
        # that are underlined.
        for line2, line1 in lines_pairs:
            line2_rstripped = line2.rstrip()

            section_name, section_body = cls._parse_one_section(
                line1, line2_rstripped, reversed_section_body_lines
            )
            if section_name is not None and section_body is not None:
                if section_name in cls._SECTION_NAMES_WITH_ITEMS:
                    reversed_sections[section_name] = cls._parse_section_items(
                        section_body
                    )
                else:
                    reversed_sections[section_name] = section_body

                # We took into account line1 in addition to line2,
                # we no longer need to process line1.
                try:
                    next(lines_pairs)
                except StopIteration:
                    # The docstring has no summary section_items.
                    has_summary = False
                    break

                reversed_section_body_lines = []
                continue

            reversed_section_body_lines += [line2_rstripped]
        else:
            has_summary = True

        sections: SectionsType = {}

        if has_summary:
            # Add the missing first line because it is not taken into account
            # by the above loop.
            reversed_section_body_lines += [lines[0]]

            # Add the section_items with the short and extended summaries.
            sections[None] = cls._get_section_body(reversed_section_body_lines)

        # dict.items() is not reversible in python < 3.8: cast to tuple.
        for section_name_, section_body_ in reversed(tuple(reversed_sections.items())):
            sections[section_name_] = section_body_

        return sections

    @classmethod
    def _inherit_sections(
        cls,
        parent_sections: SectionsType,
        child_sections: SectionsType,
        child_func: Callable[..., Any],
    ) -> SectionsType:
        """Inherit the sections of a child from the parent sections.

        Args:
            parent_sections: The parent docstring sections.
            child_sections: The child docstring sections.
            child_func: The child function which sections inherit from the parent.

        Returns:
            The inherited sections.
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
        parent_section_names = set(parent_sections)
        child_section_names = set(child_sections)

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
            parent_section_names & child_section_names & cls._SECTION_NAMES_WITH_ITEMS
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
        for section_name in temp_sections.keys() & cls._ARGS_SECTION_NAMES:
            temp_sections[section_name] = cls._filter_args_section(
                child_func,
                cast(Dict[str, str], temp_sections[section_name]),
            )

        # Reorder the standard sections.
        new_child_sections = {
            section_name: temp_sections.pop(section_name)
            for section_name in cls._SECTION_NAMES
            if section_name in temp_sections
        }

        # Add the remaining non-standard sections.
        new_child_sections.update(temp_sections)

        return new_child_sections

    @classmethod
    def _filter_args_section(
        cls,
        func: Callable[..., Any],
        section_items: dict[str, str],
    ) -> dict[str, str]:
        """Filter the args section items with the args of a signature.

        The argument ``self`` is removed. The arguments are ordered according to the
        signature of ``func``. An argument of ``func`` missing in ``section_items`` gets
        a default description defined in :attr:`.MISSING_ARG_DESCRIPTION`.

        Args:
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
                ordered_section[arg] = cls.MISSING_ARG_DESCRIPTION

        return ordered_section

    @classmethod
    def _render_docstring(cls, sections: SectionsType) -> str:
        """Render a docstring.

        Args:
            sections: The docstring sections to render.

        Returns:
            The rendered docstring.
        """
        if not sections:
            return ""

        rendered_sections = []

        for section_name, section_body in sections.items():
            rendered_sections += [cls._render_section(section_name, section_body)]

        rendered = "\n\n".join(rendered_sections)

        if None not in sections:
            # Add an empty summary line,
            # Sphinx will not behave correctly otherwise with the Google format.
            return "\n" + rendered

        return rendered

    _SECTION_ITEMS_REGEX = re.compile(
        r"(\**\w+)(.*?)(?:$|(?=\n\**\w+))", flags=re.DOTALL
    )

    @classmethod
    def _parse_section_items(cls, section_body: str) -> dict[str, str]:
        """Parse the section items for numpy and google docstrings.

        Args:
            section_body: The body of a docstring section.

        Returns:
            The parsed section body.
        """
        return dict(cls._SECTION_ITEMS_REGEX.findall(section_body))
