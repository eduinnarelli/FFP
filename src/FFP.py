'''
Projeto Final: Mateurística para o Problema dos Brigadistas.

FFP.py: Classe para o problema dos brigadistas.

Disciplina:
    MC859/MO824 - Pesquisa Operacional.
Autores:
    Eduardo Barros Innarelli - RA 170161
    Victor Ferreira Ferrari  - RA 187890

Universidade Estadual de Campinas - UNICAMP - 2020

Modificado em: 01/01/2021
'''

from networkx import Graph
from math import ceil

from M_FFM import m_ffm
from Solution import Solution

class FFP(object):
    def __init__(self, D: int, G: Graph = Graph(), B: list = [], T: int = 0):
        # Parâmetro obrigatório
        self.D = D

        # Parâmetros opcionais.
        self.G = G
        self.B = B
        self.T = T
        self.model = None

    def read_input(self, filename: str):
        ''' Função para carregar uma instância.'''

        with open(filename, 'r') as f:

            # Iterar sobre as linhas do arquivo
            for (idx, line) in enumerate(f):
                values = line.split()

                # Adicionar vértices de B
                if idx > 4 and len(values) == 1:
                    self.B.append(int(values[0]))

                # Adicionar arestas
                elif len(values) == 2:
                    self.G.add_edge(int(values[0]), int(values[1]))

        # Número de vértices e arestas
        n = self.G.number_of_nodes()

        # Limite de iterações
        self.T = ceil(n / self.D)
    
    def start_model(self):
        self.model = m_ffm(self.G, self.B, self.D, self.T, 0)
        
    def local_search(self, sol: Solution, k: int, sigma: float, f: str, 
                     time_limit: float):
        if (time_limit <= 0): 
            return sol
        
        # Construir grupo de variáveis fixadas.
        neigh = sol.construct_neighborhood(k, sigma, self.G, f)
        N = set(self.G.nodes).difference(neigh.union(sol.defended))
        
        # Fixar variáveis d_vt para v \in N e 0 <= t <= T
        d = self.model._d
        new_constrs = self.model.addConstrs((
                        d[v, t] == 0 for v in N for t in range(self.T+1)
                      ))
        self.model.setParam('TimeLimit', time_limit)
        self.model.update()
        
        # Resolver M-FFM e retornar solução.
        self.model.optimize()
        self.model.remove(new_constrs)
        return Solution.vars_to_solution(self.model, self.G, self.T)

    def __repr__(self):
        return (f"FFP\n"
                f"Firefighters: {self.D}, Iterations: {self.T}\n"
                f"Initial Burned Nodes: {self.B}\n"
                f"Nodes: {self.G.nodes}\n"
                f"Edges: {self.G.edges}")
