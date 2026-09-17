"""Exact 2019 SI defining constants.

Physics
-------
Since the 2019 redefinition the values of c, h, and k_B are exact by definition, so tests
compare them with ``==`` rather than with a tolerance [codata2018] [bipm2019].
"""
C_LIGHT: float = 299_792_458.0          # m/s, exact [bipm2019]
H_PLANCK: float = 6.626_070_15e-34      # J s, exact [bipm2019]
HBAR: float = H_PLANCK / (2.0 * 3.141592653589793)
K_BOLTZMANN: float = 1.380_649e-23      # J/K, exact [bipm2019]
