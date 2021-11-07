<!--
 Copyright 2021 Antoine DECHAUME

 This work is licensed under the Creative Commons Attribution-ShareAlike 4.0
 International License. To view a copy of this license, visit
 http://creativecommons.org/licenses/by-sa/4.0/ or send a letter to Creative
 Commons, PO Box 1866, Mountain View, CA 94042, USA.
 -->

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/docstring-inheritance)
![PyPI](https://img.shields.io/pypi/v/docstring-inheritance)
![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)
![Codecov branch](https://img.shields.io/codecov/c/gh/AntoineD/docstring-inheritance/main)

`docstring-inheritance` is a python package to avoid writing and maintaining duplicated python docstrings.
The typical usage is to enable the inheritance of the docstrings from a base class
such that its derived classes fully or partly inherit the docstrings.

# Features

- Handle numpy and google docstring formats (i.e. sections based docstrings):
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

```commandline
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

Use the `NumpyDocstringInheritanceMeta` metaclass to inherit docstrings in numpy format.

Use the `GoogleDocstringInheritanceMeta` metaclass to inherit docstrings in google format.

```python
from docstring_inheritance import NumpyDocstringInheritanceMeta


class Parent(metaclass=NumpyDocstringInheritanceMeta):
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


# The inherited docstring is
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

`docstring-inheritance` provides functions to inherit the docstring of a callable from a string.
This is typically used to inherit the docstring of a function from another function.

Use the `inherit_google_docstring` function to inherit docstrings in google format.

Use the `inherit_numpy_docstring` function to inherit docstrings in numpy format.

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


# The inherited docstring is
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

The sections of an inherited docstring are sorted according to order defined in the
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
i.e. a section of the inheritor will not fully override the parent one:
- the keys in the parent section and not in the child section are inherited,
- the keys in the child section and not in the parent section are kept,
- for keys that are both in the parent and child section,
  the child ones are kept.

This allows to only document the new keys in such a section of an inheritor.
For instance:

```python
from docstring_inheritance import NumpyDocstringInheritanceMeta


class Parent(metaclass=NumpyDocstringInheritanceMeta):
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


# The inherited docstring is
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
The description for the attribute `y` has been overridden
and the description for the attribute `z` has been added.
The only remaining description from the parent is for the attribute `x`.

### Sections documenting signatures

Those sections are:
- `Parameters` (numpy format only)
- `Args` (google format only)

In addition to the inheritance behavior described [above](#sections-with-items):
- the arguments not existing in the inheritor signature are removed,
- the arguments are sorted according the inheritor signature,
- the arguments with no description are provided with a dummy description.

```python
from docstring_inheritance import GoogleDocstringInheritanceMeta


class Parent(metaclass=GoogleDocstringInheritanceMeta):
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


# The inherited docstring is
Child.meth.__doc__ = """
Args:
    w: Description for w
    y: Overridden description for y
    z: Description for z
"""
```

Here the keys are the argument names.
The description for the argument `y` has been overridden
and the description for the argument `z` has been added.
The only remaining description from the parent is for the argument `w`.

# Advanced usage

## Abstract base class

To create a parent class that both is abstract and has docstring inheritance,
an additional metaclass is required:

```python
import abc
from docstring_inheritance import NumpyDocstringInheritanceMeta


class Meta(abc.ABCMeta, NumpyDocstringInheritanceMeta):
    pass


class Parent(metaclass=Meta):
    pass
```
# Similar projects

[custom_inherit](https://github.com/rsokl/custom_inherit):
`docstring-inherit` started as fork of this project before being re-written,
we thank its author.
