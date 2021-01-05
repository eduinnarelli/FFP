'''
Projeto Final: Mateurística para o Problema dos Brigadistas.

FFM.py: Modelo linear inteiro para o problema dos brigadistas.

Disciplina:
    MC859/MO824 - Pesquisa Operacional.
Autores:
    Eduardo Barros Innarelli - RA 170161
    Victor Ferreira Ferrari  - RA 187890

Universidade Estadual de Campinas - UNICAMP - 2020

Modificado em: 04/01/2021
'''

import gurobipy as gp
import networkx as nx

from argparse import ArgumentParser
from gurobipy import GRB
from FFP import FFP
from Solution import Solution


def ffm(G: nx.Graph, B: list, D: int, T: int, time: float):
    '''
    Firefighter Model (FFM) - modelo de programação linear inteira
    que resolve o FFP de forma exata.

        Args:
            G (networkx.Graph): o grafo de entrada.
            B (list): vértices inicialmente queimados.
            D (int): número de bombeiros disponíveis.
            T (int): limite de iterações.
    '''

    # Conjunto e número de vértices
    V = G.nodes
    n = G.number_of_nodes()

    # Inicializar modelo
    model = gp.Model('ffm')
    model.setParam('TimeLimit', time)

    # Variáveis binárias:
    # - b[v, t]: indica se o vértice v está queimado (1) ou não (0) no inst. t
    b = model.addVars(n, T+1, vtype=GRB.BINARY, name="b")
    # - d[v, t]: indica se o vértice v está salvo (1) ou não (0) no instante t
    d = model.addVars(n, T+1, vtype=GRB.BINARY, name="d")

    # Objetivo: maximizar quantidade de vértices salvos no instante T
    model.setObjective(n - gp.quicksum(b[v, T] for v in V), GRB.MAXIMIZE)

    # Restrições:

    # - cada vizinho v_n de um vértice v queimado na iteração t-1 deve ser ou
    #   queimado ou defendido na iteração t;
    model.addConstrs((
        b[v, t] + d[v, t] - b[v_n, t-1] >= 0
        for v in V
        for v_n in G.adj[v]
        for t in range(1, T+1)
    ))

    # - um vértice v não é queimado e defendido no instante t;
    model.addConstrs((
        b[v, t] + d[v, t] <= 1 for v in V for t in range(1, T+1)
    ))

    # - um vértice queimado ou protegido permanece nesse estado nas iterações
    #   seguintes;
    model.addConstrs((
        b[v, t] - b[v, t-1] >= 0 for v in V for t in range(1, T+1)
    ))
    model.addConstrs((
        d[v, t] - d[v, t-1] >= 0 for v in V for t in range(1, T+1)
    ))

    # - limite de vértices defendidos por iteração;
    model.addConstrs((gp.quicksum(d[v, t] - d[v, t-1]
                                  for v in V) <= D for t in range(1, T+1)))

    # - inicializar variáveis no instante 0 (vértices de B queimados e nenhum
    #   defendido);
    model.addConstrs((b[v, 0] == 1 for v in B))
    model.addConstrs((b[v, 0] == 0 for v in set(V).difference(set(B))))
    model.addConstrs((d[v, 0] == 0 for v in V))

    # Colocando variáveis no modelo.
    model._b = b
    model._d = d

    # Retornar modelo
    return model


if __name__ == '__main__':

    # Argumentos da linha de comando
    parser = ArgumentParser(add_help=False)
    parser.add_argument('--input-file', type=str, required=True)
    parser.add_argument('--D', type=int, required=True)
    args = parser.parse_args()

    ffp = FFP(args.D)
    ffp.read_input(args.input_file)

    # Executar M-FFM
    m = ffm(ffp.G, ffp.B, ffp.D, ffp.max_T, 1800)
    m.optimize()
    sol = Solution.vars_to_solution(m, ffp.G, ffp.max_T)
    print(sol)
