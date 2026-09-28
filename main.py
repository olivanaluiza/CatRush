import pygame
import random
import json
import os
import sys


# ============================================================
# CONFIGURAÇÕES
# ============================================================

LARGURA = 1280
ALTURA = 720
FPS = 60

FUNDO = (240, 230, 215)
MARROM = (92, 62, 42)
MARROM_ESCURO = (65, 42, 28)
BRANCO = (255, 255, 255)
PRETO = (25, 25, 25)
VERDE = (75, 170, 90)
VERMELHO = (210, 70, 70)
AMARELO = (235, 190, 60)
CINZA = (180, 180, 180)
CINZA_ESCURO = (110, 110, 110)

TAMANHO_SPRITE = 64

DIRETORIO_ASSETS = "assets"
ARQUIVO_RANKING = "ranking.json"


# ============================================================
# INICIALIZAÇÃO
# ============================================================

pygame.init()

tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("CatRush")

relogio = pygame.time.Clock()


# ============================================================
# FONTES
# ============================================================

fonte_pequena = pygame.font.Font(None, 24)
fonte_media = pygame.font.Font(None, 32)
fonte_grande = pygame.font.Font(None, 48)
fonte_titulo = pygame.font.Font(None, 64)


# ============================================================
# FUNÇÕES
# ============================================================

def carregar_sprite(nome):
    """
    Carrega uma imagem da pasta assets.
    Os sprites originais são 32x32 e são ampliados para 64x64.

    Caso a imagem não seja encontrada, retorna um quadrado vermelho.
    """

    caminho = os.path.join(DIRETORIO_ASSETS, nome)

    try:
        imagem = pygame.image.load(caminho).convert_alpha()
        imagem = pygame.transform.scale(
            imagem,
            (TAMANHO_SPRITE, TAMANHO_SPRITE)
        )
        return imagem

    except (pygame.error, FileNotFoundError):
        print(f"ERRO: não foi possível carregar {caminho}")

        imagem = pygame.Surface(
            (TAMANHO_SPRITE, TAMANHO_SPRITE),
            pygame.SRCALPHA
        )

        imagem.fill((220, 40, 40, 255))

        return imagem


def texto_centralizado(texto, fonte, cor, y):
    superficie = fonte.render(texto, True, cor)

    x = (LARGURA - superficie.get_width()) // 2

    tela.blit(superficie, (x, y))


def desenhar_texto(texto, fonte, cor, x, y):
    superficie = fonte.render(texto, True, cor)
    tela.blit(superficie, (x, y))


def desenhar_barra_tempo(
    x,
    y,
    largura,
    altura,
    tempo,
    tempo_maximo
):
    """
    Desenha a barra de espera do cliente.
    """

    pygame.draw.rect(
        tela,
        CINZA_ESCURO,
        (x, y, largura, altura),
        border_radius=5
    )

    porcentagem = max(
        0,
        min(tempo / tempo_maximo, 1)
    )

    largura_atual = int(
        largura * porcentagem
    )

    if porcentagem > 0.5:
        cor = VERDE

    elif porcentagem > 0.25:
        cor = AMARELO

    else:
        cor = VERMELHO

    if largura_atual > 0:

        pygame.draw.rect(
            tela,
            cor,
            (x, y, largura_atual, altura),
            border_radius=5
        )

    pygame.draw.rect(
        tela,
        PRETO,
        (x, y, largura, altura),
        2,
        border_radius=5
    )


def carregar_ranking():
    """
    Carrega o ranking local do arquivo ranking.json.
    """

    if not os.path.exists(ARQUIVO_RANKING):
        return []

    try:

        with open(
            ARQUIVO_RANKING,
            "r",
            encoding="utf-8"
        ) as arquivo:

            dados = json.load(arquivo)

            if isinstance(dados, list):
                return dados

    except (json.JSONDecodeError, OSError):
        pass

    return []


def salvar_pontuacao(nome, pontuacao):
    """
    Salva a pontuação no ranking local.
    """

    ranking = carregar_ranking()

    ranking.append({
        "nome": nome,
        "pontuacao": pontuacao
    })

    ranking.sort(
        key=lambda jogador: jogador["pontuacao"],
        reverse=True
    )

    ranking = ranking[:10]

    try:

        with open(
            ARQUIVO_RANKING,
            "w",
            encoding="utf-8"
        ) as arquivo:

            json.dump(
                ranking,
                arquivo,
                ensure_ascii=False,
                indent=4
            )

    except OSError:

        print(
            "Não foi possível salvar o ranking."
        )


