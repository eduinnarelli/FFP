'''
Projeto Final: Mateurística para o Problema dos Brigadistas.

nat_grasp.py: Mateurística baseada no GRASP criada por Natanael Ramos et al.

Disciplina:
    MC859/MO824 - Pesquisa Operacional.
Autores:
    Eduardo Barros Innarelli - RA 170161
    Victor Ferreira Ferrari  - RA 187890

Universidade Estadual de Campinas - UNICAMP - 2020

Modificado em: 29/12/2020
'''

from argparse import ArgumentParser
from math import ceil, inf
from random import sample
from time import time
from types import FunctionType

from Solution import Solution
from FFP import FFP


class NatGRASP(object):
    def __init__(self, ffp: FFP, k: int, f: FunctionType, eps: float,
                 time_limit: float, start_time: float):
        self.ffp = ffp
        self.k = k
        self.f = f
        self.eps = eps
        self.limit = time_limit
        self.start_time = start_time

    def constructive_heuristic_th(self, alpha: float):
        '''
        Heurística construtiva Th executada no modo probabilístico, onde em
        cada etapa são escolhidos até D vértices para serem defendidos de forma
        aleatória, com maior prioridade àqueles que estão ameaçados.

            Args:
                alpha (float): parâmetro alpha do GRASP, que rege o quão guloso
                    ou aleatório é a heurística.
            Returns:
                A solução com os vértices defendidos, queimados e o custo.
        '''

        B = self.ffp.B
        D = self.ffp.D
        G = self.ffp.G
        n = G.number_of_nodes()

        # Inicialmente defendidos e queimados
        defended = set()
        burned = set(B)

        # Conjunto de vértices intocados
        U = set(G.nodes - B)

        # Registrar iterações em que um vértice é "tocado" (defendido ou
        # queimado)
        its = [0 if v in burned else inf for v in range(n)]
        t = 1

        # Tentar executar enquanto houver vértices intocados
        while len(U) > 0:

            # Os vértices ameaçados são os vizinhos dos vértices queimados que
            # não estão defendidos ou queimados
            th = set()
            for b in burned:
                th.update([
                    v_n for v_n in G.adj[b]
                    if v_n not in defended.union(burned)
                ])

            # Se não houver vértices ameaçados, todos estão queimados,
            # defendidos ou salvos
            if len(th) == 0:
                break

            # Rankear candidatos (maior prioridade aos ameaçados)
            ranked = list(th) + list(U - th)

            # Construir lista de candidatos restritos (RCL)
            RCL = ranked[:ceil(alpha * len(ranked))]

            # Defender até D vértices da RCL
            defend = sample(RCL, D if D < len(RCL) else len(RCL))

            # Queimar vértices ameaçados não defendidos
            burn = th - set(defend)

            # Atualizar iterações
            for v in burn.union(defend):
                its[v] = t
            t += 1

            # Atualizar conjuntos
            U -= th.union(defend)
            defended.update(defend)
            burned.update(burn)

        # Construir e retornar solução
        sol = Solution(defended=defended, burned=burned,
                       iterations=its, T=t)
        sol.calculate_cost(G)
        return sol

    def pool_selection(self, S: set, rho: int):
        lS = list(S).sort(key=lambda i: i.cost)
        best = lS[-1]
        q0 = lS[0].cost
        q4 = best.cost

        # TODO: não sei se está certo.
        # Separar conjuntos Si
        diff = (q4 - q0)/4
        q = list(range(q0+diff, q4+1, step=diff))
        Si = [[]*4]
        i = 0

        for j in lS:
            if (j.cost >= q[i]):
                i += 1
            Si[i].append(j)

        # Pseudocodigo começa aqui
        # IDEIA: calcular k-vizinhança de todos os elementos de S?
        pool = set([best])
        best_neigh = best.construct_neighborhood(self.k, 1.0, self.ffp.G,
                                                 self.f)
        for i in range(4):
            for s in Si[i]:
                if len(pool) < rho:
                    pool.add(s)
                else:
                    # TODO: pegar solução do pool com menor diferença simétrica da k vizinhança com best
                    # TODO: ver se s ou essa solução do pool é mais diverso. Stub:
                    if n_s.symmetric_difference(n_best) > \
                            n_old_s.symmetric_difference(n_best):
                        pool.remove(old_s)
                        pool.add(s)

            if len(pool) == rho:
                break

        return pool

    def neighborhood_update(self, sigma: float, solution: Solution):
        return min(1, sigma+0.1) if solution.optimal else max(0, sigma-0.1)

    def adaptive_local_search(self, problem: FFP, pool: list,
                              best_sol: Solution, time: float):
        '''
            Função para busca local adaptativa da mateurística baseada no
            GRASP. Faz busca local em todos os elementos de um pool de
            soluções, atualizando os hiperparâmetros de acordo.

                Args:
                    problem    (FFP): O problema a ser resolvido.
                    pool       (list): o pool de soluções a ser explorado.
                    best_sol   (Solution): melhor solução do pool.
                    time       (float): duração atual da execução.
        '''

        # Inicializar parâmetros.
        pool.reverse()
        pool.remove(best_sol)
        inc_sol = best_sol
        sigma, rho = 0.5, len(pool)
        local_time = (self.limit - time)/2

        # Explorar pool de soluções (exceto a melhor)
        for s in pool:
            sol_time = (self.limit - time - local_time)/rho

            # Busca local com T iterações
            problem.T = ceil((1+self.eps)*s.T)
            curr_sol = problem.local_search(s, self.k, sigma, self.f,
                                            sol_time)
            inc_sol = curr_sol if curr_sol.cost > inc_sol.cost else inc_sol

            # Atualizar sigma e outros parâmetros
            sigma = neighborhood_update(sigma, curr_sol)
            rho = rho - 1
            time = time() - self.start_time

        # Explorar melhor solução (agora com vizinhança adaptada)
        problem.T = ceil((1+self.eps)*best_sol.T)
        curr_sol = problem.local_search(best_sol, self.k, sigma, self.f,
                                        local_time)
        inc_sol = curr_sol if curr_sol.cost > inc_sol.cost else inc_sol
        time = time() - self.start_time

        return self.instensification(problem, sigma, inc_sol)

    def intensification(self, problem: FFP, sigma: float,
                        best_sol: Solution, time: float):

        # Iniciar parâmetros
        prev_sol = best_sol
        gamma = False
        prev_sig = sigma

        # Consecutivas buscas locais na melhor solução.
        while(time < self.limit):
            N_prev = prev_sol.construct_neighborhood(self.k, prev_sig,
                                                     problem.G, self.f)

            # Busca local com T iterações
            problem.T = ceil((1+self.eps)*prev_sol.T)
            curr_sol = problem.local_search(prev_sol, self.k, prev_sig,
                                            self.f, self.limit - time)
            best_sol = curr_sol if curr_sol.cost > best_sol.cost else best_sol

            # Atualizar sigma
            sigma = neighborhood_update(sigma, curr_sol)

            # Verificar critérios de parada: convergência e segundo reinício.
            N_curr = curr_sol.construct_neighborhood(self.k, sigma,
                                                     problem.G, self.f)

            if N_prev.symmetric_difference(N_curr) == 0 or \
                    (sigma == sig_prev and gamma):
                break

            # Reinício.
            if sigma == sig_prev and not gamma:
                sigma = 0.5
                gamma = True

            # Atualizar parâmetros
            prev_sol = curr_sol
            prev_sig = sigma
            time = time() - self.start_time

        return best_Sol


