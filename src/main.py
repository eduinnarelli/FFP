'''
Projeto Final: Mateurística para o Problema dos Brigadistas.

main.py: Arquivo para execução dos testes.

Disciplina:
    MC859/MO824 - Pesquisa Operacional.
Autores:
    Eduardo Barros Innarelli - RA 170161
    Victor Ferreira Ferrari  - RA 187890

Universidade Estadual de Campinas - UNICAMP - 2020

Modificado em: 09/01/2021
'''

from argparse import ArgumentParser
from os.path import exists
from random import seed
from time import time
from sys import exit

from FFP import FFP
from Solution import Solution
from f_desc import num_of_descendants
from io_util import (generate_instance_list, print_result, dicts_to_csv,
                     result_to_dict, result_to_visualizer)

from NatGRASP import NatGRASP
from FFM import ffm
from M_FFM import m_ffm


def main():
    methods = {'grasp': GRASP, 'ffm': FFM, 'mffm': M_FFM}

    # Ler argumentos da linha de comando
    parser = ArgumentParser(add_help=True)
    parser.add_argument('method')
    parser.add_argument('--input-file', required=True)
    parser.add_argument('--out-file', required=False)
    parser.add_argument('--D', nargs='+', type=int,
                        required=False, default=[2])
                        
    exclusive = parser.add_mutually_exclusive_group(required=False)
    exclusive.add_argument('--instance-list', action='store_true')
    exclusive.add_argument('--visualizer', action='store_true')
    
    args = parser.parse_args()

    # Verificar arquivo de entrada
    if not exists(args.input_file):
        print("File does not exist! Try again.")
        exit(0)

    # Lista de métodos
    if args.method == 'all':
        mets = methods.values()
    elif args.method == 'ilp':
        mets = [FFM, M_FFM]
    elif args.method.lower() not in methods.keys():
        print("Method does not exist! Available: 'grasp', 'ffm, 'mffm',"
              " 'ilp','all'")
        exit(0)
    else:
        mets = [methods[args.method]]

    # Criar lista de instâncias
    if args.instance_list:
        filenames = generate_instance_list(args.input_file)
    else:
        filenames = [args.input_file]

    # Executar para CSV se nome do arquivo de saida for passado.
    # Senão, executar com saída para stdout.
    if args.visualizer:
        run_to_visualizer(filenames, args.D, mets)
    elif args.out_file:
        run_to_csv(filenames, args.D, mets, args.out_file)
    else:
        run_and_print(filenames, args.D, mets)


def run_to_csv(filenames : list, D_list : list, methods : list, 
               out_file : str):

    # Instanciar problema
    seed_number = 1337

    # Executar cada método.
    for run in methods:
        ffp = FFP(5)
        results = []
        prefix = run.__name__
        inst = 0

        # Executar para cada arquivo.
        for f in filenames:
            inst += 1
            d_index = 0
            for D in D_list:
                d_index += 1
                print(f"Method {prefix}: {inst}/{len(filenames)}, "
                      f"{d_index}/{len(D_list)} runs", end='\r')
                ffp.D = D
                ffp.read_input(f)
                best, final_time = run(ffp, seed_number)

                # Filtrar resultado
                results.append(result_to_dict(f, ffp.G.number_of_nodes(),
                                              best, D, final_time))
        dicts_to_csv(results, prefix, out_file)
        print()


def run_and_print(filenames : list, D_list : list, methods : list):

    # Instanciar problema
    seed_number = 1337

    # Executar cada método.
    for run in methods:
        ffp = FFP(5)
        print(f"Method: {run.__name__}. Instances: {len(filenames)}. "
              f"Runs: {len(D_list)}.")

        # Executar para cada arquivo
        for f in filenames:
            for D in D_list:
                ffp.D = D
                ffp.read_input(f)

                best, final_time = run(ffp, seed_number)

                # Imprimir resultado
                print_result(f, ffp.G.number_of_nodes(),
                             best, D, final_time)

def run_to_visualizer(filenames : list, D : list, method : list):
    
    # Instanciar problema
    seed_number = 1337

    # Executar.
    ffp = FFP(D[0])
    ffp.read_input(filenames[0])

    best, _ = method[0](ffp, seed_number)

    # Imprimir resultado
    result_to_visualizer(filenames[0], ffp, best)

def GRASP(ffp : FFP, seed_number : int):

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


def FFM(ffp : FFP, *_):
    m = ffm(ffp.G, ffp.B, ffp.D, ffp.max_T, ffp.G.number_of_nodes() / 2)
    m.optimize()

    if m.SolCount > 0:
        sol = Solution.vars_to_solution(m, ffp.G, ffp.max_T)
    else:
        sol = Solution(set(), set(), [], ffp.max_T)

    return sol, m.Runtime


def M_FFM(ffp : FFP, *_):
    m = m_ffm(ffp.G, ffp.sp_len, ffp.B, ffp.D,
              ffp.max_T, ffp.G.number_of_nodes() / 2)
    m.optimize()

    if m.SolCount > 0:
        sol = Solution.vars_to_solution(m, ffp.G, ffp.max_T)
    else:
        sol = Solution(set(), set(), [], ffp.max_T)

    return sol, m.Runtime


if __name__ == "__main__":
    main()
