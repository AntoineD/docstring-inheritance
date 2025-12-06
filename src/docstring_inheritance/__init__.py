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
"""Docstring inheritance entry point."""

from __future__ import annotations

from os import environ as _environ
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any

_enable_inheritance: bool = bool(_environ.get("DOCSTRING_INHERITANCE_ENABLE", False))
"""Whether the inheritance of the docctrings is enabled."""

if _enable_inheritance:
    from ._internal import GoogleDocstringInheritanceInitMeta
    from ._internal import GoogleDocstringInheritanceMeta
    from ._internal import NumpyDocstringInheritanceInitMeta
    from ._internal import NumpyDocstringInheritanceMeta
    from ._internal import inherit_google_docstring
    from ._internal import inherit_numpy_docstring
else:
    GoogleDocstringInheritanceMeta = type  # type: ignore[assignment, misc]
    GoogleDocstringInheritanceInitMeta = type  # type: ignore[assignment, misc]
    NumpyDocstringInheritanceMeta = type  # type: ignore[assignment, misc]
    NumpyDocstringInheritanceInitMeta = type  # type: ignore[assignment, misc]

    def inherit_google_docstring(  # noqa: D103
        parent_doc: str | None,
        child_func: Callable[..., Any],
    ) -> None:
        pass

    def inherit_numpy_docstring(  # noqa: D103
        parent_doc: str | None,
        child_func: Callable[..., Any],
    ) -> None:
        pass
