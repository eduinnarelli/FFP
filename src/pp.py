'''
Projeto Final: Mateurística para o Problema dos Brigadistas.

pp.py: Script para gerar perfis de desempenho.

Disciplina:
    MC859/MO824 - Pesquisa Operacional.
Autores:
    Guilherme de Oliveira Macedo        (Tradução do MATLAB)
    Victor Ferreira Ferrari - RA 187890 (configuração/leitura da entrada)

Universidade Estadual de Campinas - UNICAMP - 2020

Modificado em: 08/01/2021
'''

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy
import pandas
import seaborn as sn
from sys import argv, exit
from os.path import exists, splitext

logplot = True

# Entrada
if len(argv) < 2:
    print("Usage: pp.py FILE")
    exit(0)

filename = argv[1]

if not exists(filename):
    print("File does not exist!")
    exit(0)

# Ler CSV
T = pandas.read_csv(filename)
np = len(T)
ns = len(T.columns)

# Minimal performance per solver.
minperf = numpy.zeros(np)

for k in range(np):
    minperf[k] = min(T.to_numpy()[k])

# Compute ratios and divide by smallest element in each row.
r = numpy.zeros((np, ns))

for k in range(np):
    r[k, :] = T.to_numpy()[k, :] / minperf[k]

if logplot:
    r = numpy.log2(r)

max_ratio = r.max()

for k in range(ns):
    r[:, k] = numpy.sort(r[ :, k])


# Plot stair graphs with markers.

n = []

for k in range(1, np + 1):
    n.append(k / np)

plt.figure(figsize = (8, 5))
plt.plot(r[:, 0], n, color = '#3CB371', linewidth = 1, label = 'GRASP')
plt.plot(r[:, 1], n, color = '#FFD700', linewidth = 1, label = 'FFM')
plt.plot(r[:, 2], n, color = '#4B0082', linewidth = 1, label = 'M-FFM')
plt.plot(r[:, 3], n, color = '#FF6347', linewidth = 1, label = 'REF')
plt.ylabel('Probabilidade (%)')
plt.xlabel('$log_2(r)$')
sn.despine(left = True, bottom = True)
plt.grid(True, axis = 'x')
plt.grid(True, axis = 'y')
plt.legend()
plt.savefig(splitext(filename)[0] + '.eps', dpi = 1500, transparent = True, bbox_inches = 'tight')
plt.show()
