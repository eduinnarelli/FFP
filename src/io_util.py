'''
Projeto Final: Mateurística para o Problema dos Brigadistas.

io_util.py: Arquivo para funções de entrada e saída.

Disciplina:
    MC859/MO824 - Pesquisa Operacional.
Autores:
    Eduardo Barros Innarelli - RA 170161
    Victor Ferreira Ferrari  - RA 187890

Universidade Estadual de Campinas - UNICAMP - 2020

Modificado em: 06/01/2021
'''

from os.path import split, join
import csv

def generate_instance_list(filename):
    f = open(filename)
    l = f.read().splitlines()
    f.close()
    
    l = list(filter(None, l))
    
    for i in range(len(l)):
        split = l[i].split()
        l[i] = join('instances', split[0], split[1])
        
    return l

def print_result(filename, n, best, D, final_time):
    path, filename = split(filename)
    directory = split(path)[1]

    print(f"\"{directory}\",{n},{best.cost},"
          f"\"{filename}\",{D},{final_time:.4f}")

def result_to_dict(filename, n, best, D, final_time):
    path, filename = split(filename)
    directory = split(path)[1]
    
    res = {'set':directory, 'n':n, 'result':best.cost, 
           'instance':filename, 'D':D, 'runtime':round(final_time, 4)}
    
    return res

def dicts_to_csv(dicts, prefix, csv_filename):
    final_csv_name = join('results', 'project', prefix+'-'+csv_filename)
    csvfile = open(final_csv_name, 'w', newline='')
    fieldnames = ['set', 'n', 'result', 'instance', 'D', 'runtime']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    for d in dicts:
        writer.writerow(d)
        
    csvfile.close()