# ============================================================
# DADOS DAS FRUTAS
# ============================================================

FRUTAS = {

    "morango": {
        "nome": "Morango",
        "arquivo": "morango.png"
    },

    "laranja": {
        "nome": "Laranja",
        "arquivo": "laranja.png"
    },

    "uva": {
        "nome": "Uva",
        "arquivo": "uva.png"
    },

    "maca": {
        "nome": "Maçã",
        "arquivo": "maca.png"
    }
}


# ============================================================
# DADOS DAS FASES
# ============================================================

FASES = [

    {
        "nome": "Aprendiz de Garçom",
        "frutas": ["morango", "laranja"],
        "meta": 30,
        "velocidade": 5,
        "mesas": 2,
        "tempo": 25,
        "parede": False
    },

    {
        "nome": "Corrida das Laranjas",
        "frutas": ["morango", "laranja", "uva"],
        "meta": 80,
        "velocidade": 5.5,
        "mesas": 3,
        "tempo": 22,
        "parede": False
    },

    {
        "nome": "Salada de Frutas",
        "frutas": ["morango", "laranja", "uva"],
        "meta": 150,
        "velocidade": 6,
        "mesas": 3,
        "tempo": 19,
        "parede": True
    },

    {
        "nome": "Hora do Rush",
        "frutas": ["morango", "laranja", "uva", "maca"],
        "meta": 240,
        "velocidade": 6.5,
        "mesas": 4,
        "tempo": 15,
        "parede": False
    },

    {
        "nome": "Grande Banquete do Gato",
        "frutas": ["morango", "laranja", "uva", "maca"],
        "meta": 350,
        "velocidade": 7,
        "mesas": 4,
        "tempo": 12,
        "parede": True
    }
]


# ============================================================
# CLIENTES
# ============================================================

CLIENTES = [
    "cachorro.png",
    "pato.png",
    "galinha.png",
    "lhama.png"
]


# ============================================================
# SPRITES
# ============================================================

sprites = {}

arquivos_sprites = [

    # Gato
    "gato_parado.png",
    "gato_frente.png",
    "gato_costas.png",
    "gato_esquerda.png",
    "gato_direita.png",

    # Cenário
    "balcao.png",
    "mesa.png",

    # Frutas
    "morango.png",
    "laranja.png",
    "uva.png",
    "maca.png",

    # Clientes
    "cachorro.png",
    "pato.png",
    "galinha.png",
    "lhama.png"
]

for arquivo in arquivos_sprites:

    sprites[arquivo] = carregar_sprite(arquivo)


# ============================================================
# POSIÇÕES
# ============================================================

POSICOES_BALCOES = [
    (70, 100),
    (70, 230),
    (70, 360),
    (200, 100)
]


# ============================================================
# MESAS
# ============================================================
# A tela agora é 1280x720, então as mesas ficam
# mais espalhadas para deixar espaço para:
# cliente + balão + mesa + barra de tempo.

POSICOES_MESAS = [
    (850, 190),
    (850, 370),
    (540, 500),
    (1000, 500)
]


# ============================================================
# CLASSE JOGADOR
# ============================================================

