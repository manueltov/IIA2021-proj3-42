from jogos import *

stateRastros = namedtuple('EstadoRastros', 'to_move, white, blacks')

class EstadoRastros(stateRastros):

    def ve_se_terminou(self):
        "devolve 1 se ganhou sul, -1 se ganhou norte, 0 se não terminou"
        if self.blacks==set():
            return 0
        justplayed = self.other(self.to_move) 
        if self.white==(8,1):
            return 1 
        elif self.white == (1,8):
            return -1 
        elif len(self.moves()) == 0:
            return 1 if justplayed == 'S' else -1
        else:
            return 0
        
    def __init__(self, to_move, white, blacks):
        self.fullboard = set([(x, y) for x in range(1, 9)
                 for y in range(1, 9)])
        self.terminou = self.ve_se_terminou() # = 1 se ganhou sul, -1 se ganhou norte, 0 se não terminou

    def moves(self):
        "Legal moves are any square adjacent to white if not in blacks"
        alladjacent = [(self.white[0]+a, self.white[1]+b) for a in [-1,0,1] for b in [-1,0,1]]
        return [p for p in alladjacent
                if p not in self.blacks and p !=self.white and p in self.fullboard]

    def compute_utility(self, player):
        "If player wins in this state, return 1; if otherplayer wins return -1; else return 0."
        return self.terminou if player=='S' else -self.terminou

    def other(self,player):
        return 'N' if player == 'S' else 'S'


    def posicao(self, a, b):
        if (a,b)==self.white:
            return 'o' 
        elif (a,b) in self.blacks:
            return '@'
        else:
            return '.'
        
    def display(self):
        print(" 12345678")
        for x in range(1, 9):
            print(x, end="")
            for y in range(1, 9):
                print(self.posicao(x, y), end='')
            print(x)
        print(" 12345678 ")





estado_inicial = EstadoRastros(to_move = 'S', white = (4,5), blacks=set())


class Rastros(Game):
    """Play rastros on an 8 x 8 board, with Max (first player) playing 'S'.
    A state has the player to move, a cached utility, a list of moves in
    the form of a list of (x, y) positions, and a board, represented by the
    position of the white mark and a list of positions of the black marks."""

    def __init__(self):
        self.fullboard = set([(x, y) for x in range(1, 9)
                 for y in range(1, 9)])
        self.initial = EstadoRastros(to_move = 'S', white = (4,5), blacks=set())
        self.first = "S"
        self.second = "N"

    def actions(self, state):
        "Legal moves are any square adjacent to white if not in blacks"
        return state.moves()

    def result(self, state, move):
        blacks = state.blacks.copy() # Sim, temos de duplicar o conjunto de blacks
        blacks.add(state.white) ## marca a antiga white como black
        return EstadoRastros(to_move=('N' if state.to_move == 'S' else 'S'),
                         white=move,blacks=blacks)

    def utility(self, state, player):
        "Return the value to player; 1 for win, -1 for loss, 0 otherwise."
        "If the player is S and .utility == 1 then return .utility"
        "Otherwise return the symmetric. Note that the symmetric of 0 is 0"
        "Note that player might be different from the player within the state that has just virtually played"
        #aux = self.compute_utility(state)
        #return aux if player == 'S' else -aux
        
        return state.compute_utility(player)
        

    def terminal_test(self, state):
        "A state is terminal if someone won or there are no empty squares."
        "It assumes that the calculus if there is a winner is computed first and saved in .utility, thus it uses the value of .utility."
        return state.terminou != 0


    def display(self, state):
        print("Tabuleiro:")
        state.display()
        fim = self.terminal_test(state)
        if  fim:
            print("FIM do Jogo")
        else :
            print("Próximo jogador:{}\n".format(state.to_move))



##########
def jogaRastros11(jog1, jog2):
    ### jog1 e jog2 são jogadores com funções que dado um estado do jogo devolvem a jogada que escolheram
    ### devolve uma lista de jogadas e o resultado 1 se S ganha
    game = Rastros()
    estado=game.initial
    proxjog = jog1
    lista_jogadas=[]
    while not game.terminal_test(estado):
        jogada = proxjog.fun(game, estado)
        estado=game.result(estado,jogada)
        lista_jogadas.append((proxjog.nome, jogada))
        proxjog = jog2 if proxjog == jog1 else jog1
    return (lista_jogadas, estado.terminou)



def jogaRastros11_display(jog1, jog2):
    ### jog1 e jog2 são jogadores com funções que dado um estado do jogo devolvem a jogada que escolheram
    ### devolve uma lista de jogadas e o resultado 1 se S ganha
    game = Rastros()
    estado=game.initial
    game.display(estado)
    proxjog = jog1
    lista_jogadas=[]
    while not game.terminal_test(estado):
        jogada = proxjog.fun(game, estado)
        estado=game.result(estado,jogada)
        lista_jogadas.append((proxjog.nome, jogada))
        proxjog = jog2 if proxjog == jog1 else jog1
        game.display(estado)
    return (lista_jogadas, estado.terminou)

from func_timeout import func_timeout, FunctionTimedOut

