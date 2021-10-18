import abc
import random
import numpy as np
import pandas as pd

class Resultado:
    def __init__(self, rodadas, perfil, saldo):
        self.rodadas = rodadas
        self.perfil = perfil
        self.saldo = saldo

    def __repr__(self):
        return f'Resultado(rodadas={self.rodadas}, perfil={self.perfil}, saldo={self.saldo})'

class Estrategia(abc.ABC):
    @abc.abstractmethod
    def realiza_compra(self, Propriedade):
        pass


class DecisaoImpulsivo(Estrategia):
    def realiza_compra(self, propriedade):
        return self.saldo > propriedade.valor


class DecisaoExigente(Estrategia):
    def realiza_compra(self, propriedade):
        return propriedade.aluguel > 50


class DecisaoCauteloso(Estrategia):
    def realiza_compra(self, propriedade):
        return (self.saldo - propriedade.aluguel) >= 80


class DecisaoAleatorio(Estrategia):
    def realiza_compra(self, propriedade):
        return int(random.choices([0, 1], [50, 50], k=1)[0]) == 1


class Jogador:
    def __init__(self, id, perfil, saldo, ativo, Estrategia):
        self.id = id
        self.perfil = perfil
        self.saldo = saldo
        self.ativo = ativo
        self.estrategia = Estrategia

    def __repr__(self):
        return f'Jogador(id={self.id}, perfil={self.perfil}, saldo={self.saldo}, ativo={self.ativo})'


class Propriedade:
    def __init__(self, id, valor, aluguel, id_proprietario, disponivel):
        self.id = id
        self.valor = valor
        self.aluguel = aluguel
        self.id_proprietario = id_proprietario
        self.disponivel = disponivel

    def __repr__(self):
        return f'Propriedade(id={self.id}, valor={self.valor}, aluguel={self.aluguel}, id_proprietario={self.id_proprietario}, disponivel={self.disponivel})'


class Slot:
    def __init__(self, propriedade, idjogadores=[]):
        self.propriedade = propriedade
        self.jogadores = idjogadores

    def __repr__(self):
        return f'Slot({repr(self.propriedade)}, {repr(self.jogadores)}'


class Tabuleiro:

    def __cria_slots(self, jogadores):
        slots = []
        valor = 20
        for p in range(1, 21):

            valor = valor + 10

            if valor > 200:
                valor = 10

            slot = Slot(Propriedade(p, valor, int(valor / 3), None, 1), [])

            if p == 1:
                for j in jogadores:
                    slot.jogadores.append(j.id)

            slots.append(slot)

        return slots

    def cria_tabuleiro(self, jogadores):
        return self.__cria_slots(jogadores)


