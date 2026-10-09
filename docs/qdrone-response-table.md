# QDrone2 response table

Generated from [results.json](../Data/qdrone-response/results.json).
[Download CSV](qdrone-response.csv) for stored precision; display rounding is not measurement uncertainty.
Rows follow command time. Missing metrics mean an incomplete window, never zero.

| Step | Direction | Time [s] | Precommand [V] | Bias [m] | MAE [m] | RMSE [m] | Window |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | :--- |
| 1 | Up | 4.418 | 15.518 | -0.2782 | 0.3024 | 0.4910 | Complete |
| 2 | Down | 11.415 | 15.474 | 0.3050 | 0.3124 | 0.5022 | Complete |
| 3 | Up | 18.420 | 15.447 | -0.2863 | 0.3054 | 0.4938 | Complete |
| 4 | Down | 25.420 | 15.412 | 0.3259 | 0.3264 | 0.5074 | Complete |
| 5 | Up | 32.418 | 15.314 | -0.2916 | 0.3023 | 0.4959 | Complete |
| 6 | Down | 39.418 | 15.358 | 0.3013 | 0.3074 | 0.5046 | Complete |
| 7 | Up | 46.418 | 15.270 | -0.2783 | 0.3032 | 0.4937 | Complete |
| 8 | Down | 53.433 | 15.279 | 0.3029 | 0.3120 | 0.5027 | Complete |
| 9 | Up | 60.418 | 15.261 | -0.2894 | 0.3030 | 0.4932 | Complete |
| 10 | Down | 67.425 | 15.225 | 0.3050 | 0.3125 | 0.5067 | Complete |
| 11 | Up | 74.418 | 15.163 | -0.2820 | 0.3032 | 0.4928 | Complete |
| 12 | Down | 81.422 | 15.119 | 0.3096 | 0.3203 | 0.5129 | Complete |
| 13 | Up | 88.420 | 15.048 | -0.2940 | 0.3025 | 0.4942 | Complete |
| 14 | Down | 95.417 | 15.039 | 0.2996 | 0.3079 | 0.5017 | Complete |
| 15 | Up | 102.417 | 15.022 | -0.2794 | 0.3054 | 0.4955 | Complete |
| 16 | Down | 109.423 | 14.915 | 0.3029 | 0.3102 | 0.5072 | Complete |
| 17 | Up | 116.415 | 14.853 | -0.2789 | 0.3020 | 0.4924 | Complete |
| 18 | Down | 123.417 | 14.924 | 0.3038 | 0.3140 | 0.5092 | Complete |
| 19 | Up | 130.417 | 14.889 | -0.2938 | 0.3061 | 0.4977 | Complete |
| 20 | Down | 137.423 | 14.889 | 0.3032 | 0.3180 | 0.5080 | Complete |
| 21 | Up | 144.417 | 14.844 | N/A | N/A | N/A | Incomplete: recording ended |

Original MPC; one development discharge. Repeated steps do not identify independent packs.
Observations: Borbolla-Burillo et al., [Zenodo 19464105](https://doi.org/10.5281/zenodo.19464105), CC BY 4.0.
Table derived here. [Method and limits](qdrone-response.md).