def jogaRastros11com_timeout(jog1, jog2, nsec):
    ### jog1 e jog2 são jogadores com funções que dado um estado do jogo devolvem a jogada que escolheram
    ### devolve uma lista de jogadas e o resultado 1 se S ganha
    game = Rastros()
    estado=game.initial
    proxjog = jog1
    lista_jogadas=[]
    while not game.terminal_test(estado):
        try:
            ReturnedValue = func_timeout(nsec, proxjog.fun, args=(game, estado))
        except FunctionTimedOut:
            print("pim!", proxjog.nome)
            ReturnedValue = None    
        jogada = ReturnedValue
        if jogada == None:
            estado.terminou = 1 if proxjog==jog2 else -1 # se norte deu timeout ganha sul e vice-versa 
            return (lista_jogadas, estado.terminou)
        else:
            estado=game.result(estado,jogada)
            lista_jogadas.append((proxjog.nome, jogada))
            proxjog = jog2 if proxjog == jog1 else jog1
    return (lista_jogadas, estado.terminou)



def mostraJogo(listajog, verbose = False, step_by_step=False):
    j = Rastros()
    estado = j.initial
    for jog in listajog:
        if verbose:
            j.display(estado)
        if step_by_step:
            input()
        estado=j.result(estado,jog[1])
        print(jog[0]+ "--> ", str(jog[1]))
    if verbose:
        j.display(estado)
    print('{}'.format("Ganhou S" if estado.terminou == 1 else "Ganhou N" if estado.terminou == -1 else "Empate"))

def jogaRastrosNN(listaJog, listaAdv, nsec=1):
    ### devolve uma lista de tuplos da forma (j1, j2, (lista de jogadas, vencedor))
    lista_jogos=[]
    for jog in listaJog:
        for adv in listaAdv:
            if jog != adv:
                lista_jogos.append((jog.nome, adv.nome, jogaRastros11com_timeout(jog,adv, nsec)))
    return lista_jogos

########
# Classe Jogador com algumas instâncias

class Jogador():
    def __init__(self, nome, fun):
        self.nome = nome
        self.fun = fun
    def display(self):
        print(nome+" ")

import random

def bacoco(game, state):
    return random.choice(state.moves())

bacoco = Jogador("Bacoco", bacoco)


def sudoeste(game, state):
    moves = state.moves()
    moves.sort(key = lambda t: (t[0],-t[1]))
    return moves[-1]

def nordeste(game, state):
    moves = state.moves()
    moves.sort(key = lambda t: (-t[0],t[1]))
    return moves[-1]

obtusoSW = Jogador("ObtusoSW", sudoeste)

obtusoNE = Jogador("ObtusoNE", nordeste)


def pergunta(game, state):
    state.display()
    print("Jogadas possíveis: ", state.moves())
    return eval(input(state.to_move+", para onde quer jogar? "))
    
humano1 = Jogador("Pessoa1", pergunta)
humano2 = Jogador("Pessoa2", pergunta)

##### profundidade igual para todos
depth_for_all = 5


########
#### funções heurísticas para avaliação de estado
def num_livres(estado,jogador) :
    "maximiza o espaço livre junto à peça B"
    return len(estado.moves())
   

#### mais um jogador, agora com alpha-beta
arlivre = Jogador("Ar Livre",
                  lambda game, state:
                  alphabeta_cutoff_search_new(state,game,depth_for_all,eval_fn=num_livres))

humano = Jogador("humano",query_player)

##### heuristica para jogador básico
# derrota vale -10, vitória vale 10,
# cc subtrai distância da peça branca à casa objectivo

def distancia (a, b):
    return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

def f_aval_basico(estado, jogador):
    if estado.terminou == 1:
        return 10 if jogador == "S" else -10
    elif estado.terminou == -1:
        return 10 if jogador == "N" else -10
    else:
        obj = (8, 1) if jogador == "S" else (1, 8)
        return 7-distancia(estado.white, obj)


basilio = Jogador("Basilio",
                  lambda game, state:
                  alphabeta_cutoff_search_new(state,game,depth_for_all,eval_fn=f_aval_basico))



### todos os jogadores definidos excepto os humanos
todosJog = [bacoco, obtusoSW, obtusoNE, arlivre, basilio]


######## Funções para jogar e fazer torneios
def faz_campeonato(listaJogadores, nsec=10):
    ### faz todos os jogos com timeout de nsec por jogada
    campeonato = jogaRastrosNN(listaJogadores, listaJogadores, nsec)
    ### ignora as jogadas e contabiliza quem ganhou
    resultado_jogos = [(a,b,n) for (a,b,(x,n)) in campeonato]
    tabela = dict([(jog.nome, 0) for jog in listaJogadores])
    for jogo in resultado_jogos:
        if jogo[2] == 1:
            tabela[jogo[0]] += 1
        else:
            tabela[jogo[1]] += 1
    classificacao = list(tabela.items())
    classificacao.sort(key=lambda p: -p[1])
    print("JOGADOR", "VITÓRIAS")
    for jog in classificacao:
        print('{:11}'.format(jog[0]), '{:>4}'.format(jog[1]))


