<!--
 Copyright 2021 Antoine DECHAUME

 This work is licensed under the Creative Commons Attribution 4.0
 International License. To view a copy of this license, visit
 http://creativecommons.org/licenses/by/4.0/ or send a letter to Creative
 Commons, PO Box 1866, Mountain View, CA 94042, USA.
 -->

# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0rc0] - 2023-06
### Changed
- Docstring inheritance for methods only inherit from the first found parent.
### Fixed
- Docstring inheritance for methods with no argument descriptions.
- Format of the arguments provided with the default description for the Numpy style.

## [1.1.1] - 2023-01
### Fixed
- Docstring inheritance for methods with multiple parents.

## [1.1.0] - 2023-01
### Added
- Support class docstrings with `__init__` signature description.
### Changed
- Some performance improvements.
### Fixed
- Metaclasses API no longer leaks into the classes they create.

## [1.0.1] - 2022-11
### Added
- Support for Python 3.11.

## [1.0.0] - 2021-11
### Changed
- Metaclasses naming.
### Fixed
- Handling of *object* in the class hierarchy.
- Rendering of Google docstrings with no summaries.
- Formatting of items without descriptions.
- Inheritance of a metaclass'd class from its grandparents.

## [0.1] - 2021-11
### Added
- Initial release.
