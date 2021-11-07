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
from itertools import dropwhile
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from . import parse_section_items
from .base import AbstractDocstringProcessor


class NumpyDocstringProcessor(AbstractDocstringProcessor):

    _SECTION_NAMES = [
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

    _ARGS_SECTION_ITEMS_NAMES = {
        "Parameters",
        "Other Parameters",
    }

    _SECTION_ITEMS_NAMES = _ARGS_SECTION_ITEMS_NAMES | {
        "Attributes",
        "Methods",
    }

    MISSING_ARG_DESCRIPTION = f":\n{AbstractDocstringProcessor.MISSING_ARG_DESCRIPTION}"

    @classmethod
    def _parse_section_items(cls, section_body: str) -> Dict[str, str]:
        return parse_section_items(section_body)

    @classmethod
    def _parse_one_section(
        cls, line1: str, line2_rstripped: str, reversed_section_body_lines: List[str]
    ) -> Union[Tuple[str, str], Tuple[None, None]]:
        # See https://github.com/numpy/numpydoc/blob/d85f54ea342c1d223374343be88da94ce9f58dec/numpydoc/docscrape.py#L179  # noqa: E501
        if len(line2_rstripped) >= 3 and (set(line2_rstripped) in ({"-"}, {"="})):
            line1s = line1.rstrip()
            min_line_length = len(line1s)
            if line2_rstripped.startswith(
                "-" * min_line_length
            ) or line2_rstripped.startswith("=" * min_line_length):
                return line1s, cls._get_section_body(reversed_section_body_lines)
        return None, None

    @classmethod
    def _get_section_body(cls, reversed_section_body_lines: List[str]) -> str:
        reversed_section_body_lines = list(
            dropwhile(lambda x: not x, reversed_section_body_lines)
        )
        reversed_section_body_lines.reverse()
        return "\n".join(reversed_section_body_lines)

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
        return f"{section_name}\n{'-' * len(section_name)}\n{section_body}"
