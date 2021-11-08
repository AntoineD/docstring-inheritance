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
from typing import Callable
from typing import Optional

from .metaclass import AbstractDocstringInheritanceMeta
from .processors.google import GoogleDocstringProcessor
from .processors.numpy import NumpyDocstringProcessor

DocstringProcessorType = Callable[[Optional[str], Callable], None]

inherit_numpy_docstring = NumpyDocstringProcessor()
inherit_google_docstring = GoogleDocstringProcessor()


def DocstringInheritanceMeta(  # noqa: N802
    docstring_processor: DocstringProcessorType,
) -> type:
    metaclass = type(
        AbstractDocstringInheritanceMeta.__name__,
        AbstractDocstringInheritanceMeta.__bases__,
        dict(AbstractDocstringInheritanceMeta.__dict__),
    )
    metaclass.docstring_processor = docstring_processor
    return metaclass


# Helper metaclasses for each docstring styles.
NumpyDocstringInheritanceMeta = DocstringInheritanceMeta(inherit_numpy_docstring)
GoogleDocstringInheritanceMeta = DocstringInheritanceMeta(inherit_google_docstring)
