'''
Projeto Final: Mateurística para o Problema dos Brigadistas.

Solution.py: Classe para solução do problema dos brigadistas.

Disciplina:
    MC859/MO824 - Pesquisa Operacional.
Autores:
    Eduardo Barros Innarelli - RA 170161
    Victor Ferreira Ferrari  - RA 187890

Universidade Estadual de Campinas - UNICAMP - 2020

Modificado em: 15/12/2020
'''

from networkx import Graph
from math import inf

class Solution(object):
    def __init__(self, defended: set, burned: set, iterations: list,
                 cost: int = 0):
        self.defended = defended
        self.burned = burned
        self.iterations = iterations
        self.cost = cost

    def calculate_cost(self, G: Graph):
        self.cost = len(set(G.nodes).difference(self.burned))

    def full_solution(self):
        defended = [(x, self.iterations[x]) for x in self.defended]
        burned = [(x, self.iterations[x]) for x in self.burned]
        return defended, burned

    def __repr__(self):
        defended,burned = self.full_solution()
        return (f"SOLUTION\n"
                f"Cost: {self.cost}\n"
                f"Defended vertices: {defended}\n"
                f"Burned vertices: {burned}")


    @staticmethod
    def vars_to_solution(model, problem):
        ''' Função para traduzir variáveis do Gurobi para Solution.'''
        b, d = model._b, model._d
        defended, burned = set(), set()

        n = problem.G.number_of_nodes()
        iteration = [inf for i in range(n)]

        # Converter variáveis para conjuntos/listas
        for v in range(n):
            for t in range(problem.T+1):

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

        return Solution(defended, burned, iteration, model.objVal)
