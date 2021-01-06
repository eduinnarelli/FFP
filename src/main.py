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

from FFP import FFP
from NatGRASP import NatGRASP
from f_desc import num_of_descendants

def generate_instance_list(filename):
    f = open(filename)
    l = f.read().splitlines()
    f.close()
    
    l = list(filter(None, l))
    
    for i in range(len(l)):
        split = l[i].split()
        l[i] = join('instances',split[0],split[1])
        
    return l


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

if __name__ == "__main__":

    # Ler argumentos da linha de comando
    parser = ArgumentParser(add_help=False)
    parser.add_argument('--input-file', required=True)
    parser.add_argument('--instance-list', action='store_true')
    args = parser.parse_args()

    if not exists(args.input_file):
        print("File does not exist! Try again.")
        exit(0)
        
    # Criar lista de instâncias
    if args.instance_list:
        filenames = generate_instance_list(args.input_file)
    else:
        filenames= [args.input_file]
    
    # Instanciar problema
    seed_number = 1337
    ffp = FFP(5)

    for f in filenames:
        for D in range(1, 11):
            ffp.D = D
            best, final_time = run(f, seed_number, ffp)

            # Imprimir resultado
            print_result(f, ffp.G.number_of_nodes(),
                         best, D, final_time)
