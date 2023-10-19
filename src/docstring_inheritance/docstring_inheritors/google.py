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

import textwrap
from typing import ClassVar

from .bases.inheritor import BaseDocstringInheritor
from .bases.parser import BaseDocstringParser
from .bases.renderer import BaseDocstringRenderer


class DocstringRenderer(BaseDocstringRenderer):
    @staticmethod
    def _render_section(
        section_name: str | None,
        section_body: str | dict[str, str],
    ) -> str:
        if section_name is None:
            assert isinstance(section_body, str)
            return section_body
        if isinstance(section_body, dict):
            section_body = "\n".join(
                f"{key}{value}" for key, value in section_body.items()
            )
        section_body = textwrap.indent(section_body, " " * 4)
        return f"{section_name}:\n{section_body}"


class DocstringParser(BaseDocstringParser):
    ARGS_SECTION_NAME: ClassVar[str] = "Args"
    SECTION_NAMES: ClassVar[list[str | None]] = list(BaseDocstringParser.SECTION_NAMES)
    SECTION_NAMES[1] = ARGS_SECTION_NAME
    SECTION_NAMES_WITH_ITEMS: ClassVar[set[str]] = {
        ARGS_SECTION_NAME,
        "Attributes",
        "Methods",
    }

    @classmethod
    def _get_section_body(
        cls,
        reversed_section_body_lines: list[str],
    ) -> str:
        return textwrap.dedent(super()._get_section_body(reversed_section_body_lines))

    @classmethod
    def _parse_one_section(
        cls,
        line1: str,
        line2_rstripped: str,
        reversed_section_body_lines: list[str],
    ) -> tuple[str, str] | tuple[None, None]:
        # See https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings  # noqa: B950
        # The parsing of a section is complete when the first line line1 has:
        # - no leading blank spaces,
        # - ends with :,
        # - has a second line indented by at least 2 blank spaces,
        # - has a section name.
        line1_rstripped = line1.rstrip()
        if (
            not line1_rstripped.startswith(" ")
            and line1_rstripped.endswith(":")
            and line2_rstripped.startswith("  ")
            and line1_rstripped[:-1].strip() in cls.SECTION_NAMES
        ):
            reversed_section_body_lines += [line2_rstripped]
            return line1_rstripped.rstrip(" :"), cls._get_section_body(
                reversed_section_body_lines
            )
        return None, None


class GoogleDocstringInheritor(BaseDocstringInheritor):
    _MISSING_ARG_TEXT = f": {BaseDocstringInheritor.MISSING_ARG_DESCRIPTION}"
    _DOCSTRING_PARSER = DocstringParser
    _DOCSTRING_RENDERER = DocstringRenderer