class Partida:
    jogadores = []
    ultimo_jogador = -1
    imprime_log = True

    def __log(self, mensagem):
        if self.imprime_log == True:
            print(mensagem)


    def __jogar_dado(self):

        numero_dado = int(random.uniform(1, 7))

        self.__log(f'Numero sorteado {numero_dado}')

        return numero_dado


    def __cria_jogadores(self):

        jogadores = [Jogador(1, 'Impulsivo', 400, 1, DecisaoImpulsivo),
                     Jogador(2, 'Exigente', 400, 1, DecisaoExigente),
                     Jogador(3, 'Cauteloso', 400, 1, DecisaoCauteloso),
                     Jogador(4, 'Aleatorio', 400, 1, DecisaoAleatorio)]


        return random.sample(jogadores, len(jogadores))


    def __proximo_jogador(self):
        inativos = 0

        for j in self.jogadores:
            if j.ativo == 0:
                inativos += 1

        if inativos == len(self.jogadores) - 1:
            self.__log(f'Não existem mais outros jogadores')
            return None

        jogador_atual = self.ultimo_jogador + 1

        while True:
            if jogador_atual > len(self.jogadores) - 1:
                jogador_atual = 0

            if self.jogadores[jogador_atual].ativo == 1:
                break
            else:
                jogador_atual += 1

        self.ultimo_jogador = jogador_atual

        self.__log(f'Jogador atual {self.jogadores[jogador_atual].id}')

        return self.jogadores[jogador_atual]


    def __procura_jogador_tabuleiro(self, jogador):
        for slot in self.tabuleiro:
            if jogador.id in slot.jogadores:

                self.__log(f'Jogador atual {jogador.id} está na casa {slot.propriedade.id}')

                return slot


    def __pode_comprar_propriedade_slot(self, jogador, propriedade):
        retorno = propriedade.disponivel == 1 and jogador.saldo >= propriedade.valor

        if retorno == True:
            self.__log(f'Jogador {jogador.id} pode comprar casa {propriedade.id}')
        else:
            self.__log(f'Jogador {jogador.id} não pode comprar casa {propriedade.id}')

        return retorno


    def __verifica_decisao_jogador(self, jogador, propriedade):
        retorno = jogador.estrategia.realiza_compra(jogador, propriedade)

        if retorno == True:
            self.__log(f'Jogador {jogador.id} decidiu comprar')
        else:
            self.__log(f'Jogador {jogador.id} decidiu não comprar')

        return retorno


    def __localiza_dono_propriedade(self, jogador, propriedade):
        if propriedade.id_proprietario == None or propriedade.id_proprietario == jogador.id:
            return None

        for j in self.jogadores:
            if propriedade.id_proprietario == j.id:
                self.__log(f'A propriedade {propriedade.id} já possui um dono ({j.id})')
                return j


    def __debita_compra_jogador(self, jogador, propriedade):

        self.__log(f'Jogador {jogador.id} pagou {propriedade.valor} pela propriedade')

        jogador.saldo = jogador.saldo - propriedade.valor

        self.__log(f'Jogador {jogador.id} está com saldo {jogador.saldo}')

        return jogador


    def __debita_aluguel_jogador(self, jogador, propriedade):

        self.__log(f'Jogador {jogador.id} pagou aluguel de {propriedade.aluguel}')

        jogador.saldo = jogador.saldo - propriedade.aluguel

        self.__log(f'Jogador {jogador.id} está com saldo {jogador.saldo}')

        return jogador


    def __credita_aluguel_jogador(self, jogador, propriedade):

        self.__log(f'Jogador {jogador.id} recebeu aluguel de {propriedade.aluguel}')

        jogador.saldo = jogador.saldo + propriedade.aluguel

        self.__log(f'Jogador {jogador.id} está com saldo {jogador.saldo}')

        return jogador


    def __atualiza_propriedades_jogador(self, jogador):

        self.__log(f'Colocando propriedades do jogador {jogador.id} a venda')

        for slot in self.tabuleiro:
            if jogador.id == slot.propriedade.id_proprietario:

                self.__log(f'Propriedade a venda {slot.propriedade.id}')

                slot.propriedade.id_proprietario = None
                slot.propriedade.disponivel = 1


    def __verifica_se_desativa_jogador(self, jogador):

        if jogador.saldo < 0:
            jogador.ativo = 0
            self.__log(f'Jogador {jogador.id} está fora do jogo')

            self.__atualiza_propriedades_jogador(jogador)

        return jogador


    def __procura_proximo_slot(self, slot_atual, numero_dado):
        index_slot_atual = slot_atual.propriedade.id - 1

        novo_index = index_slot_atual + numero_dado

        if novo_index > len(self.tabuleiro) - 1:
            novo_index = (index_slot_atual + numero_dado - (len(self.tabuleiro) - 1)) - 1

        return self.tabuleiro[novo_index]


    def __atualiza_slot(self, slot):
        self.tabuleiro[slot.propriedade.id - 1] = slot


    def __retorna_vencedor(self, jogadores):

        idx_vencedor = -1

        for i in range(0, len(jogadores) - 1):
            if jogadores[i].ativo == 1:

                if idx_vencedor > -1:
                    if jogadores[i].ativo > jogadores[idx_vencedor].ativo:
                        idx_vencedor = i
                else:
                    idx_vencedor = i

        return jogadores[idx_vencedor]



    def __efetiva_compra_propriedade(self, jogador_atual, slot_atual):

        self.__log(f'Efetivada a compra para o jogador {jogador_atual.id}')

        slot_atual.propriedade.id_proprietario = jogador_atual.id
        slot_atual.propriedade.disponivel = 0

        return slot_atual


    def __move_jogador(self, jogador_atual, slot_atual, numero_dado):

        self.__log(f'Movendo jogador {numero_dado} casas')

        if jogador_atual.ativo == 1:
            slot_novo = self.__procura_proximo_slot(slot_atual, numero_dado)

            slot_novo.jogadores.append(jogador_atual.id)

            self.__atualiza_slot(slot_novo)

        slot_atual.jogadores.remove(jogador_atual.id)

        self.__atualiza_slot(slot_atual)

        return slot_novo


    def __atualiza_jogador(self, jogador):

        for j in self.jogadores:
            if j.id == jogador.id:
                j = jogador
                break


    def __executa_jogada(self):

        self.__log('Executando jogada')

        jogador_atual = self.__proximo_jogador()

        if jogador_atual == None:
            return False

        numero_dado = self.__jogar_dado()

        slot_atual = self.__procura_jogador_tabuleiro(jogador_atual)

        slot_atual = self.__move_jogador(jogador_atual, slot_atual, numero_dado)

        if self.__pode_comprar_propriedade_slot(jogador_atual, slot_atual.propriedade):

            if self.__verifica_decisao_jogador(jogador_atual, slot_atual.propriedade):

                slot_atual = self.__efetiva_compra_propriedade(jogador_atual, slot_atual)

                jogador_atual = self.__debita_compra_jogador(jogador_atual, slot_atual.propriedade)

                self.__atualiza_jogador(jogador_atual)

        else:

            jogador_dono = self.__localiza_dono_propriedade(jogador_atual, slot_atual.propriedade)

            if jogador_dono is not None:
                jogador_atual = self.__debita_aluguel_jogador(jogador_atual, slot_atual.propriedade)

                jogador_atual = self.__verifica_se_desativa_jogador(jogador_atual)

                jogador_dono = self.__credita_aluguel_jogador(jogador_dono, slot_atual.propriedade)

                self.__atualiza_jogador(jogador_dono)

            self.__atualiza_jogador(jogador_atual)

        self.__log('')

        return True


    def inicia_partida(self, partida, imprime_log, imprime_resultado):

        rodadas = 0

        self.imprime_log = imprime_log

        self.jogadores = self.__cria_jogadores()

        self.tabuleiro = Tabuleiro().cria_tabuleiro(self.jogadores)

        for r in range(1, 1001):

            rodadas = r

            self.__log(f'Iniciando rodada {r}')

            if self.__executa_jogada() == False:
                break

        self.imprime_log = imprime_resultado

        self.__log('')
        self.__log('------------------------------------------------------')
        self.__log(f'Resultado partida {partida}')
        self.__log('------------------------------------------------------')
        self.__log(f'Jogo finalizado em {rodadas} rodadas')

        jogador_vencedor = self.__retorna_vencedor(self.jogadores)

        self.__log(f'Jogador vencedor {jogador_vencedor.id} perfil {jogador_vencedor.perfil} saldo {jogador_vencedor.saldo}')

        resultado = Resultado(rodadas, jogador_vencedor.perfil, jogador_vencedor.saldo)

        return resultado


def inicia():

    rodadas =[]
    perfils = []

    for p in range(1, 301):

        partida = Partida()

        resultado = partida.inicia_partida(p, False, False)

        rodadas.append(resultado.rodadas)
        perfils.append(resultado.perfil)

        del partida

    data = {"rodadas": rodadas,
            "perfils": perfils}

    df = pd.DataFrame(data)

    print('Estatísticas')

    timeout = df.query( 'rodadas == 1000')
    media_rodadas = int(df["rodadas"].mean())
    perfil_vencedor = df['perfils'].value_counts(ascending=False)
    percentual = (perfil_vencedor / perfil_vencedor.values.sum()) * 100

    print(f'Partidas finalizadas por timeout: {len(timeout)}')
    print(f'Media de rodadas por partida: {media_rodadas}')

    for i in range(0, len(percentual)):
        print(f'{i+1}º lugar: {perfil_vencedor.axes[0][i]} com {perfil_vencedor[i]} vitórias')

    for i in range(0, len(percentual)):
        print(f'Perfil {percentual.axes[0][i]} teve um percentual de vitorias de {percentual[i]}')

inicia()
