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
from os.path import exists, split
from random import seed
from time import time

from FFP import FFP
from NatGRASP import NatGRASP
from f_desc import num_of_descendants

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
    parser.add_argument('--input-file', type=str, required=True)
    args = parser.parse_args()
    
    if not exists(args.input_file):
        print("Instance does not exist! Try again.")
    
    # Instanciar problema
    seed_number = 1337
    ffp = FFP(5)
    
    for D in range(1,11):
        ffp.D = D
        best, final_time = run(args.input_file, seed_number, ffp)
        
        # Imprimir resultado
        print_result(args.input_file, ffp.G.number_of_nodes(), 
                     best, D, final_time)
