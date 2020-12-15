'''
Projeto Final: Mateurística para o Problema dos Brigadistas.

M-FFM.py: Modelo linear inteiro relaxado para o problema dos brigadistas.

Disciplina:
    MC859/MO824 - Pesquisa Operacional.
Autores:
    Eduardo Barros Innarelli - RA 170161
    Victor Ferreira Ferrari  - RA 187890

Universidade Estadual de Campinas - UNICAMP - 2020

Modificado em: 15/12/2020
'''

'''
Nesse módulo constam uma função que modela e resolve o FFP e um script que
chama a função.
'''
import gurobipy as gp
import networkx as nx

from argparse import ArgumentParser
from gurobipy import GRB
from FFP import FFP
from Solution import Solution
from math import inf

def m_ffm(G: nx.Graph, B: list, D: int, T: int):
    '''
    Modified Firefighter Model (M-FFM) - modelo de programação linear inteira
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

    # Inicializar ambiente
    env = gp.Env(empty=True)
    env.setParam('TimeLimit', 1800)
    env.start()

    # Inicializar modelo
    model = gp.Model('ffm', env=env)

    # Variáveis binárias:
    # - b[v, t]: indica se o vértice v está queimado (1) ou não (0) no inst. t
    b = model.addVars(n, T, vtype=GRB.BINARY, name="b")
    # - d[v, t]: indica se o vértice v está salvo (1) ou não (0) no instante t
    d = model.addVars(n, T, vtype=GRB.BINARY, name="d")

    # Objetivo: minimizar quantidade de vértices queimados no instante T
    model.setObjective(gp.quicksum(b[v, T-1] for v in V))

    # Restrições:

    # - cada vizinho v_n de um vértice v queimado na iteração t-1 deve ser ou
    #   queimado ou defendido na iteração t;
    model.addConstrs((
        b[v, t] + d[v, t] - b[v_n, t-1] >= 0
        for v in V
        for v_n in G.adj[v]
        for t in range(1, T)
    ))

    # - um vértice v não é queimado e defendido no instante t;
    model.addConstrs((
        b[v, t] + d[v, t] <= 1 for v in V for t in range(1, T)
    ))

    # - um vértice queimado ou protegido permanece nesse estado nas iterações
    #   seguintes;
    model.addConstrs((
        b[v, t] - b[v, t-1] >= 0 for v in V for t in range(1, T)
    ))
    model.addConstrs((
        d[v, t] - d[v, t-1] >= 0 for v in V for t in range(1, T)
    ))

    # - limitar o número de vértices defendidos em t por t*D. Essa restrição é
    #   relaxada da original e permite a alocação de bombeiros adicionais, mas
    #   isso não impacta no custo e é possível viabilizar a solução em tempo
    #   polinomial;
    model.addConstrs((d.sum('*', t) <= t*D for t in range(1, T)))

    # - inicializar variáveis no instante 0 (vértices de B queimados e nenhum
    #   defendido);
    model.addConstrs((b[v, 0] == 1 for v in B))
    model.addConstrs((b[v, 0] == 0 for v in set(V).difference(set(B))))
    model.addConstrs((d[v, 0] == 0 for v in V))

    # - um vértice v só pode ser queimado a partir do instante t >= d(v, B),
    #   onde d(v, B) representa o menor caminho entre v e o conjunto B.
    model.addConstrs((
        b[v, t] == 0
        for v in set(V).difference(set(B))
        for t in range(1, min([nx.shortest_path_length(G, v, b) for b in B]))
    ))

    # Retornar modelo
    return model


def vars_to_solution(model, problem):
    b = model.getVarByName("b")
    d = model.getVarByName("d")

    defended = set()
    burned = set()
    
    n = self.G.number_of_nodes()
    iteration = [inf for i in range(n)]
    
    # Converter variáveis para conjuntos/listas
    for v in range(n):
        for t in range(T):
            
            # Quando um nó é queimado ou defendido,
            # guarda a iteração e vai para o próximo.
            if b[v,t] == 1: 
                burned.add(v)
                iteration[v] = t
                break
            elif d[v,t] == 1:
                defended.add(v)
                iteration[v] = t
                break
    
    return Solution(defended, burned, iteration, model.cost)
    

if __name__ == '__main__':

    # Argumentos da linha de comando
    parser = ArgumentParser(add_help=False)
    parser.add_argument('--input-file', type=str, required=True)
    parser.add_argument('--D', type=int, required=True)
    args = parser.parse_args()

    ffp = FFP(args.D)
    ffp.read_input(args.input_file)
    print(ffp)

    # Executar M-FFM
    m = m_ffm(ffp.G, ffp.B, ffp.D, ffp.T)
    #m.optimize()
    sol = vars_to_solution(m, ffp)
    print(sol)
