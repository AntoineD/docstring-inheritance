`docstring-inheritance` is a python package to avoid writing and maintaining duplicated python docstrings.
The typical usage is to enable the inheritance from a base class
such that its derived classes fully or partly inherit the docstrings.

# Features

- Handle numpy and google docstring formats, i.e. sections based docstrings.
    - [NumPy docstring format specification](https://numpydoc.readthedocs.io/en/latest/format.html)
    - [Google docstring format specification](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- Handle docstrings for functions, classes, methods, class methods, static methods, properties.
- Handle docstrings for classes with multiple or multi-level inheritance.
- Docstring sections are inherited individually,
  like methods for a classes.
- For docstring sections documenting signatures,
  the signature arguments are inherited individually.
- Minimum performance cost: the inheritance is performed at import time,
  not for each call.
- Compatible with rendering the documentation with [Sphinx](http://www.sphinx-doc.org/).

# Licenses

The source code is distributed under the MIT license.
The documentation is distributed under the CC BY-SA 4.0 license.
The dependencies, with their licenses, are given in the CREDITS.rst file.

# Installation

Install via pip:

```shell
    pip install docstring-inheritance
```

# Basic Usage

## Inheriting docstrings for classes

`docstring-inheritance` provides
[metaclasses](https://docs.python.org/3/reference/datamodel.html#customizing-class-creation)
to enable the docstrings of a class to be inherited from its base classes.
This feature is automatically transmitted to its derived classes as well.
The docstring inheritance is performed for the docstrings of the:
- class
- methods
- classmethods
- staticmethods
- properties

Use `NumpyDocstringInheritanceMeta` to inherit docstrings with numpy format.
Use `GoogleDocstringInheritanceMeta` to inherit docstrings with google format.

```python
from docstring_inheritance import NumpyDocstringInheritorMeta


class Parent(metaclass=NumpyDocstringInheritorMeta):
    def meth(self, x, y=None):
        """Parent summary.

        Parameters
        ----------
        x:
           Description for x.
        y:
           Description for y.

        Notes
        -----
        Parent notes.
        """

class Child(Parent):
    def meth(self, x, z):
        """
        Parameters
        ----------
        z:
           Description for z.

        Returns
        -------
        Something.

        Notes
        -----
        Child notes.
        """

Child.meth.__doc__ = """Parent summary.

Parameters
----------
x:
   Description for x.
z:
   Description for z.

Returns
-------
Something.

Notes
-----
Child notes.
"""
```

## Inheriting docstrings for functions

`docstring-inheritance` provides functions to inherit the docstring of a callable
from a string.
This is typically used to inherit the docstring of a function from another function.
Use `inherit_google_docstring` to inherit docstrings with google format.
Use `inherit_numpy_docstring` to inherit docstrings with numpy format.

```python
from docstring_inheritance import inherit_google_docstring

def parent():
    """Parent summary.

    Args:
        x: Description for x.
        y: Description for y.

    Notes:
        Parent notes.
    """


def child():
    """
    Args:
        z: Description for z.

    Returns:
        Something.

    Notes:
        Child notes.
    """

inherit_google_docstring(parent.__doc__, child)
child.__doc__ = """Parent summary.

Args:
    x: Description for x.
    z: Description for z.

Returns:
    Something.

Notes:
    Child notes.
"""
```

# Docstring inheritance specification

## Sections order

The sections of an inherited docstring are sorted according to order defined in
[NumPy docstring format specification](https://numpydoc.readthedocs.io/en/latest/format.html):
- `Summary`
- `Extended summary`
- `Parameters` for the NumPy format or `Args` for the Google format
- `Returns`
- `Yields`
- `Receives`
- `Other Parameters`
- `Attributes`
- `Methods`
- `Raises`
- `Warns`
- `Warnings`
- `See Also`
- `Notes`
- `References`
- `Examples`
- sections with other names come next

This ordering is also used for the docstring written with the
[Google docstring format specification](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
even though it does not define all of these sections.

## Sections with items

Those sections are:
- `Other Parameters`
- `Methods`
- `Attributes`

The inheritance is done at the key level,
i.e. an inheritor section will not fully override the parent one:
- keys of the parent section and not in the child section are inherited,
- keys of the child section and not in the parent section are kept,
- for keys that are both in the parent and child sections,
  the child ones are kept.

This allows to only document the new keys in such a section of an inheritor.
For instance:

```python
from docstring_inheritance import NumpyDocstringInheritorMeta

class Parent(metaclass=NumpyDocstringInheritorMeta):
    """
    Attributes
    ----------
    x:
       Description for x
    y:
       Description for y
    """

class Child(Parent):
    """
    Attributes
    ----------
    y:
       Overridden description for y
    z:
       Description for z
    """

Child.__doc__ = """
Attributes
----------
x:
   Description for x
y:
   Overridden description for y
z:
   Description for z
"""
```

Here the keys are the attribute names.
The description for the key `y` has been overridden
and the description for the key `z` has been added.
The only remaining description from the parent is for the key `x`.

### Sections documenting signatures

Those sections are:
- `Parameters` (numpy format only)
- `Args` (google format only)

In addition to the inheritance behavior described [above](#docstring-sections-not-for-signatures):
- arguments not existing in the inheritor signature are removed,
- arguments are sorted according the inheritor signature,
- missing arguments' descriptions are provided with a dummy description.

```python
from docstring_inheritance import GoogleDocstringInheritorMeta

class Parent(metaclass=GoogleDocstringInheritorMeta):
    def meth(self, w, x, y):
        """
        Args:
            w: Description for w
            x: Description for x
            y: Description for y
        """

class Child(Parent):
    def meth(self, w, y, z):
        """
        Args:
            z: Description for z
            y: Overridden description for y
        """

Child.meth.__doc__ = """
Args:
    w: Description for w
    y: Overridden description for y
    z: Description for z
"""
```

Here the keys are the arguments names.
The description for the key `y` has been overridden
and the description for the key `z` has been added.
The only remaining description from the parent is for the key `w`.

# Advanced usage

## Abstract base class

To create a parent class that both is abstract and has docstring inheritance,
an additional metaclass is required:

```python
import abc
from docstring_inheritance import NumpyDocstringInheritorMeta


class Meta(abc.ABCMeta, NumpyDocstringInheritorMeta):
    pass


class Parent(metaclass=Meta):
    ...
```
