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

from typing import ClassVar

from .base import AbstractDocstringInheritor


class NumpyDocstringInheritor(AbstractDocstringInheritor):
    """A class for inheriting docstrings in Numpy format."""

    # The section OtherParameters is not processed for the arguments.
    _ARGS_SECTION_NAME: ClassVar[str] = "Parameters"

    _SECTION_NAMES_WITH_ITEMS: ClassVar[set[str]] = {_ARGS_SECTION_NAME} | {
        "OtherParameters",
        "Attributes",
        "Methods",
    }

    MISSING_ARG_DESCRIPTION: ClassVar[
        str
    ] = f"\n    {AbstractDocstringInheritor.MISSING_ARG_DESCRIPTION}"

    @classmethod
    def _parse_one_section(
        cls, line1: str, line2_rstripped: str, reversed_section_body_lines: list[str]
    ) -> tuple[str, str] | tuple[None, None]:
        # See https://github.com/numpy/numpydoc/blob/d85f54ea342c1d223374343be88da94ce9f58dec/numpydoc/docscrape.py#L179  # noqa: B950
        if len(line2_rstripped) >= 3 and (set(line2_rstripped) in ({"-"}, {"="})):
            line1s = line1.rstrip()
            min_line_length = len(line1s)
            if line2_rstripped.startswith(
                "-" * min_line_length
            ) or line2_rstripped.startswith("=" * min_line_length):
                return line1s, cls._get_section_body(reversed_section_body_lines)
        return None, None

    @classmethod
    def _render_section(
        cls, section_name: str | None, section_body: str | dict[str, str]
    ) -> str:
        if section_name is None:
            assert isinstance(section_body, str)
            return section_body
        if isinstance(section_body, dict):
            section_body = "\n".join(
                f"{key}{value}" for key, value in section_body.items()
            )
        return f"{section_name}\n{'-' * len(section_name)}\n{section_body}"
