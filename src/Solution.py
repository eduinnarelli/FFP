'''
Projeto Final: Mateurística para o Problema dos Brigadistas.

Solution.py: Classe para solução do problema dos brigadistas.

Disciplina:
    MC859/MO824 - Pesquisa Operacional.
Autores:
    Eduardo Barros Innarelli - RA 170161
    Victor Ferreira Ferrari  - RA 187890

Universidade Estadual de Campinas - UNICAMP - 2020

Modificado em: 14/12/2020
'''

from networkx import Graph

class Solution(object):
    def __init__(self, defended: set, burned: set, iterations: list,
                 cost: int=0):
        self.defended = defended
        self.burned = burned
        self.iterations = iterations
        self.cost = cost
    
    def calculate_cost(self, G: Graph):
        self.cost = set(G.nodes).difference(self.burned)
