'''
Projeto Final: Mateurística para o Problema dos Brigadistas.

Solution.py: Classe para solução do problema dos brigadistas.

Disciplina:
    MC859/MO824 - Pesquisa Operacional.
Autores:
    Eduardo Barros Innarelli - RA 170161
    Victor Ferreira Ferrari  - RA 187890

Universidade Estadual de Campinas - UNICAMP - 2020

Modificado em: 31/12/2020
'''

from networkx import Graph, single_source_shortest_path
from math import ceil, inf
from types import FunctionType
from gurobipy import Model, GRB


class Solution(object):
    def __init__(self, defended: set, burned: set, iterations: list,
                 T: int, cost: int = 0, optimal: bool = True):
        self.defended = defended
        self.burned = burned
        self.iterations = iterations
        self.T = T
        self.cost = cost
        self.optimal = optimal
        self.neighborhood = None

    def calculate_cost(self, G: Graph):
        self.cost = len(set(G.nodes).difference(self.burned))

    def construct_neighborhood(self, k: int, G: Graph):
        '''
        Função que constrói todas as k-vizinhanças dos vértices defendidos na
        solução.

            Args:
                k (int): profundidade da vizinhança.
                G (Graph): o grafo de entrada.
        '''

        # Conjunto de todas as k-vizinhanças
        kn = set()

        for d in self.defended:

            kn.update(
                # Menores caminhos de profundidade k (as chaves retornam os
                # destinos)
                v_n for v_n in list(single_source_shortest_path(G, d, k)
                                    .keys())
                # Ignorar vértices queimados ou defendidos
                if v_n not in self.defended.union(self.burned)
            )

        self.neighborhood = kn

    def filter_neighborhood(self, k: int, sigma: float, G: Graph,
                            f: FunctionType):
        '''
        Função que filtra do conjunto de todas k-vizinhanças a fração sigma de
        melhores vizinhos de acordo com um critério guloso regido pela função
        f.

            Args:
                k     (int): profundidade da vizinhança.
                sigma (float): fração dos melhores vizinhos a serem
                               retornados.
                G     (Graph): o grafo de entrada.
                f     (FunctionType): critério guloso para rankear vizinhos.
        '''

        # Construir k-vizinhanças, se preciso
        if self.neighborhood is None:
            self.construct_neighborhood(k, G)

        # Ordenar k-vizinhanças em ordem descrescente usando função f
        kn_sorted = sorted(list(self.neighborhood),
                           key=lambda v: f(self, G, v),
                           reverse=True)

        # Retornar fração sigma dos melhores vizinhos
        return set(kn_sorted[:ceil(sigma * len(kn_sorted))])

    def full_solution(self):
        defended = [(x, self.iterations[x]) for x in self.defended]
        burned = [(x, self.iterations[x]) for x in self.burned]
        return defended, burned

    def __eq__(self, other):
        '''
        Duas soluções são consideradas iguais se o tamanho da diferença
        simétrica de suas vizinhanças for 0.
        '''
        return isinstance(other, Solution) and \
            len(self.neighborhood.symmetric_difference(other.neighborhood)) \
            == 0

    def __hash__(self):
        return hash(tuple(sorted(tuple(self.neighborhood))))

    def __repr__(self):
        defended, burned = self.full_solution()
        return (f"SOLUTION\n"
                f"Cost: {self.cost}\n"
                f"Defended vertices: {defended}\n"
                f"Burned vertices: {burned}")

    @ staticmethod
    def vars_to_solution(model: Model, G: Graph, T: int):
        ''' Função para traduzir variáveis do Gurobi para Solution.'''
        b, d = model._b, model._d
        defended, burned = set(), set()

        n = G.number_of_nodes()
        iteration = [inf for i in range(n)]

        # Converter variáveis para conjuntos/listas
        for v in range(n):
            for t in range(T+1):

                # Quando um nó é queimado ou defendido,
                # guarda a iteração e vai para o próximo.
                if b[v, t].X == 1.0:
                    burned.add(v)
                    iteration[v] = t
                    break
                elif d[v, t].X == 1.0:
                    defended.add(v)
                    iteration[v] = t
                    break

        optimal = model.status == GRB.Status.OPTIMAL
        return Solution(defended, burned, iteration, T, model.objVal,
                        optimal)
