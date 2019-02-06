# Optical Ray-Tracer
Year two computing project at Imperial

![Picture of a lens](./lens.png)

---

## Project goals (taken verbatim from the assignment)

1. design and write an optical ray tracer in Python using object-oriented programming
2. test and verify the operation of the ray-tracer
3. use the ray-tracer to investigate the imaging performance of simple lenses
4. use the ray-tracer to optimise the design of a biconvex lens

## Project Description

`trace` is a Python module which implements a ray-tracer. The user can assemble a scene,
containing different lenses or mirrors, as well as ray sources (rays may also be added
directly). The module was designed to be easy and safe to use.

To accommodate the need for optimizing parameters of lenses (or other geometry objects),
`trace` offers a optimization package, which allows any numeric parameter of a geometry
object to be changed after its creation.

To complement the use of `trace` in interactive sessions, a graphics package (using
[matplotlib][plot]) is also provided. It allows the user to visualize scenes and screens
in 3D or 2D.

## Documentation

The code in this project is fully documented with comments and doc-strings. For a walk-through
of `trace`'s features, see the accompanying [`demo_notebook.ipynb`][demo] [Jupyter notebook][jupyter].
This notebook includes examples of how to work with scenes and how to use the optimization
package.

## Unit Tests

A suite of unit tests is available and can be run with `$ python tests.py`.

## As per request from _'Submission of your code'_ section

> You should also include in the README.txt file a list
> of the files that are submitted.

Here is this list:

- `trace` [directory]
  - `__init__.py`
  - `_unsafe.py`
  - `_utils.py`
  - `geometry.py`
  - `graphics.py`
  - `materials.py`
  - `optim.py`
  - `rays.py`
  - `scene.py`
- `.gitattributes`
- `.gitignore`
- `demo_notebook.ipynb`
- `lens.png`
- `LICENSE`
- `README.md`
- `requirements.txt`
- `tests.py`

[plot]: https://matplotlib.org/
[demo]: ./demo_notebook.ipynb
[jupyter]: https://jupyter.org/
