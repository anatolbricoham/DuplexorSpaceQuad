# Protocolo de pruebas (NanoVNA o analizador vectorial)

| # | Prueba | Montaje | Criterio de aceptación |
|---|---|---|---|
| 1 | Cortos y continuidad | Polímetro | RADIO–masa: ni corto ni resistencia baja en DC (la rama de 70 cm tiene condensadores en serie). RADIO–2m: continuidad en DC. |
| 2 | Adaptación (S11) | VNA en RADIO; carga de 50 Ω en 2m y en 70cm | < −15 dB entre 144 y 146 MHz y entre 430 y 440 MHz |
| 3 | Rama 2 m (S21) | RADIO → 2m; carga de 50 Ω en 70cm | Pérdida < 0.5 dB a 145 MHz; rechazo > 35 dB a 435 MHz |
| 4 | Rama 70 cm (S21) | RADIO → 70cm; carga de 50 Ω en 2m | Pérdida < 0.7 dB a 435 MHz; rechazo > 35 dB a 145 MHz |
| 5 | Aislamiento | 2m → 70cm; carga de 50 Ω en RADIO | > 35 dB en las dos bandas |
| 6 | Potencia | Radio → diplexor → vatímetro/ROE → carga | Subir 1 → 5 → 10 W: ROE estable y sin calentamiento apreciable |

Recomendaciones:
- Calibra el VNA (SOL + Thru) en el extremo de los cables que vayas a usar.
- Barrido recomendado: de 100 a 500 MHz con 401 puntos o más.
- Si la banda de 70 cm aparece desplazada por los parásitos de la PCB:
  - Si queda baja, reduce C4 un escalón (4.7 → 3.9 pF).
  - Si queda alta, sube L4 y L5 (15 → 18 nH).
- Resultados de la simulación ideal: `make sim`.
