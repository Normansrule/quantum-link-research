# Turbulence and Adaptive Optics

## Definitions
- **Refractive-index structure constant** $C_n^2$ (m$^{-2/3}$): strength of turbulence versus altitude; the Hufnagel–Valley 5/7 profile is the standard model [andrews2005].
- **Fried parameter** $r_0=\big[0.423k^2\sec\zeta\int C_n^2\,dh\big]^{-3/5}$: the aperture beyond which turbulence, not diffraction, limits resolution; 5–20 cm at 500 nm at good sites, scaling as $\lambda^{6/5}$.
- **Rytov variance** $\sigma_R^2=2.25k^{7/6}\sec^{11/6}\zeta\int C_n^2(h)h^{5/6}dh$: weak turbulence for $\sigma_R^2<1$ (downlinks), strong for uplinks.
- **Scintillation index** $\sigma_I^2\approx e^{\sigma_R^2}-1$, reduced by a large receiver (aperture averaging).
- **Beam wander**: random tilt of an uplink beam from turbulence near the transmitter; the reason quantum links are downlinks.

## Why downlinks
A downlink meets the turbulence only in the last 20 km of a 500–2000 km path, when the beam is already metres wide, so the phase screen tilts and speckles it mildly (weak turbulence, $\sigma_R^2\sim0.1$ at zenith, 810 nm). An uplink meets the same screen at the start, where a 10 cm beam is deflected by microradians and then diverges over the whole path: microradians times 1 000 km is metres of miss. Micius and Jinan-1 therefore both send photons downward [bourgoin2013] [li2025jinan].

## Adaptive optics for quantum links
A single-photon signal is too weak to sense the wavefront, so the correction uses a bright beacon (a laser from the other terminal) at a different wavelength, measured by a Shack–Hartmann sensor and corrected by a fast-steering mirror (tip–tilt) and a deformable mirror (higher orders). For a downlink, tip–tilt alone recovers most of the coupling into a single-mode fiber; full AO matters when the receiver couples into fiber for a detector at 1550 nm or a memory. The numbers in this repository (`qll/channels/atmosphere.py`) give $r_0$, $\sigma_R^2$, and aperture averaging from the HV-5/7 profile; site-specific $C_n^2$ replaces the profile when measured (P04 measures the daytime scintillation on the rooftop as a proxy).

## Key papers
- Andrews, L. C., & Phillips, R. L. (2005). *Laser Beam Propagation through Random Media* (2nd ed.). SPIE Press. https://doi.org/10.1117/3.626196
- Fried, D. L. (1966). Optical resolution through a randomly inhomogeneous medium for very long and very short exposures. *Journal of the Optical Society of America*, 56, 1372. https://doi.org/10.1364/JOSA.56.001372
- Bourgoin, J.-P., et al. (2013). *New Journal of Physics*, 15, 023006. https://doi.org/10.1088/1367-2630/15/2/023006
- Gruneisen, M. T., et al. (2021). Adaptive-optics-enabled quantum communication: a technique for daytime space-to-Earth links. *Physical Review Applied*, 16, 014067. https://doi.org/10.1103/PhysRevApplied.16.014067

## In this repo
`qll/channels/atmosphere.py` (profile, $r_0$, Rytov, scintillation, aperture averaging, beam wander); P04; F2 stage S3.

## Exercises
1. Compute $r_0$ at 810 nm and 1550 nm at zenith and at 60° from zenith; which changes more, wavelength or angle?
2. Why does a 1 m receiver see a third of the scintillation of a 5 cm one at 1 000 km?