class Jogador:

    def __init__(self):

        self.rect = pygame.Rect(
            400,
            250,
            TAMANHO_SPRITE,
            TAMANHO_SPRITE
        )

        self.direcao = "parado"

        self.item_na_mao = None

    def mover(self, velocidade, paredes):

        teclas = pygame.key.get_pressed()

        dx = 0
        dy = 0

        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:

            dx -= velocidade
            self.direcao = "esquerda"

        elif teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:

            dx += velocidade
            self.direcao = "direita"

        if teclas[pygame.K_w] or teclas[pygame.K_UP]:

            dy -= velocidade
            self.direcao = "costas"

        elif teclas[pygame.K_s] or teclas[pygame.K_DOWN]:

            dy += velocidade
            self.direcao = "frente"

        if dx == 0 and dy == 0:

            self.direcao = "parado"

        # Movimento horizontal
        self.rect.x += int(dx)

        for parede in paredes:

            if self.rect.colliderect(parede):

                if dx > 0:
                    self.rect.right = parede.left

                elif dx < 0:
                    self.rect.left = parede.right

        # Movimento vertical
        self.rect.y += int(dy)

        for parede in paredes:

            if self.rect.colliderect(parede):

                if dy > 0:
                    self.rect.bottom = parede.top

                elif dy < 0:
                    self.rect.top = parede.bottom

        # Limites da tela
        self.rect.left = max(
            self.rect.left,
            0
        )

        self.rect.right = min(
            self.rect.right,
            LARGURA
        )

        self.rect.top = max(
            self.rect.top,
            70
        )

        self.rect.bottom = min(
            self.rect.bottom,
            ALTURA
        )

    def desenhar(self):

        if self.direcao == "frente":

            imagem = sprites[
                "gato_frente.png"
            ]

        elif self.direcao == "costas":

            imagem = sprites[
                "gato_costas.png"
            ]

        elif self.direcao == "esquerda":

            imagem = sprites[
                "gato_esquerda.png"
            ]

        elif self.direcao == "direita":

            imagem = sprites[
                "gato_direita.png"
            ]

        else:

            imagem = sprites[
                "gato_parado.png"
            ]

        tela.blit(
            imagem,
            self.rect
        )

        # ====================================================
        # FRUTA NA MÃO
        # ====================================================

        if self.item_na_mao is not None:

            fruta = sprites[
                FRUTAS[
                    self.item_na_mao
                ]["arquivo"]
            ]

            largura_item = fruta.get_width()
            altura_item = fruta.get_height()

            x_item = (
                self.rect.centerx
                - largura_item // 2
            )

            # Mantido como estava funcionando.
            y_item = self.rect.top - 32

            tela.blit(
                fruta,
                (x_item, y_item)
            )


# ============================================================
# CLASSE BALCÃO
# ============================================================

class Balcao:

    def __init__(self, x, y, item):

        self.rect = pygame.Rect(
            x,
            y,
            TAMANHO_SPRITE,
            TAMANHO_SPRITE
        )

        self.item = item

    def desenhar(self):

        tela.blit(
            sprites["balcao.png"],
            self.rect
        )

        fruta = sprites[
            FRUTAS[
                self.item
            ]["arquivo"]
        ]

        x = (
            self.rect.centerx
            - fruta.get_width() // 2
        )

        y = self.rect.top - 50

        tela.blit(
            fruta,
            (x, y)
        )

        nome = FRUTAS[
            self.item
        ]["nome"]

        superficie = fonte_pequena.render(
            nome,
            True,
            MARROM_ESCURO
        )

        x_texto = (
            self.rect.centerx
            - superficie.get_width() // 2
        )

        tela.blit(
            superficie,
            (
                x_texto,
                self.rect.bottom + 5
            )
        )


# ============================================================
# CLASSE MESA
# ============================================================

