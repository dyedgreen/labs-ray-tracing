# Optical Ray-Tracer
Year two computing project at Imperial

## Project goals (taken verbatim from the assignment)

1. design and write an optical ray tracer in Python using object-oriented programming
2. test and verify the operation of the ray-tracer
3. use the ray-tracer to investigate the imaging performance of simple lenses
4. use the ray-tracer to optimise the design of a biconvex lens

## Project Description

This project implements a library which allows to construct scenes containing objects
and then let's the user trace rays through the scene.

The supports fully three-dimensional arrangements of lenses, sources and screens. The scenes
can also be rendered in 3D, using matplotlib.

To investigate the behavior of lenses, screens can be added. Screens terminate any rays which
fall onto them and images of the rays which fell onto a screen can be printed.
