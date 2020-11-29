#Coevolução no jogo Rastros - Projeto nº 3 - Introdução à Inteligência Artificial - edição 2020/21
#Grupo 42: Ivo Veiga - 44865 | João Silva - 48782 | Manuel Tovar - 49522

##############################################################################################
from jogos import * 

##############################################################################################
#Classe que encapsula o algoritmo coevol

class Coevol():
    def __init__(self):
        self.list_fun_caracts = None
        self.p__game_chromossome = {}
    
    def f_eval(self,state,player):
        game = self.p__game_chromossome[player][0]
        chromossome = self.p__game_chromossome[player][1]
        #estados terminais
        win_or_lose = game.utility(state, player)
        if win_or_lose == 1:
            return infinity
        elif win_or_lose == -1:
            return -infinity
        else:
            #combinacao linear dos genes peso * funcao caracteristica 
            res = 0
            for chrom_index, caract in enumerate(self.list_fun_caracts):
                res += chromossome[chrom_index] * caract(state,player)
            return res
        
    def play_game_pair(self,game_class,chromossome1,chromossome2,alfabeta_func,verbose=False) :
        def play_one_game(game):
            estado = game.initial
            if verbose :
                game.display(estado)
            fim = False
            while not fim :
                jogada = alfabeta_func(game,estado)
                if jogada == None:
                    return 1 if game.to_move(estado) == game.second else -1
                estado = game.result(estado,jogada)
                if verbose :
                    game.display(estado)
                fim = game.terminal_test(estado) 
            return game.utility(estado, game.to_move(game.initial))
        #primeiro jogo
        game = game_class()
        self.p__game_chromossome[game.first] = (game, chromossome1)
        self.p__game_chromossome[game.second] = (game, chromossome2)
        res_with_chrom1_fst = play_one_game(game)    
        #segundo jogo
        game = game_class()
        self.p__game_chromossome[game.first] = (game, chromossome2)
        self.p__game_chromossome[game.second] = (game, chromossome1)        
        res_with_chrom2_fst = play_one_game(game)

        if res_with_chrom1_fst == res_with_chrom2_fst:
            return 1,1 #empate ambos têm 1 vitória
        elif res_with_chrom1_fst > res_with_chrom2_fst:
            return 2,0 #chrom1 tem 2 vitórias , chrom2 tem 0 vitórias
        else:
            return 0,2 #chrom1 tem 0 vitórias , chrom2 tem 2 vitórias
        
    def play_n_pairs_per_limit(self,game_class,chromossome1,chromossome2,num_pairs_per_limit,depth_limits):
        chrom1_res = 0
        chrom2_res = 0
        for depth in depth_limits:  
            alfabeta_func = lambda game, state: alphabeta_cutoff_search_new(state,game,depth,eval_fn=self.f_eval)        
            for i in range (num_pairs_per_limit):
                chrom1_wins, chrom2_wins = self.play_game_pair(game_class, chromossome1, chromossome2, alfabeta_func)
                chrom1_res += chrom1_wins
                chrom2_res += chrom2_wins
        return chrom1_res, chrom2_res
    
    def init_population(self, dim, gene_pool, num_caracts):
        assert (dim & (dim-1) == 0) and dim != 0 #dim tem de ser potência de 2 (100 (4) and 011 (3) = 000)
        g = len(gene_pool)
        population = []
        for i in range(dim):
            new_individual = [gene_pool[random.randrange(0, g)] for c in range(num_caracts)]
            population.append(new_individual)
        return population
    
    def do_cup_competition(self, population, game_class, num_game_pairs, depth_limits):    
        fitness_list = []

        def do_round(players, i_round):
            winners = []
            for i in range(int(len(players)/2)):
                c1 = players[i*2]
                c2 = players[(i*2)+1]            
                wins1, wins2 = self.play_n_pairs_per_limit(game_class, c1, c2, num_game_pairs, depth_limits)
                if wins1 == wins2:
                    if random.choice([True,False]):
                        winners.append(c1)
                        fitness_list.append((c2,i_round))
                    else:
                        winners.append(c2)
                        fitness_list.append((c1,i_round))
                elif wins1 > wins2:
                    winners.append(c1)
                    fitness_list.append((c2,i_round))
                else:
                    winners.append(c2)
                    fitness_list.append((c1,i_round))

            if len(winners) > 1:
                do_round(winners,i_round+1)
            else:
                fitness_list.append((winners[0], i_round+1))

        random.shuffle(population) #modifica var. population, devolve None
        do_round(population, 1) #constroi a fitness_list

        return fitness_list
    
    def do_tournament_selection(self, fitness_table, k_rivais=2, verbose=False):      
        highest_fitness = 0
        best_chromosome = None

        k_choices = random.sample(fitness_table, k_rivais)
        if verbose:
            print("tournament selected chromosomes: ", k_choices)

        for chrom_fit in k_choices:
            if chrom_fit[1] > highest_fitness:
                highest_fitness = chrom_fit[1]
                best_chromosome = chrom_fit[0]

        return best_chromosome
    
    def generate_2_descendents(self, parent1, parent2):
        char_num = len(parent1)
        cut_point = random.randrange(1, char_num)
        f1 = parent1[:cut_point] + parent2[cut_point:]
        f2 = parent2[:cut_point] + parent1[cut_point:]
        return f1,f2
    
    def mutate_all_genes(self, chromossome, p_mut, mut_range=10):       
        new_chrom = []
        for c in chromossome:
            if random.uniform(0, 1) <= p_mut: 
                new_carac = c + random.randrange(-mut_range, mut_range+1)
                new_chrom.append(new_carac)
            else:
                new_chrom.append(c)
        return new_chrom
    
    def generate_new_gen_with_elitism(self, fitness_table, p_elit, k_rivais, p_mut):
        new_gen = []
        pop_size = len(fitness_table)

        elite_size = round(pop_size * p_elit)
        non_elite_size = pop_size - elite_size
        #assume-se que fitness_table está ordenado por ordem de fitness crescente
        for i in range(pop_size-1, non_elite_size-1, -1):        
            new_gen.append(fitness_table[i][0])    

        for i in range(int(non_elite_size/2)):
            parent1 = self.do_tournament_selection(fitness_table, k_rivais)
            parent2 = self.do_tournament_selection(fitness_table, k_rivais)

            desc1, desc2 = self.generate_2_descendents(parent1, parent2)

            m_desc1 = self.mutate_all_genes(desc1, p_mut)
            m_desc2 = self.mutate_all_genes(desc2, p_mut)

            new_gen.append(m_desc1)
            new_gen.append(m_desc2)

        diff_gen_sizes = pop_size - len(new_gen)
        if diff_gen_sizes != 0: #falta +1 individuo para gerar, acontece se elite_size for ímpar
            parent1 = self.do_tournament_selection(fitness_table, k_rivais)
            parent2 = self.do_tournament_selection(fitness_table, k_rivais)        
            desc1, _ = self.generate_2_descendents(parent1, parent2)  
            m_desc1 = self.mutate_all_genes(desc1, p_mut)
            new_gen.append(m_desc1)

        return new_gen
    
    def coevol(self, gen,dim,gene_pool,elit,p_mut,k_rivais,lim_profs,n_jogos,jogo,caracts):
        self.list_fun_caracts = caracts
        best_chromosomes = []

        population = self.init_population(dim, gene_pool, len(caracts))

        for i in range(gen):
            pop_fitness = self.do_cup_competition(population, jogo, n_jogos, lim_profs)   
            best_chromosomes.append(pop_fitness[-1])

            population = self.generate_new_gen_with_elitism(pop_fitness, elit, k_rivais, p_mut)

        pop_fitness = self.do_cup_competition(population, jogo, n_jogos, lim_profs)   
        best_chromosomes.append(pop_fitness[-1])
        
        return best_chromosomes


