<!--
 Copyright 2021 Antoine DECHAUME

 This work is licensed under the Creative Commons Attribution 4.0
 International License. To view a copy of this license, visit
 http://creativecommons.org/licenses/by/4.0/ or send a letter to Creative
 Commons, PO Box 1866, Mountain View, CA 94042, USA.
 -->

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/docstring-inheritance)
![PyPI](https://img.shields.io/pypi/v/docstring-inheritance)
![Conda (channel only)](https://img.shields.io/conda/vn/conda-forge/docstring-inheritance)
![Codecov branch](https://img.shields.io/codecov/c/gh/AntoineD/docstring-inheritance/main)

`docstring-inheritance` is a Python package that eliminates the need to write and maintain duplicate docstrings.
Its primary purpose is to enable docstrings defined in a base class to be inherited—either wholly or partially—by derived subclasses.
Inheritance is applied only when it is explicitly enabled, typically during documentation builds.

# Features

- Handle numpy and google docstring formats (i.e. sections based docstrings):
  - [NumPy docstring format specification](https://numpydoc.readthedocs.io/en/latest/format.html)
  - [Google docstring format specification](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- Handle docstrings for functions, classes, methods, class methods, static methods, properties.
- Handle docstrings for classes with multiple or multi-level inheritance.
- Docstring sections are inherited individually, like methods.
- For docstring sections documenting signatures,
  the signature arguments are inherited individually.
- Minimum performance cost: the inheritance is performed at import time,
  not for each call.
- Compatible with rendering the documentation with [Sphinx](http://www.sphinx-doc.org/) and [mkdocs](https://www.mkdocs.org/) (See [below](#mkdocs)). (Be sure to install the package your are building the docs for in the environment used to build the docs.)
- Missing docstring sections for signature arguments can be notified by warnings
  when the environment variable `DOCSTRING_INHERITANCE_WARNS` is set.
- Docstring sections can be compared to detect duplicated or similar contents that could be inherited.
- By default, the metaclasses and functions in this package do nothing, so they have virtually no performance impact.
- When building documentation, enable the inheritance of the docstrings by defining the environment variable `DOCSTRING_INHERITANCE_ENABLE=1`.

# Licenses

The source code is distributed under the MIT license.
The documentation is distributed under the CC BY 4.0 license.
The dependencies, with their licenses, are given in the CREDITS.md file.

# Installation

Install with pip:

```commandline
pip install docstring-inheritance
```

Or with conda:

```commandline
conda install -c conda-forge docstring-inheritance
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

Use the `NumpyDocstringInheritanceMeta` metaclass to inherit docstrings in numpy format
if `__init__` method is documented in its own docstring.
Otherwise, if `__init__` method is documented in the class docstring,
use the `NumpyDocstringInheritanceInitMeta` metaclass.

Use the `GoogleDocstringInheritanceMeta` metaclass to inherit docstrings in google format
if `__init__` method is documented in its own docstring.
Otherwise, if `__init__` method is documented in the class docstring,
use the `GoogleDocstringInheritanceInitMeta` metaclass.

```python
from docstring_inheritance import NumpyDocstringInheritanceMeta


class Parent(metaclass=NumpyDocstringInheritanceMeta):
  def method(self, x, y=None):
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
  def method(self, x, z):
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
Child.method.__doc__ == """Parent summary.

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
child.__doc__ == """Parent summary.

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

## Sections without sub-sections

For sections that have no sub-sections,
like the `Returns` section for instance,
the inheritance applies to the entire content of the section.

## Sections with sub-sections

Those sections are:

- `Args`
- `Parameters`
- `Other Parameters`
- `Methods`
- `Attributes`

The inheritance applies at the sub-section levels.
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
Child.__doc__ == """
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

Here the section is `Attributes`,
the sub-sections describe the attribute names.
The description for the attribute `y` has been overridden
and the description for the attribute `z` has been added.
The only remaining description from the parent is for the attribute `x`.

### Sections documenting signatures

Those sections are:

- `Parameters` (numpy format only)
- `Args` (google format only)

In addition to the inheritance behavior described [above](#sections-with-sub-sections):

- the arguments not existing in the child signature are removed,
- the arguments are sorted according the child signature,
- the arguments with no description are provided with a dummy description.

```python
from docstring_inheritance import GoogleDocstringInheritanceMeta


class Parent(metaclass=GoogleDocstringInheritanceMeta):
  def method(self, w, x, y):
    """
    Args:
        w: Description for w
        x: Description for x
        y: Description for y
    """


class Child(Parent):
  def method(self, w, y, z):
    """
    Args:
        z: Description for z
        y: Overridden description for y
    """


# The inherited docstring is
Child.method.__doc__ == """
Args:
    w: Description for w
    y: Overridden description for y
    z: Description for z
"""
```

The description for the argument `y` has been overridden
and the description for the argument `z` has been added.
The only remaining description from the parent is for the argument `w`.

# Advanced usage

## Abstract base class

To create a parent class that is both abstract and has docstring inheritance,
an additional metaclass is required:

```python
import abc
from docstring_inheritance import NumpyDocstringInheritanceMeta


class Meta(abc.ABCMeta, NumpyDocstringInheritanceMeta):
  pass


class Parent(metaclass=Meta):
  pass
```

## Detecting similar docstrings

Duplicated docstrings that could benefit from inheritance can be detected
by setting the environment variable `DOCSTRING_INHERITANCE_SIMILARITY_RATIO` to a value between `0` and `1`.
When set, the docstring sections of a child and its parent are compared and warnings are issued when the docstrings are
similar.
The docstring sections are compared with
[difflib ratio](https://docs.python.org/3/library/difflib.html#difflib.SequenceMatcher.ratio)
from the standard library.
If the ratio is higher or equal to the value of `DOCSTRING_INHERITANCE_SIMILARITY_RATIO`,
the docstring sections are considered similar.
Use a ratio of `1` to detect identical docstring sections.
Use a ratio lower than `1` to detect similar docstring sections.

# Mkdocs

To render the documentation with `mkdocs`,
the package `mkdocstring[python]` is required and
the package `griffe-inherited-docstrings` is recommended,
finally the following shall be added to `mkdocs.yml`:

```yaml
plugins:
- mkdocstrings:
    handlers:
      python:
        options:
          extensions:
            - docstring_inheritance.griffe
            - griffe_inherited_docstrings
```

# Similar projects

[custom_inherit](https://github.com/rsokl/custom_inherit):
`docstring-inherit` started as fork of this project before being re-written,
we thank its author.
