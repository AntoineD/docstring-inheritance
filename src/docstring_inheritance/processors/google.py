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
import textwrap
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from . import parse_section_items
from .base import AbstractDocstringProcessor
from .numpy import NumpyDocstringProcessor


class GoogleDocstringProcessor(AbstractDocstringProcessor):
    _SECTION_NAMES = list(NumpyDocstringProcessor._SECTION_NAMES)
    _SECTION_NAMES[1] = "Args"

    _ARGS_SECTION_ITEMS_NAMES = {"Args"}

    _SECTION_ITEMS_NAMES = _ARGS_SECTION_ITEMS_NAMES | {
        "Attributes",
        "Methods",
    }

    MISSING_ARG_DESCRIPTION = f": {AbstractDocstringProcessor.MISSING_ARG_DESCRIPTION}"

    @classmethod
    def _parse_section_items(cls, section_body: str) -> Dict[str, str]:
        return parse_section_items(section_body)

    @classmethod
    def _get_section_body(cls, reversed_section_body_lines: List[str]) -> str:
        return textwrap.dedent(
            NumpyDocstringProcessor._get_section_body(reversed_section_body_lines)
        )

    @classmethod
    def _parse_one_section(
        cls, line1: str, line2_rstripped: str, reversed_section_body_lines: List[str]
    ) -> Union[Tuple[str, str], Tuple[None, None]]:
        # See https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings  # noqa: E501
        line1s = line1.rstrip()
        if (
            not line1s.startswith(" ")
            and line1s.endswith(":")
            and line2_rstripped.startswith("  ")
        ):
            reversed_section_body_lines += [line2_rstripped]
            return line1s.rstrip(" :"), cls._get_section_body(
                reversed_section_body_lines
            )
        return None, None

    @classmethod
    def _render_section(
        cls, section_name: Optional[str], section_body: Union[str, Dict[str, str]]
    ) -> str:
        if section_name is None:
            return section_body
        if isinstance(section_body, dict):
            section_body = "\n".join(
                f"{key}{value}" for key, value in section_body.items()
            )
        section_body = textwrap.indent(section_body, " " * 4)
        return f"{section_name}:\n{section_body}"