##############################################################################################
##############################################################################################
# Modelização do jogo do Galo (copiado do guião da PL5 + first e second) e suas funções características

#Funções Características para o TicTacToe

def f_num_centros_player(state,player):
    centro = (2,2)
    num_centros = 1 if centro in state.board and state.board[centro] == player else 0    
    return num_centros

def f_num_centros_oponent(state,player):
    centro = (2,2)
    num_centros = 1 if centro in state.board and state.board[centro] == state.other(player) else 0    
    return num_centros

def f_num_cantos_player(state,player):
    cantos = [(1,1),(1,3),(3,1),(3,3)]
    num_cantos = 0
    for canto in cantos:
        if canto in state.board and state.board[canto] == player:
            num_cantos += 1   
    return num_cantos

def f_num_cantos_oponent(state,player):
    cantos = [(1,1),(1,3),(3,1),(3,3)]
    num_cantos = 0
    for canto in cantos:
        if canto in state.board and state.board[canto] == state.other(player):
            num_cantos += 1   
    return num_cantos

def f_num_laterais_player(state,player):
    laterais = [(1,2),(2,1),(2,3),(3,2)]
    num_laterais = 0
    for lateral in laterais:
        if lateral in state.board and  state.board[lateral] == player:
            num_laterais += 1   
    return num_laterais

