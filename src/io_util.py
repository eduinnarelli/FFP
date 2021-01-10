'''
Projeto Final: Mateurística para o Problema dos Brigadistas.

io_util.py: Arquivo para funções de entrada e saída.

Disciplina:
    MC859/MO824 - Pesquisa Operacional.
Autores:
    Eduardo Barros Innarelli - RA 170161
    Victor Ferreira Ferrari  - RA 187890

Universidade Estadual de Campinas - UNICAMP - 2020

Modificado em: 09/01/2021
'''

from Solution import Solution
from FFP import FFP

from os.path import split, join, basename, splitext
import csv

def generate_instance_list(filename: str):
    f = open(filename)
    l = f.read().splitlines()
    f.close()
    
    l = list(filter(None, l))
    
    for i in range(len(l)):
        split = l[i].split()
        l[i] = join('instances', split[0], split[1])
        
    return l

def print_result(filename : str, n : int, best : Solution, D : int, 
                 final_time : float):
    path, filename = split(filename)
    directory = split(path)[1]

    print(f"\"{directory}\",{n},{best.cost},"
          f"\"{filename}\",{D},{final_time:.4f}")

def result_to_dict(filename : str, n : int, best : Solution, D : int, 
                   final_time : float):
    path, filename = split(filename)
    directory = split(path)[1]
    
    res = {'set':directory, 'n':n, 'result':best.cost, 
           'instance':filename, 'D':D, 'runtime':round(final_time, 4)}
    
    return res

def dicts_to_csv(dicts : list, prefix : str, csv_filename : str):
    final_csv_name = join('results', 'project', prefix+'-'+csv_filename)
    csvfile = open(final_csv_name, 'w', newline='')
    fieldnames = ['set', 'n', 'result', 'instance', 'D', 'runtime']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    for d in dicts:
        writer.writerow(d)
        
    csvfile.close()

def result_to_visualizer(filename : str, ffp : FFP, sol : Solution):
    res_file = splitext(basename(filename))[0]
    res_file = join('results', 'visualizer', res_file + '.vis')
    with open(res_file, 'w') as f:
        
        # Problem parameters
        f.write(str(ffp.G.number_of_nodes()) + '\n')
        f.write(str(ffp.G.number_of_edges()) + '\n')
        f.write(str(len(ffp.B)) + '\n')
        f.write(' '.join(str(i) for i in ffp.B) + '\n')
        
        for e in ffp.G.edges:
            f.write(str(e[0]) + ' ' + str(e[1]) + '\n')
        
        # Solution parameters
        defended, burned = sol.full_solution()
        f.write(str(len(defended)) + '\n')
        for i in defended:
            f.write(str(i[0]) + ' ' + str(i[1]) + '\n')
        
        f.write(str(len(burned)) + '\n')
        for i in burned:
            f.write(str(i[0]) + ' ' + str(i[1]) + '\n')
    
    return 
