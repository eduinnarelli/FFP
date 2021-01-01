'''
Projeto Final: Mateurística para o Problema dos Brigadistas.

nat_grasp.py: Mateurística baseada no GRASP criada por Natanael Ramos et al.

Disciplina:
    MC859/MO824 - Pesquisa Operacional.
Autores:
    Eduardo Barros Innarelli - RA 170161
    Victor Ferreira Ferrari  - RA 187890

Universidade Estadual de Campinas - UNICAMP - 2020

Modificado em: 01/01/2021
'''

from argparse import ArgumentParser
from math import ceil, inf
from random import sample
from time import time
from types import FunctionType

from Solution import Solution
from FFP import FFP
from desc import num_of_descendants


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
                    ou aleatória é a heurística.
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
        S = list(S)
        S.sort(key=lambda i: i.cost)
        best = S.pop()
        q0 = S[0].cost
        q4 = best.cost

        # TODO: não sei se está certo.
        # Criar quantis q_i
        diff = (q4 - q0)//4
        q = list(range(q0+diff, q4+1, diff))
        Si = [[], [], [], []]
        
        # Separar conjuntos Si.
        i = 0
        for j in S:
            if (j.cost > q[i]):
                i += 1
            Si[i].append(j)

        # Iniciar pool e construir vizinhanças para economizar tempo.
        neigh = lambda s: s.construct_neighborhood(self.k, 1.0, self.ffp.G,
                                                   self.f) 
        pool = []
        n_s = {s:neigh(s) for s in S}
        n_best = neigh(best)
            
        # Pseudocodigo começa aqui:
        # Para cada Si (ao contrário), adiciona no pool até "rho-1" elementos.
        # Em seguida, verifica diversidade, substituindo os elementos
        # menos diversos até acabar o último conjunto. 
        for i in range(4)[::-1]:
            for s in Si[i]:
                if len(pool) < rho-1:
                    pool.append(s)
                else:
                    old_s = min(pool, key=lambda x: len(n_s[x].symmetric_difference(n_best)))
                    if len(n_s[s].symmetric_difference(n_best)) > \
                            len(n_s[old_s].symmetric_difference(n_best)):
                        pool.remove(old_s)
                        pool.append(s)

            if len(pool) == rho-1:
                break
        
        return pool, best

    def neighborhood_update(self, sigma: float, solution: Solution):
        return min(1, sigma+0.1) if solution.optimal else max(0, sigma-0.1)

    def adaptive_local_search(self, problem: FFP, pool: list,
                              best_sol: Solution, curr_time: float):
        '''
            Função para busca local adaptativa da mateurística baseada no
            GRASP. Faz busca local em todos os elementos de um pool de
            soluções, atualizando os hiperparâmetros de acordo.

                Args:
                    problem    (FFP): O problema a ser resolvido.
                    pool       (list): o pool de soluções a ser explorado.
                    best_sol   (Solution): melhor solução do pool.
                    curr_time  (float): duração atual da execução.
        '''

        # Inicializar parâmetros.
        pool.reverse()
        inc_sol = best_sol
        sigma, rho = 0.5, len(pool)
        local_time = (self.limit - curr_time)/2

        # Explorar pool de soluções (exceto a melhor)
        for s in pool:
            sol_time = (self.limit - curr_time - local_time)/rho

            # Busca local com T iterações
            problem.T = ceil((1+self.eps)*s.T)
            curr_sol = problem.local_search(s, self.k, sigma, self.f,
                                            sol_time)
            inc_sol = curr_sol if curr_sol.cost > inc_sol.cost else inc_sol

            # Atualizar sigma e outros parâmetros
            sigma = self.neighborhood_update(sigma, curr_sol)
            rho = rho - 1
            curr_time = time() - self.start_time

        # Explorar melhor solução (agora com vizinhança adaptada)
        problem.T = ceil((1+self.eps)*best_sol.T)
        curr_sol = problem.local_search(best_sol, self.k, sigma, self.f,
                                        local_time)
        inc_sol = curr_sol if curr_sol.cost > inc_sol.cost else inc_sol
        curr_time = time() - self.start_time

        return self.intensification(problem, sigma, inc_sol, curr_time)

    def intensification(self, problem: FFP, sigma: float,
                        best_sol: Solution, curr_time: float):
        '''
            Função de intensificação de busca da mateurística baseada no
            GRASP. Realiza uma série de buscas locais em cima da melhor
            solução, com diferentes valores de "sigma" para busca local.
            Early stopping em caso de convergência.

                Args:
                    problem    (FFP): O problema a ser resolvido.
                    sigma      (float): fração de elementos da vizinhança.
                    best_sol   (Solution): melhor solução do pool.
                    curr_time  (float): duração atual da execução.
        '''

        # Iniciar parâmetros
        prev_sol = best_sol
        gamma = False
        prev_sig = sigma

        # Consecutivas buscas locais na melhor solução.
        while(curr_time < self.limit):
            N_prev = prev_sol.construct_neighborhood(self.k, prev_sig,
                                                     problem.G, self.f)

            # Busca local com T iterações
            problem.T = ceil((1+self.eps)*prev_sol.T)
            curr_sol = problem.local_search(prev_sol, self.k, prev_sig,
                                            self.f, self.limit - curr_time)
            best_sol = curr_sol if curr_sol.cost > best_sol.cost else best_sol

            # Atualizar sigma
            sigma = self.neighborhood_update(sigma, curr_sol)

            # Verificar critérios de parada: convergência e segundo reinício.
            N_curr = curr_sol.construct_neighborhood(self.k, sigma,
                                                     problem.G, self.f)

            if len(N_prev.symmetric_difference(N_curr)) == 0 or \
                    (sigma == sig_prev and gamma):
                break

            # Reinício.
            if sigma == sig_prev and not gamma:
                sigma = 0.5
                gamma = True

            # Atualizar parâmetros
            prev_sol = curr_sol
            prev_sig = sigma
            curr_time = time() - self.start_time

        return best_sol


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
    f = num_of_descendants
    eps = 0.5
    limit = ffp.G.number_of_nodes() / 2
    alpha = 0.3
    eta = 11000
    rho = 4

    # Instanciar mateurística
    start_time = time()
    method = NatGRASP(ffp, k, f, eps, limit, start_time)
    ffp.start_model()

    # PASSO 1: Construção
    S = set()

    # Critério de parada 1: eta iterações
    for _ in range(eta):

        # Critério de parada 2: metade do limite de tempo alcançado
        if time() - method.start_time >= method.limit / 2:
            break

        curr = method.constructive_heuristic_th(alpha)
        S.add(curr)

    # Passo 2: Seleção
    P, best = method.pool_selection(S, rho)
    
    print("Pool:", P)
    print("Length:", len(P))

    # Passo 3: Busca Local
    best = method.adaptive_local_search(ffp, P, best, time()-start_time)
    print(best)