if __name__ == "__main__":
    # Ler argumentos da linha de comando
    parser = ArgumentParser(add_help=False)
    parser.add_argument('--input-file', type=str, required=True)
    parser.add_argument('--D', type=int, required=True)
    args = parser.parse_args()

    # Instanciar problema
    ffp = FFP(args.D)
    ffp.read_input(args.input_file)

    # Parâmetros
    k = 2
    f = None
    eps = 0.5
    limit = ffp.G.number_of_nodes() / 2
    alpha = 0.3
    eta = 11000
    rho = 4

    # Instanciar mateurística
    start_time = time()
    method = NatGRASP(ffp, k, f, eps, limit, start_time)

    # PASSO 1: Construção
    S = set()
    best = method.constructive_heuristic_th(alpha)
    S.add(best)

    # Critério de parada 1: eta iterações
    for i in range(eta):

        # Critério de parada 2: metade do limite de tempo alcançado
        if time() - method.start_time >= method.limit / 2:
            break

        curr = method.constructive_heuristic_th(alpha)
        best = curr if curr.cost > best.cost else best
        S.add(curr)

    print(best)

    # # Passo 2: Seleção
    # P = method.pool_selection(S, rho)

    # # Passo 3: Busca Local
    # best = method.adaptive_local_search(ffp, P, best, time()-start_time)