class Mesa:

    def __init__(
        self,
        x,
        y,
        cliente,
        pedido,
        tempo_maximo
    ):

        self.rect = pygame.Rect(
            x,
            y,
            TAMANHO_SPRITE,
            TAMANHO_SPRITE
        )

        self.cliente = cliente
        self.pedido = pedido

        self.tempo_maximo = tempo_maximo
        self.tempo = tempo_maximo

        self.insatisfeito = False

        self.pedido_alterado = False

    def novo_pedido(self, frutas):

        self.pedido = random.choice(frutas)

        self.tempo = self.tempo_maximo

        self.insatisfeito = False

        self.pedido_alterado = False

    def atualizar(self, dt, fase):

        self.tempo -= dt

        # ====================================================
        # PEDIDOS DINÂMICOS DA FASE 5
        # ====================================================

        if fase == 5:

            if (
                self.tempo <= 5
                and not self.pedido_alterado
            ):

                opcoes = [
                    fruta
                    for fruta in jogo.frutas_atuais
                    if fruta != self.pedido
                ]

                if opcoes:

                    self.pedido = random.choice(
                        opcoes
                    )

                self.pedido_alterado = True

        # ====================================================
        # PEDIDO EXPIRADO
        # ====================================================

        if self.tempo <= 0:

            self.tempo = 0

            if not self.insatisfeito:

                self.insatisfeito = True

                return True

        return False

    def desenhar(self):

        # ----------------------------------------------------
        # CLIENTE
        # ----------------------------------------------------

        cliente_x = (
            self.rect.centerx
            - TAMANHO_SPRITE // 2
        )

        cliente_y = self.rect.top - 70

        tela.blit(
            sprites[self.cliente],
            (cliente_x, cliente_y)
        )

        # ----------------------------------------------------
        # BALÃO DE PENSAMENTO
        # ----------------------------------------------------

        # Maior para facilitar a visualização
        # na nova resolução.

        balao = pygame.Rect(
            self.rect.centerx - 45,
            cliente_y - 55,
            90,
            55
        )

        pygame.draw.rect(
            tela,
            BRANCO,
            balao,
            border_radius=12
        )

        pygame.draw.rect(
            tela,
            MARROM_ESCURO,
            balao,
            2,
            border_radius=12
        )

        # Pequenas bolinhas do balão
        pygame.draw.circle(
            tela,
            BRANCO,
            (
                self.rect.centerx - 30,
                cliente_y - 8
            ),
            6
        )

        pygame.draw.circle(
            tela,
            MARROM_ESCURO,
            (
                self.rect.centerx - 30,
                cliente_y - 8
            ),
            1
        )

        # ----------------------------------------------------
        # FRUTA PEDIDA
        # ----------------------------------------------------

        fruta = sprites[
            FRUTAS[
                self.pedido
            ]["arquivo"]
        ]

        fruta_pequena = pygame.transform.scale(
            fruta,
            (40, 40)
        )

        x_fruta = (
            balao.centerx
            - fruta_pequena.get_width() // 2
        )

        y_fruta = (
            balao.centery
            - fruta_pequena.get_height() // 2
        )

        tela.blit(
            fruta_pequena,
            (x_fruta, y_fruta)
        )

        # ----------------------------------------------------
        # MESA
        # ----------------------------------------------------

        tela.blit(
            sprites["mesa.png"],
            self.rect
        )

        # ----------------------------------------------------
        # BARRA DE TEMPO
        # ----------------------------------------------------

        barra_x = (
            self.rect.centerx - 45
        )

        barra_y = (
            self.rect.bottom + 12
        )

        desenhar_barra_tempo(
            barra_x,
            barra_y,
            90,
            10,
            self.tempo,
            self.tempo_maximo
        )


# ============================================================
# CLASSE PRINCIPAL DO JOGO
# ============================================================

