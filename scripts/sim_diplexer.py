#!/usr/bin/env python3
"""Simulacion nodal (componentes ideales) del diplexor 2m/70cm.

Uso: python3 scripts/sim_diplexer.py            -> tabla con valores del esquema y optimizados
"""
import numpy as np

SCHEM = dict(L1=68e-9, L2=100e-9, L3=68e-9, C1=18e-12, C2=18e-12,
             C3=4.7e-12, C4=2.7e-12, C5=4.7e-12, L4=15e-9, L5=15e-9)
OPTIM = dict(SCHEM, C3=8.2e-12, C4=4.7e-12, C5=8.2e-12)


def sparams(f, v, z0=50.0):
    """Devuelve (S11, S21 radio->2m, S31 radio->70cm, S32 aislamiento) en dB."""
    w = 2 * np.pi * f
    # nodos: 0 radio, 1 n1, 2 n2, 3 salida 2m, 4 n3, 5 n4, 6 salida 70cm
    def solve(src):
        Y = np.zeros((7, 7), complex)
        def add(a, b, y):
            Y[a, a] += y
            if b is not None:
                Y[b, b] += y; Y[a, b] -= y; Y[b, a] -= y
        yl = lambda L: 1 / (1j * w * L); yc = lambda C: 1j * w * C
        add(0, 1, yl(v['L1'])); add(1, None, yc(v['C1'])); add(1, 2, yl(v['L2']))
        add(2, None, yc(v['C2'])); add(2, 3, yl(v['L3']))
        add(0, 4, yc(v['C3'])); add(4, None, yl(v['L4'])); add(4, 5, yc(v['C4']))
        add(5, None, yl(v['L5'])); add(5, 6, yc(v['C5']))
        for n in (0, 3, 6):
            Y[n, n] += 1 / z0
        I = np.zeros(7, complex); I[src] = 2 / z0
        return np.linalg.solve(Y, I)
    db = lambda x: 20 * np.log10(abs(x))
    V = solve(0); V3 = solve(3)
    return db(V[0] - 1), db(V[3]), db(V[6]), db(V3[6])


if __name__ == '__main__':
    for name, v in (('ESQUEMA', SCHEM), ('OPTIMIZADO', OPTIM)):
        print(f'\n{name}')
        print('   MHz     S11    ->2m   ->70cm   2m<->70cm (dB)')
        for f in (144, 146, 290, 430, 435, 440, 870):
            print('  %5d  %6.1f  %6.1f  %6.1f  %6.1f' % ((f,) + sparams(f * 1e6, v)))
