'''
Projeto Final: Mateurística para o Problema dos Brigadistas.

main.py: Arquivo para execução dos testes da mateurística.

Disciplina:
    MC859/MO824 - Pesquisa Operacional.
Autores:
    Eduardo Barros Innarelli - RA 170161
    Victor Ferreira Ferrari  - RA 187890

Universidade Estadual de Campinas - UNICAMP - 2020

Modificado em: 06/01/2021
'''

from argparse import ArgumentParser
from os.path import exists, split, join
from random import seed
from time import time
from sys import exit
import csv

from FFP import FFP
from NatGRASP import NatGRASP
from f_desc import num_of_descendants

def main():
    # Ler argumentos da linha de comando
    parser = ArgumentParser(add_help=True)
    parser.add_argument('--input-file', required=True)
    parser.add_argument('--instance-list', action='store_true')
    parser.add_argument('--out-file', required=False)
    parser.add_argument('--D', nargs='+', type=int, required=False)
    args = parser.parse_args()
    
    if not exists(args.input_file):
        print("File does not exist! Try again.")
        exit(0)
        
    # Criar lista de instâncias
    if args.instance_list:
        filenames = generate_instance_list(args.input_file)
    else:
        filenames= [args.input_file]
    
    # Executar para CSV se nome do arquivo de saida for passado.
    # Senão, executar com saída para stdout.    
    if args.out_file:
        run_to_csv(filenames, args.D, args.out_file)
    else:
        run_and_print(filenames, D_range)

def generate_instance_list(filename):
    f = open(filename)
    l = f.read().splitlines()
    f.close()
    
    l = list(filter(None, l))
    
    for i in range(len(l)):
        split = l[i].split()
        l[i] = join('instances', split[0], split[1])
        
    return l

def run_to_csv(filenames, D_range, out_file):
    # Instanciar problema
    ffp = FFP(5)
    seed_number = 1337
    results = []
    
    # Executar para cada arquivo.
    for f in filenames:
        for D in D_range:
            ffp.D = D
            best, final_time = run(f, seed_number, ffp)

            # Filtrar resultado
            results.append(result_to_dict(f, ffp.G.number_of_nodes(),
                                          best, D, final_time))
    dicts_to_csv(results, out_file)

def run_and_print(filenames, D_range):
    # Instanciar problema
    ffp = FFP(5)
    seed_number = 1337
    
    # Executar para cada arquivo
    for f in filenames:
        for D in D_range:
            ffp.D = D
            best, final_time = run(f, seed_number, ffp)

            # Imprimir resultado
            print_result(f, ffp.G.number_of_nodes(),
                         best, D, final_time)

def run(filename, seed_number, ffp):

    # Ler instância
    ffp.read_input(filename)

    # Parâmetros
    k = 2
    f = num_of_descendants
    eps = 0.5
    limit = ffp.G.number_of_nodes() / 2
    alpha = 0.3
    eta = 11000
    rho = 4

    # Instanciar mateurística
    seed(seed_number)
    start_time = time()
    method = NatGRASP(ffp, k, f, eps, limit, start_time)

    # PASSO 1: Construção
    S = set()

    # Critério de parada 1: eta iterações
    for _ in range(eta):

        # Critério de parada 2: metade do limite de tempo alcançado
        if time() - method.start_time >= method.limit / 2:
            break

        curr = method.constructive_heuristic_th(alpha)
        S.add(curr)

    # PASSO 2: Seleção
    P, best = method.pool_selection(S, rho)

    # PASSO 3: Busca Local
    best = method.adaptive_local_search(ffp, P, best, time()-start_time)

    return best, time()-start_time    

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

def dicts_to_csv(dicts, csv_filename):
    final_csv_name = join('results', 'project', csv_filename)
    csvfile = open(final_csv_name, 'w', newline='')
    fieldnames = ['set', 'n', 'result', 'instance', 'D', 'runtime']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    for d in dicts:
        writer.writerow(d)
        
    csvfile.close()

if __name__ == "__main__":
    main()
