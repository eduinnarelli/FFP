'''
Projeto Final: Mateurística para o Problema dos Brigadistas.

FFP.py: Classe para o problema dos brigadistas.

Disciplina:
    MC859/MO824 - Pesquisa Operacional.
Autores:
    Eduardo Barros Innarelli - RA 170161
    Victor Ferreira Ferrari  - RA 187890

Universidade Estadual de Campinas - UNICAMP - 2020

Modificado em: 05/01/2021
'''

from networkx import Graph, all_pairs_shortest_path_length

from M_FFM import m_ffm
from Solution import Solution


class FFP(object):
    def __init__(self, D: int, B: list = [], T: int = 0):
        # Parâmetro obrigatório
        self.D = D

        # Parâmetros opcionais
        self.B = B
        self.max_T = T

        # Inicializar grafo
        self.G = Graph()

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

        # Calcular caminho mínimo entre todos os pares
        self.sp_len = dict(all_pairs_shortest_path_length(self.G))

    def local_search(self, sol: Solution, k: int, sigma: float, f: str,
                     T: int, time_limit: float):
        if (time_limit <= 0):
            return sol

        # Construir grupo de variáveis fixadas.
        neigh = sol.filter_neighborhood(self, k, sigma, f)
        N = set(self.G.nodes).difference(neigh)

        # Fixar variáveis d_vt para v \in N e 0 <= t <= T
        T = min(self.max_T, T)
        model = m_ffm(self.G, self.sp_len, self.B, self.D, T, time_limit)
        d = model._d
        model.addConstrs((
            d[v, t] == 0 for v in N for t in range(T+1)
        ))
        model.update()

        # Resolver M-FFM e retornar solução.
        model.optimize()
        if model.SolCount > 0:
            sol = Solution.vars_to_solution(model, self.G, T)

        return sol

    def __repr__(self):
        return (f"FFP\n"
                f"Firefighters: {self.D}, Max Iterations: {self.max_T}\n"
                f"Initial Burned Nodes: {self.B}\n"
                f"Nodes: {self.G.nodes}\n"
                f"Edges: {self.G.edges}")
