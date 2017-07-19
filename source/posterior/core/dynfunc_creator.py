#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
Gravitational group (gravgroup) module.

The objective of this module is to define the GravGroup, Star and Planet class.
A GravGroup intance is a group of gravitationnaly bond objects (stars or planets).
It could be:
- a stellar planetary system (one star, and one or several planets),
- a binary system (two star, no planets),
- a herarchical triple system (two stars, one planet orbiting around one of the stars)
- a circum binary system (a planet orbiting, a binary star)
- any combinaison of stars and planets (for now I think it should contain at least two objects
  including at least a star so that it produces a variable signal in RV and or LC)

@TODO:
    - Move the part of load_parameter_file that update one parameter value to parameter.py
    - Log info the creation of stars and planets in a model
    - Deal with fitting transit times individually
    - Deal with limb darkening coefficients parametrisation
    - Redefine the get_list_main_params routine in gravgroup so that it give the parametrisation of
      the planets and stars inside it.
    - Implement subgravgroups in GravGroup
    - Transform the attributes transit_model, rv_model and ld_model into set and get properties
"""
