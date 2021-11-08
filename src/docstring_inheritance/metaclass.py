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
from types import FunctionType
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple


def create_dummy_func_with_doc(docstring: Optional[str]) -> Callable:
    """Return a dummy function with a given docstring."""

    def func():  # pragma: no cover
        pass

    func.__doc__ = docstring
    return func


class AbstractDocstringInheritanceMeta(type):
    """Abstract metaclass for inheriting class docstrings."""

    docstring_processor: Callable[[Optional[str], Callable], str]

    def __new__(
        cls, class_name: str, class_bases: Tuple[type], class_dict: Dict[str, Any]
    ) -> "AbstractDocstringInheritanceMeta":
        if class_bases:
            cls._process_class_docstring(class_bases, class_dict)
            cls._process_attrs_docstrings(class_bases, class_dict)
        return type.__new__(cls, class_name, class_bases, class_dict)

    @classmethod
    def _process_class_docstring(
        cls, class_bases: Tuple[type], class_dict: Dict[str, Any]
    ) -> None:
        dummy_func = create_dummy_func_with_doc(class_dict.get("__doc__"))

        for base_class in cls._get_mro_classes(class_bases):
            cls.docstring_processor(base_class.__doc__, dummy_func)

        class_dict["__doc__"] = dummy_func.__doc__

    @classmethod
    def _process_attrs_docstrings(
        cls, class_bases: Tuple[type], class_dict: Dict[str, Any]
    ) -> None:
        mro_classes = cls._get_mro_classes(class_bases)

        for attr_name, attr in class_dict.items():
            if not isinstance(attr, FunctionType):
                continue

            for mro_cls in mro_classes:
                if not hasattr(mro_cls, attr_name):
                    continue

                parent_doc = getattr(mro_cls, attr_name).__doc__
                if parent_doc is not None:
                    break
            else:
                continue

            cls.docstring_processor(parent_doc, attr)

    @staticmethod
    def _get_mro_classes(class_bases: Tuple[type]) -> List[type]:
        mro_classes = [mro_cls for base in class_bases for mro_cls in base.mro()]
        # Do not inherit the docstrings from the object base class.
        mro_classes.remove(object)
        return mro_classes