class CatRush:

    def __init__(self):

        self.estado = "nome"

        self.nome_jogador = ""

        self.fase = 1

        self.pontuacao = 0

        self.clientes_insatisfeitos = 0

        self.jogador = Jogador()

        self.balcoes = []

        self.mesas = []

        self.paredes = []

        self.frutas_atuais = []

        self.ranking = []

        self.pontuacao_salva = False

        self.criar_fase()

    # ========================================================
    # CRIAR FASE
    # ========================================================

    def criar_fase(self):

        dados = FASES[
            self.fase - 1
        ]

        self.frutas_atuais = dados["frutas"]

        self.balcoes = []

        self.mesas = []

        self.paredes = []

        self.clientes_insatisfeitos = 0

        self.jogador.item_na_mao = None

        # ----------------------------------------------------
        # BALCÕES
        # ----------------------------------------------------

        for i, item in enumerate(
            self.frutas_atuais
        ):

            if i >= len(
                POSICOES_BALCOES
            ):
                break

            x, y = POSICOES_BALCOES[i]

            self.balcoes.append(
                Balcao(
                    x,
                    y,
                    item
                )
            )

        # ----------------------------------------------------
        # MESAS
        # ----------------------------------------------------

        clientes_disponiveis = CLIENTES.copy()

        random.shuffle(
            clientes_disponiveis
        )

        for i in range(
            dados["mesas"]
        ):

            x, y = POSICOES_MESAS[i]

            cliente = clientes_disponiveis[
                i % len(clientes_disponiveis)
            ]

            pedido = random.choice(
                self.frutas_atuais
            )

            mesa = Mesa(
                x,
                y,
                cliente,
                pedido,
                dados["tempo"]
            )

            self.mesas.append(
                mesa
            )

        # ----------------------------------------------------
        # PAREDE CENTRAL
        # ----------------------------------------------------

        if dados["parede"]:

            parede = pygame.Rect(
                650,
                210,
                70,
                230
            )

            self.paredes.append(
                parede
            )

    # ========================================================
    # INICIAR JOGO
    # ========================================================

    def iniciar(self):

        self.fase = 1

        self.pontuacao = 0

        self.clientes_insatisfeitos = 0

        self.pontuacao_salva = False

        self.jogador.rect.x = 400
        self.jogador.rect.y = 250

        self.jogador.item_na_mao = None

        self.criar_fase()

        self.estado = "jogando"

    # ========================================================
    # ATUALIZAR
    # ========================================================

    def atualizar(self, dt):

        if self.estado != "jogando":
            return

        dados = FASES[
            self.fase - 1
        ]

        # ----------------------------------------------------
        # MOVIMENTO
        # ----------------------------------------------------

        self.jogador.mover(
            dados["velocidade"],
            self.paredes
        )

        # ----------------------------------------------------
        # PEGAR FRUTA
        # ----------------------------------------------------

        for balcao in self.balcoes:

            if self.jogador.rect.colliderect(
                balcao.rect
            ):

                if (
                    self.jogador.item_na_mao
                    != balcao.item
                ):

                    self.jogador.item_na_mao = (
                        balcao.item
                    )

        # ----------------------------------------------------
        # ENTREGAR FRUTA
        # ----------------------------------------------------

        for mesa in self.mesas:

            if self.jogador.rect.colliderect(
                mesa.rect
            ):

                if (
                    self.jogador.item_na_mao
                    is not None
                    and not mesa.insatisfeito
                ):

                    if (
                        self.jogador.item_na_mao
                        == mesa.pedido
                    ):

                        self.pontuacao += 10

                        self.jogador.item_na_mao = None

                        mesa.novo_pedido(
                            self.frutas_atuais
                        )

                    else:

                        pass

        # ----------------------------------------------------
        # TEMPO DAS MESAS
        # ----------------------------------------------------

        for mesa in self.mesas:

            expirou = mesa.atualizar(
                dt,
                self.fase
            )

            if expirou:

                self.pontuacao -= 5

                self.clientes_insatisfeitos += 1

                mesa.cliente = random.choice(
                    CLIENTES
                )

                mesa.novo_pedido(
                    self.frutas_atuais
                )

        # ----------------------------------------------------
        # GAME OVER
        # ----------------------------------------------------

        if self.clientes_insatisfeitos >= 3:

            self.estado = "game_over"

            self.salvar_resultado()

            return

        # ----------------------------------------------------
        # GAME OVER POR PONTUAÇÃO NEGATIVA
        # ----------------------------------------------------

        if self.pontuacao < 0:

            self.estado = "game_over"

            self.salvar_resultado()

            return

        # ----------------------------------------------------
        # PASSAR DE FASE
        # ----------------------------------------------------

        if self.pontuacao >= dados["meta"]:

            if self.fase < 5:

                self.fase += 1

                self.criar_fase()

            else:

                self.estado = "vitoria"

                self.salvar_resultado()

    # ========================================================
    # SALVAR RESULTADO
    # ========================================================

    def salvar_resultado(self):

        if self.pontuacao_salva:
            return

        nome = self.nome_jogador.strip()

        if nome == "":
            nome = "Jogador"

        salvar_pontuacao(
            nome,
            self.pontuacao
        )

        self.pontuacao_salva = True

    # ========================================================
    # DESENHAR CENÁRIO
    # ========================================================

    def desenhar_cenario(self):

        tela.fill(FUNDO)

        # ----------------------------------------------------
        # CHÃO
        # ----------------------------------------------------

        pygame.draw.rect(
            tela,
            (225, 210, 190),
            (
                0,
                70,
                LARGURA,
                ALTURA - 70
            )
        )

        # ----------------------------------------------------
        # PAREDES
        # ----------------------------------------------------

        for parede in self.paredes:

            pygame.draw.rect(
                tela,
                MARROM,
                parede,
                border_radius=6
            )

            pygame.draw.rect(
                tela,
                MARROM_ESCURO,
                parede,
                3,
                border_radius=6
            )

    # ========================================================
    # HUD
    # ========================================================

    def desenhar_hud(self):

        dados = FASES[
            self.fase - 1
        ]

        pygame.draw.rect(
            tela,
            MARROM_ESCURO,
            (0, 0, LARGURA, 70)
        )

        desenhar_texto(
            f"FASE {self.fase}/5",
            fonte_media,
            BRANCO,
            20,
            10
        )

        desenhar_texto(
            dados["nome"],
            fonte_media,
            BRANCO,
            20,
            40
        )

        texto_pontos = (
            f"Pontos: "
            f"{self.pontuacao}/"
            f"{dados['meta']}"
        )

        superficie = fonte_media.render(
            texto_pontos,
            True,
            BRANCO
        )

        tela.blit(
            superficie,
            (
                LARGURA
                - superficie.get_width()
                - 20,
                15
            )
        )

        texto_insatisfeitos = (
            f"Clientes insatisfeitos: "
            f"{self.clientes_insatisfeitos}/3"
        )

        superficie = fonte_pequena.render(
            texto_insatisfeitos,
            True,
            BRANCO
        )

        tela.blit(
            superficie,
            (
                LARGURA
                - superficie.get_width()
                - 20,
                45
            )
        )

    # ========================================================
    # DESENHAR JOGO
    # ========================================================

    def desenhar_jogo(self):

        self.desenhar_cenario()

        for balcao in self.balcoes:
            balcao.desenhar()

        for mesa in self.mesas:
            mesa.desenhar()

        self.jogador.desenhar()

        self.desenhar_hud()

    # ========================================================
    # TELA DE NOME
    # ========================================================

    def desenhar_nome(self):

        tela.fill(FUNDO)

        texto_centralizado(
            "CatRush",
            fonte_titulo,
            MARROM_ESCURO,
            100
        )

        texto_centralizado(
            "Digite seu nome:",
            fonte_grande,
            MARROM,
            200
        )

        caixa = pygame.Rect(
            LARGURA // 2 - 212,
            270,
            424,
            55
        )

        pygame.draw.rect(
            tela,
            BRANCO,
            caixa,
            border_radius=8
        )

        pygame.draw.rect(
            tela,
            MARROM_ESCURO,
            caixa,
            3,
            border_radius=8
        )

        texto = self.nome_jogador

        superficie = fonte_media.render(
            texto,
            True,
            PRETO
        )

        tela.blit(
            superficie,
            (
                caixa.x + 15,
                caixa.y + 13
            )
        )

        texto_centralizado(
            "ENTER para começar",
            fonte_media,
            MARROM,
            370
        )

        texto_centralizado(
            "ESC para sair",
            fonte_pequena,
            CINZA_ESCURO,
            415
        )

    # ========================================================
    # TELA DE VITÓRIA
    # ========================================================

    def desenhar_vitoria(self):

        tela.fill(FUNDO)

        texto_centralizado(
            "VITÓRIA!",
            fonte_titulo,
            VERDE,
            100
        )

        texto_centralizado(
            "Você completou as 5 fases!",
            fonte_grande,
            MARROM_ESCURO,
            190
        )

        texto_centralizado(
            f"Pontuação final: {self.pontuacao}",
            fonte_grande,
            MARROM,
            260
        )

        texto_centralizado(
            "R - Ver ranking",
            fonte_media,
            MARROM_ESCURO,
            350
        )

        texto_centralizado(
            "ENTER - Jogar novamente",
            fonte_media,
            MARROM_ESCURO,
            390
        )

        texto_centralizado(
            "ESC - Sair",
            fonte_pequena,
            CINZA_ESCURO,
            440
        )

    # ========================================================
    # TELA DE GAME OVER
    # ========================================================

    def desenhar_game_over(self):

        tela.fill(FUNDO)

        texto_centralizado(
            "GAME OVER",
            fonte_titulo,
            VERMELHO,
            100
        )

        texto_centralizado(
            "Os clientes ficaram insatisfeitos.",
            fonte_grande,
            MARROM_ESCURO,
            190
        )

        texto_centralizado(
            f"Pontuação: {self.pontuacao}",
            fonte_grande,
            MARROM,
            260
        )

        texto_centralizado(
            "R - Ver ranking",
            fonte_media,
            MARROM_ESCURO,
            350
        )

        texto_centralizado(
            "ENTER - Tentar novamente",
            fonte_media,
            MARROM_ESCURO,
            390
        )

        texto_centralizado(
            "ESC - Sair",
            fonte_pequena,
            CINZA_ESCURO,
            440
        )

    # ========================================================
    # TELA DE RANKING
    # ========================================================

    def desenhar_ranking(self):

        tela.fill(FUNDO)

        texto_centralizado(
            "RANKING GERAL",
            fonte_titulo,
            MARROM_ESCURO,
            50
        )

        ranking = carregar_ranking()

        if not ranking:

            texto_centralizado(
                "Nenhuma pontuação registrada.",
                fonte_media,
                MARROM,
                180
            )

        else:

            y = 140

            for i, jogador in enumerate(
                ranking[:10]
            ):

                posicao = f"{i + 1}º"

                nome = jogador.get(
                    "nome",
                    "Jogador"
                )

                pontuacao = jogador.get(
                    "pontuacao",
                    0
                )

                texto = (
                    f"{posicao:<4} "
                    f"{nome:<20} "
                    f"{pontuacao} pontos"
                )

                desenhar_texto(
                    texto,
                    fonte_media,
                    MARROM_ESCURO,
                    250,
                    y
                )

                y += 35

        texto_centralizado(
            "ENTER - Jogar novamente",
            fonte_media,
            MARROM,
            480
        )

        texto_centralizado(
            "ESC - Sair",
            fonte_pequena,
            CINZA_ESCURO,
            520
        )