def f_num_laterais_oponent(state,player):
    laterais = [(1,2),(2,1),(2,3),(3,2)]
    num_laterais = 0
    for lateral in laterais:
        if lateral in state.board and  state.board[lateral] == state.other(player):
            num_laterais += 1   
    return num_laterais


#Estado e classe TicTacToe (copiado do guião da PL5 + first e second)

stateTicTacToe = namedtuple('stateTicTacToe', 'to_move, board, last_move')
class EstadoTicTacToe(stateTicTacToe):    
    def next_move(self,move):
        board = self.board.copy() # Sim, temos de duplicar o board.
        board[move] = self.to_move ## adiciona jogada ao dicionário (board)  
        return EstadoTicTacToe(to_move=self.other(self.to_move),
                         board=board,last_move=move)    
    def used_cells(self):
        return self.board.keys()
    def k_pieces(self,k):
        "If 'X' wins with this move, return 1; if 'O' wins return -1; else return 0."
        (play,board,move)=self
        if move=="None":
            return 0
        player = self.other(play) # the one thar has played, not the one that will play
        if (self.k_in_row(board, move, player, (0, 1),k) or
                self.k_in_row(board, move, player, (1, 0),k) or
                self.k_in_row(board, move, player, (1, -1),k) or
                self.k_in_row(board, move, player, (1, 1),k)):
            return 1 if player == 'X' else -1
        else:
            return 0    
    def k_in_row(self, board, move, player,delta_x_y,k):
        "Return true if there is a line with k cells through move on board for player."
        (delta_x, delta_y) = delta_x_y
        x, y = move
        n = 0  # n is number of moves in row
        while board.get((x, y)) == player:
            n += 1
            x, y = x + delta_x, y + delta_y
        x, y = move
        while board.get((x, y)) == player:
            n += 1
            x, y = x - delta_x, y - delta_y
        n -= 1  # Because we counted move itself twice
        return n >= k    
    def other(self,player):
        return 'X' if player == 'O' else 'O'    
    def display(self,h,v):
        for x in range(1, h + 1):
            for y in range(1, v + 1):
                print(self.board.get((x, y), '.'), end=' ')
            print()            

class TicTacToe(Game):
    """Play TicTacToe on an h x v board (h is the height of the board, and v the width), 
    with Max (first player) playing 'X'. k is the number of continuous marks to win a game.
    A state has the player to move, a cached utility, a list of moves in
    the form of a list of (x, y) positions (coordinates of a move), and a board, in the form of
    a dict of {(x, y): Player} entries, where Player is 'X' or 'O'."""

    def __init__(self, h=3, v=3, k=3):
        "The board is empty, it is 'X' that begins, and no last move"
        self.h = h
        self.v = v
        self.k = k
        self.initial = EstadoTicTacToe(to_move='X',board={},last_move="None")
        self.first = "X"
        self.second = "O"

    def actions(self, state):
        "Legal moves are any square not yet taken."
        return list([(x, y) for x in range(1, self.h + 1)
                 for y in range(1, self.v + 1)] - state.used_cells())

    def result(self, state, move):
        "Dado state executa jogada move"
        return state.next_move(move)
    
    
    def utility(self, state, player):
        "Return the value to player; 1 for win, -1 for loss, 0 otherwise."
        "If the player is X and .utility == 1 then return .utility"
        "Otherwise return the symmetric. Note that the symmetric of 0 is 0"
        "Note that player might be different from the player within the state that has just virtually played"
        aux = state.k_pieces(self.k)
        return aux if player == 'X' else -aux

    def terminal_test(self, state):
        "A state is terminal if someone won or there are no empty squares."
        "It assumes that the calculus if there is a winner is computed first and saved in .utility, thus it uses the value of .utility."
        return state.k_pieces(self.k) != 0 or len(self.actions(state)) == 0

    def display(self, state):
        print("Tabuleiro actual:")
        state.display(self.h,self.v)
        fim = self.terminal_test(state)
        if  fim:
            print("FIM do Jogo")
        else :
            print("Próximo jogador:{}\n".format(state.to_move))
