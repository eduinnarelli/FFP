'''
Projeto Final: Mateurística para o Problema dos Brigadistas.

desc.py: Funções para calcular o número descendentes de um vértice em uma
solução.

Disciplina:
    MC859/MO824 - Pesquisa Operacional.
Autores:
    Eduardo Barros Innarelli - RA 170161
    Victor Ferreira Ferrari  - RA 187890

Universidade Estadual de Campinas - UNICAMP - 2020

Modificado em: 31/12/2020
'''

from networkx import Graph, shortest_path_length
from Solution import Solution


def is_descendant(G: Graph, B: set, u: int, v: int):
    '''
    Função que checa se o vértice v é descendente de u no grafo não direcionado
    G. Aqui, v é descendente de u se existe um caminho entre eles e se d(v, B)
    > d(u, B), i.e., u está mais próximo do conjunto B.

    NOTE: a entrada sempre é um grafo não-direcionado e conexo, então sempre há
    um caminho entre u e v.
    '''

    # Checar se u está mais próximo de B do que v
    d_uB = min([shortest_path_length(G, u, b) for b in B])
    d_vB = min([shortest_path_length(G, v, b) for b in B])
    if d_uB < d_vB:
        return True

    return False


def num_of_descendants(sol: Solution, G: Graph, u: int):
    '''
    Função que calcula e retorna o número de descendentes do vértice u.
    '''
    return sum(is_descendant(G, sol.burned, u, v) for v in G.nodes)