# ============================================================
# CRIAR JOGO
# ============================================================

jogo = CatRush()


# ============================================================
# LOOP PRINCIPAL
# ============================================================

executando = True

while executando:

    dt = relogio.tick(FPS) / 1000

    # ========================================================
    # EVENTOS
    # ========================================================

    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:

            executando = False

        # ----------------------------------------------------
        # DIGITAÇÃO DO NOME
        # ----------------------------------------------------

        if jogo.estado == "nome":

            if evento.type == pygame.KEYDOWN:

                if evento.key == pygame.K_ESCAPE:

                    executando = False

                elif evento.key == pygame.K_RETURN:

                    jogo.iniciar()

                elif evento.key == pygame.K_BACKSPACE:

                    jogo.nome_jogador = (
                        jogo.nome_jogador[:-1]
                    )

                else:

                    if len(
                        jogo.nome_jogador
                    ) < 18:

                        if evento.unicode.isprintable():

                            jogo.nome_jogador += (
                                evento.unicode
                            )

        # ----------------------------------------------------
        # VITÓRIA
        # ----------------------------------------------------

        elif jogo.estado == "vitoria":

            if evento.type == pygame.KEYDOWN:

                if evento.key == pygame.K_ESCAPE:

                    executando = False

                elif evento.key == pygame.K_RETURN:

                    jogo.iniciar()

                elif evento.key == pygame.K_r:

                    jogo.estado = "ranking"

        # ----------------------------------------------------
        # GAME OVER
        # ----------------------------------------------------

        elif jogo.estado == "game_over":

            if evento.type == pygame.KEYDOWN:

                if evento.key == pygame.K_ESCAPE:

                    executando = False

                elif evento.key == pygame.K_RETURN:

                    jogo.iniciar()

                elif evento.key == pygame.K_r:

                    jogo.estado = "ranking"

        # ----------------------------------------------------
        # RANKING
        # ----------------------------------------------------

        elif jogo.estado == "ranking":

            if evento.type == pygame.KEYDOWN:

                if evento.key == pygame.K_ESCAPE:

                    executando = False

                elif evento.key == pygame.K_RETURN:

                    jogo.iniciar()

    # ========================================================
    # ATUALIZAÇÃO
    # ========================================================

    jogo.atualizar(dt)

    # ========================================================
    # DESENHO
    # ========================================================

    if jogo.estado == "nome":

        jogo.desenhar_nome()

    elif jogo.estado == "jogando":

        jogo.desenhar_jogo()

    elif jogo.estado == "vitoria":

        jogo.desenhar_vitoria()

    elif jogo.estado == "game_over":

        jogo.desenhar_game_over()

    elif jogo.estado == "ranking":

        jogo.desenhar_ranking()

    pygame.display.flip()


# ============================================================
# ENCERRAR
# ============================================================

pygame.quit()
sys.exit()