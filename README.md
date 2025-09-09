# Data-mapping for IMAS

In this project we will keep track of the latest status, updates and issues on the mapping of various experiments 
to the [IMAS-Data-Dictionary](https://github.com/iterorganization/IMAS-Data-Dictionary) convention.

Whenever possible, we will also try to share pointers to open-accessible dataset examples, to allow code testing for various tokamak configurations. 

You can find some additional resources and information on our regular online discussion meetings in the [wiki](https://github.com/iterorganization/IMAS-Data-Mapping/wiki).

If you want to update the information for a given experiment or if you find issues in the mapped data, please 
first take look at the [contribution guidelines](CONTRIBUTING.md).




## Tokamak data mapping status :construction:

| Experiment | Contact person | Mapping information | List of mapped IDSs |
|:----------:|:--------------:|:--------------------|:--------------------|
| AUG | [@DavidPCoster](https://github.com/DavidPCoster) | from `trview` and `readaug` | `core_profiles`, `dataset_description`, `equilibrium`, `ic_antennas`, `magnetics`, `nbi`, `pf_active`, `pulse_schedule`, `summary`, `tf`, `wall` |
| DIII-D | [@AreWeDreaming](https://github.com/AreWeDreaming) | with [OMAS](https://github.com/gafusion/omas) | `bolometer`, `charge_exchange`, `coils_non_axisymmetric`, `core_profiles`, `dataset_description`, `ec_launchers`, `ece`, `em_coupling`, `equilibrium`, `gas_injection`, `interferometer`, `langmuir_probes`, `magnetics`, `mse`, `nbi`, `neutron_diagnostics`, `pf_active`, `summary`, `thomson_scattering`, `tf`, `wall` |
| EAST | [@simpla-fusion](https://github.com/simpla-fusion) | with [FyTok](https://github.com/fusion-yun/fytok) |`core_profiles`,  `equilibrium`, `magnetics`,  `pf_active`,  `tf`, `wall` |
| ITER | [@MasanariHosokawa](https://github.com/MasanariHosokawa) | only machine description (e.g. [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15525525.svg)](https://doi.org/10.5281/zenodo.15525525)) | `bolometer`, `camera_visible`, `coils_non_axisymmetric`, `ec_launcher`, `ece`, `ic_antennas`, `interferometer`, `magnetics`, `nbi`, `neutron_diagnostic`, `pf_active`, `pf_passive`, `polarimeter`, `refractometer`, `spectrometer_visible`, `spectrometer_x_ray_crystal`, `soft_x_rays`, `tf`, `thomson_scattering`, `wall` |
| TT-1 | [@ApiwatWis](https://github.com/ApiwatWis) | manual mapping | `magnetics`, `pf_active`, `pf_passive`, `tf`, `wall`, `interferometer`, `camera_visible`, `gas_pumping`, `langmuir_probes`|
| WEST | [@JorgeAMorales](https://github.com/JorgeAMorales) | with [`UDA`](https://github.com/ukaea/UDA) and WEST plasma reconstruction chain | `bolometer`, `bremsstrahlung_visible`, `camera_ir`, `camera_x_rays`, `calorimetry`, `core_profiles`, `ece`, `equilibrium`, `gas_injection`, `hard_x_rays`, `ic_antennas`, `interferometer`, `langmuir_probes`, `lh_antennas`, `magnetics`, `neutron_diagnostic`, `pf_active`, `pf_passive`, `polarimeter`, `pulse_schedule`, `reflectometer_profile`, `soft_x_rays`, `spectrometer_visible`, `spectrometer_x_ray_crystal`, `summary`, `tf`, `wall` |

