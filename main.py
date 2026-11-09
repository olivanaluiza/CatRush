import pygame
import random
import json
import os
import sys

LARGURA = 1280
ALTURA = 720
FPS = 60

FUNDO = (250, 244, 235)
FUNDO_JOGO = (241, 228, 208)
CREME = (255, 250, 242)
BRANCO = (255, 255, 255)
PRETO = (42, 35, 31)
MARROM = (116, 74, 49)
MARROM_ESCURO = (62, 41, 31)
VERDE = (92, 177, 115)
VERDE_ESCURO = (57, 128, 79)
VERDE_CLARO = (219, 239, 221)
ROSA = (226, 126, 145)
ROSA_CLARO = (250, 218, 223)
PESSEGO = (245, 190, 149)
AMARELO = (239, 190, 79)
VERMELHO = (208, 83, 83)
BEGE = (229, 207, 180)
BEGE_ESCURO = (205, 181, 150)
SOMBRA = (190, 166, 140)
CINZA = (145, 137, 130)

TAMANHO_SPRITE = 112
DIRETORIO_ASSETS = "assets"
ARQUIVO_RANKING = "ranking.json"

pygame.init()
info_tela = pygame.display.Info()
LARGURA = info_tela.current_w
ALTURA = info_tela.current_h
tela = pygame.display.set_mode((LARGURA, ALTURA), pygame.FULLSCREEN)
pygame.display.set_caption("CatRush")
relogio = pygame.time.Clock()

fonte_pequena = pygame.font.Font(None, 24)
fonte_media = pygame.font.Font(None, 30)
fonte_grande = pygame.font.Font(None, 46)
fonte_titulo = pygame.font.Font(None, 72)
fonte_logo = pygame.font.Font(None, 94)
fonte_botao = pygame.font.Font(None, 34)
fonte_numero = pygame.font.Font(None, 58)


def carregar_sprite(nome):
    caminho = os.path.join(DIRETORIO_ASSETS, nome)
    try:
        imagem = pygame.image.load(caminho).convert_alpha()
        return pygame.transform.scale(imagem, (TAMANHO_SPRITE, TAMANHO_SPRITE))
    except (pygame.error, FileNotFoundError):
        imagem = pygame.Surface((TAMANHO_SPRITE, TAMANHO_SPRITE), pygame.SRCALPHA)
        pygame.draw.rect(imagem, VERMELHO, (0, 0, TAMANHO_SPRITE, TAMANHO_SPRITE), border_radius=12)
        return imagem


def desenhar_texto(texto, fonte, cor, x, y):
    tela.blit(fonte.render(texto, True, cor), (x, y))


def texto_centralizado(texto, fonte, cor, y):
    superficie = fonte.render(texto, True, cor)
    tela.blit(superficie, ((LARGURA - superficie.get_width()) // 2, y))


def desenhar_painel(rect, cor=CREME, borda=BEGE_ESCURO, raio=18, largura_borda=2):
    sombra = pygame.Rect(rect.x, rect.y + 6, rect.width, rect.height)
    pygame.draw.rect(tela, SOMBRA, sombra, border_radius=raio)
    pygame.draw.rect(tela, cor, rect, border_radius=raio)
    if largura_borda:
        pygame.draw.rect(tela, borda, rect, largura_borda, border_radius=raio)


def desenhar_botao(rect, texto, mouse_pos, largura=2):
    hover = rect.collidepoint(mouse_pos)
    y = rect.y - 2 if hover else rect.y
    atual = pygame.Rect(rect.x, y, rect.width, rect.height)
    sombra = pygame.Rect(atual.x, atual.y + 7, atual.width, atual.height)
    pygame.draw.rect(tela, SOMBRA, sombra, border_radius=16)
    pygame.draw.rect(tela, VERDE_ESCURO if hover else VERDE, atual, border_radius=16)
    pygame.draw.rect(tela, MARROM_ESCURO, atual, largura, border_radius=16)
    superficie = fonte_botao.render(texto, True, BRANCO)
    tela.blit(superficie, (atual.centerx - superficie.get_width() // 2, atual.centery - superficie.get_height() // 2))


def desenhar_barra_tempo(x, y, largura, altura, tempo, tempo_maximo):
    pygame.draw.rect(tela, (122, 105, 90), (x, y, largura, altura), border_radius=6)
    porcentagem = max(0, min(tempo / tempo_maximo, 1))
    largura_atual = int(largura * porcentagem)
    cor = VERDE if porcentagem > 0.5 else AMARELO if porcentagem > 0.25 else VERMELHO
    if largura_atual > 0:
        pygame.draw.rect(tela, cor, (x, y, largura_atual, altura), border_radius=6)
    pygame.draw.rect(tela, MARROM_ESCURO, (x, y, largura, altura), 2, border_radius=6)


def carregar_ranking():
    if not os.path.exists(ARQUIVO_RANKING):
        return []
    try:
        with open(ARQUIVO_RANKING, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
            return dados if isinstance(dados, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def salvar_pontuacao(nome, pontuacao):
    ranking = carregar_ranking()
    ranking.append({"nome": nome, "pontuacao": pontuacao})
    ranking.sort(key=lambda jogador: jogador.get("pontuacao", 0), reverse=True)
    try:
        with open(ARQUIVO_RANKING, "w", encoding="utf-8") as arquivo:
            json.dump(ranking[:10], arquivo, ensure_ascii=False, indent=4)
    except OSError:
        pass


FRUTAS = {
    "morango": {"nome": "Morango", "arquivo": "morango.png"},
    "laranja": {"nome": "Laranja", "arquivo": "laranja.png"},
    "uva": {"nome": "Uva", "arquivo": "uva.png"},
    "maca": {"nome": "Maçã", "arquivo": "maca.png"}
}

FASES = [
    {"nome": "Aprendiz de Garçom", "frutas": ["morango", "laranja"], "meta": 30, "velocidade": 7, "mesas": 2, "tempo": 37, "parede": False, "urgentes": 0},
    {"nome": "Corrida das Laranjas", "frutas": ["morango", "laranja", "uva"], "meta": 80, "velocidade": 7.5, "mesas": 3, "tempo": 36, "parede": False, "urgentes": 0},
    {"nome": "Salada de Frutas", "frutas": ["morango", "laranja", "uva"], "meta": 150, "velocidade": 8, "mesas": 3, "tempo": 35, "parede": True, "urgentes": 0},
    {"nome": "Hora do Rush", "frutas": ["morango", "laranja", "uva", "maca"], "meta": 240, "velocidade": 8.5, "mesas": 4, "tempo": 34, "parede": True, "urgentes": 1},
    {"nome": "Grande Banquete do Gato", "frutas": ["morango", "laranja", "uva", "maca"], "meta": 350, "velocidade": 9, "mesas": 4, "tempo": 33, "parede": True, "urgentes": 2},
    {"nome": "Festival das Frutas", "frutas": ["morango", "laranja", "uva", "maca"], "meta": 430, "velocidade": 9.5, "mesas": 4, "tempo": 32, "parede": True, "urgentes": 2, "descricao": "Dois clientes precisam ser atendidos com prioridade."},
    {"nome": "Desafio do Café", "frutas": ["morango", "laranja", "uva", "maca"], "meta": 520, "velocidade": 10, "mesas": 4, "tempo": 31, "parede": True, "urgentes": 2, "descricao": "Dois clientes precisam ser atendidos com prioridade."},
    {"nome": "Último Pedido", "frutas": ["morango", "laranja", "uva", "maca"], "meta": 620, "velocidade": 10.5, "mesas": 4, "tempo": 30, "parede": True, "urgentes": 3, "descricao": "Três clientes precisam ser atendidos com prioridade."}
]

CLIENTES = ["cachorro.png", "pato.png", "galinha.png", "lhama.png"]

sprites = {}
for arquivo in [
    "gato_parado.png", "gato_frente.png", "gato_costas.png", "gato_esquerda.png", "gato_direita.png",
    "balcao.png", "mesa.png", "morango.png", "laranja.png", "uva.png", "maca.png",
    "cachorro.png", "pato.png", "galinha.png", "lhama.png"
]:
    sprites[arquivo] = carregar_sprite(arquivo)


def gerar_posicoes_frutas(quantidade):
    x = 105
    inicio = 195
    fim = ALTURA - 165
    if quantidade == 1:
        return [(x, (inicio + fim) // 2)]
    passo = (fim - inicio) / (quantidade - 1)
    return [(x, int(inicio + i * passo)) for i in range(quantidade)]


def gerar_posicoes_mesas(quantidade):
    x_esquerda = LARGURA - 350
    x_direita = LARGURA - 190
    y_superior = max(230, ALTURA // 2 - 130)
    y_inferior = ALTURA - 220
    posicoes = [
        (x_esquerda, y_superior),
        (x_direita, y_superior),
        (x_esquerda, y_inferior),
        (x_direita, y_inferior)
    ]
    if quantidade == 3:
        posicoes[2] = (LARGURA - 270, y_inferior)
    return posicoes[:quantidade]


class Jogador:
    def __init__(self):
        self.rect = pygame.Rect(LARGURA // 2 - TAMANHO_SPRITE // 2, ALTURA // 2 - TAMANHO_SPRITE // 2, TAMANHO_SPRITE, TAMANHO_SPRITE)
        self.direcao = "parado"
        self.item_na_mao = None

    def mover(self, velocidade, paredes):
        teclas = pygame.key.get_pressed()
        dx = dy = 0
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

        self.rect.x += int(dx)
        for parede in paredes:
            if self.rect.colliderect(parede):
                if dx > 0:
                    self.rect.right = parede.left
                elif dx < 0:
                    self.rect.left = parede.right

        self.rect.y += int(dy)
        for parede in paredes:
            if self.rect.colliderect(parede):
                if dy > 0:
                    self.rect.bottom = parede.top
                elif dy < 0:
                    self.rect.top = parede.bottom

        self.rect.left = max(self.rect.left, 30)
        self.rect.right = min(self.rect.right, LARGURA - 30)
        self.rect.top = max(self.rect.top, 92)
        self.rect.bottom = min(self.rect.bottom, ALTURA - 35)

    def desenhar(self):
        tela.blit(sprites[f"gato_{self.direcao}.png"], self.rect)
        if self.item_na_mao is not None:
            fruta = sprites[FRUTAS[self.item_na_mao]["arquivo"]]
            tela.blit(fruta, (self.rect.centerx - fruta.get_width() // 2, self.rect.top - fruta.get_height() + 12))


class Balcao:
    def __init__(self, x, y, item):
        self.rect = pygame.Rect(x, y, TAMANHO_SPRITE, TAMANHO_SPRITE)
        self.item = item

    def desenhar(self):
        pygame.draw.rect(tela, SOMBRA, (self.rect.x, self.rect.y + 7, TAMANHO_SPRITE, TAMANHO_SPRITE), border_radius=12)
        tela.blit(sprites["balcao.png"], self.rect)
        fruta = sprites[FRUTAS[self.item]["arquivo"]]
        tela.blit(fruta, (self.rect.centerx - fruta.get_width() // 2, self.rect.top - fruta.get_height() + 8))
        nome = fonte_pequena.render(FRUTAS[self.item]["nome"], True, MARROM_ESCURO)
        tela.blit(nome, (self.rect.centerx - nome.get_width() // 2, self.rect.bottom + 7))


class Mesa:
    def __init__(self, x, y, cliente, pedido, tempo_maximo, urgente=False):
        self.rect = pygame.Rect(x, y, TAMANHO_SPRITE, TAMANHO_SPRITE)
        self.cliente = cliente
        self.pedido = pedido
        self.urgente = urgente
        self.tempo_maximo = tempo_maximo * 0.90 if urgente else tempo_maximo
        self.tempo = self.tempo_maximo
        self.insatisfeito = False

    def novo_pedido(self, frutas):
        # Um novo pedido só é sorteado quando um novo cliente ocupa a mesa.
        self.pedido = random.choice(frutas)
        self.tempo = self.tempo_maximo
        self.insatisfeito = False

    def atualizar(self, dt):
        # O pedido permanece o mesmo durante todo o atendimento.
        self.tempo -= dt
        if self.tempo <= 0:
            self.tempo = 0
            if not self.insatisfeito:
                self.insatisfeito = True
                return True
        return False

    def desenhar(self):
        cliente_x = self.rect.centerx - TAMANHO_SPRITE // 2
        cliente_y = self.rect.top - 82
        tela.blit(sprites[self.cliente], (cliente_x, cliente_y))

        balao = pygame.Rect(self.rect.centerx - 60, cliente_y - 56, 120, 62)
        pygame.draw.rect(tela, BRANCO, balao, border_radius=13)
        pygame.draw.rect(tela, MARROM_ESCURO, balao, 2, border_radius=13)
        pygame.draw.circle(tela, BRANCO, (self.rect.centerx - 40, cliente_y - 7), 8)
        pygame.draw.circle(tela, MARROM_ESCURO, (self.rect.centerx - 40, cliente_y - 7), 1)

        fruta = pygame.transform.scale(sprites[FRUTAS[self.pedido]["arquivo"]], (52, 52))
        tela.blit(fruta, (balao.centerx - 26, balao.centery - 26))

        pygame.draw.rect(tela, SOMBRA, (self.rect.x, self.rect.y + 7, TAMANHO_SPRITE, TAMANHO_SPRITE), border_radius=12)
        tela.blit(sprites["mesa.png"], self.rect)
        barra_x = self.rect.centerx - 60
        barra_y = self.rect.bottom + 15
        desenhar_barra_tempo(barra_x, barra_y, 120, 12, self.tempo, self.tempo_maximo)
        if self.urgente:
            pygame.draw.rect(tela, VERMELHO, (barra_x - 3, barra_y - 3, 126, 18), 2, border_radius=6)
            aviso = fonte_pequena.render("URGENTE", True, VERMELHO)
            tela.blit(aviso, (self.rect.centerx - aviso.get_width() // 2, barra_y + 17))


class CatRush:
    def __init__(self):
        self.estado = "inicio"
        self.nome_jogador = ""
        self.fase = 1
        self.pontuacao = 0
        self.clientes_insatisfeitos = 0
        self.jogador = Jogador()
        self.balcoes = []
        self.mesas = []
        self.paredes = []
        self.frutas_atuais = []
        self.pontuacao_salva = False
        self.botao_continuar = pygame.Rect(LARGURA // 2 - 190, 510, 380, 64)
        self.botao_iniciar = pygame.Rect(LARGURA // 2 - 180, ALTURA // 2 + 70, 360, 62)
        self.botao_ranking = pygame.Rect(LARGURA // 2 - 180, ALTURA // 2 + 148, 360, 62)
        self.criar_fase()

    def criar_fase(self):
        dados = FASES[self.fase - 1]
        self.frutas_atuais = dados["frutas"]
        self.balcoes = []
        self.mesas = []
        self.paredes = []
        self.clientes_insatisfeitos = 0
        self.jogador.item_na_mao = None

        posicoes = gerar_posicoes_frutas(len(self.frutas_atuais))
        for i, item in enumerate(self.frutas_atuais):
            self.balcoes.append(Balcao(posicoes[i][0], posicoes[i][1], item))

        clientes = CLIENTES.copy()
        random.shuffle(clientes)
        for i, (x, y) in enumerate(gerar_posicoes_mesas(dados["mesas"])):
            cliente = clientes[i % len(clientes)]
            pedido = random.choice(self.frutas_atuais)
            urgente = i < dados.get("urgentes", 0)
            self.mesas.append(Mesa(x, y, cliente, pedido, dados["tempo"], urgente))

        if self.fase >= 3:
            centro = LARGURA // 2
            self.paredes.append(
                pygame.Rect(centro - 48, 220, 96, 275)
            )

        if self.fase >= 7:
            # A partir da fase 7, a segunda barreira fica maior e exige
            # que o jogador escolha melhor por onde atravessar.
            self.paredes.append(
                pygame.Rect(centro + 100, ALTURA // 2 + 35, 90, 225)
            )
        elif self.fase >= 6:
            self.paredes.append(
                pygame.Rect(centro + 115, ALTURA // 2 + 80, 76, 170)
            )

    def iniciar(self):
        self.fase = 1
        self.pontuacao = 0
        self.clientes_insatisfeitos = 0
        self.pontuacao_salva = False
        self.jogador.rect.center = (LARGURA // 2, ALTURA // 2)
        self.jogador.item_na_mao = None
        self.criar_fase()
        self.estado = "jogando"

    def atualizar(self, dt):
        if self.estado != "jogando":
            return

        dados = FASES[self.fase - 1]
        self.jogador.mover(dados["velocidade"], self.paredes)

        for balcao in self.balcoes:
            if self.jogador.rect.colliderect(balcao.rect):
                self.jogador.item_na_mao = balcao.item

        for mesa in self.mesas:
            if self.jogador.rect.colliderect(mesa.rect) and self.jogador.item_na_mao is not None and not mesa.insatisfeito:
                if self.jogador.item_na_mao == mesa.pedido:
                    self.pontuacao += 10
                    self.jogador.item_na_mao = None
                    mesa.novo_pedido(self.frutas_atuais)

        for mesa in self.mesas:
            if mesa.atualizar(dt):
                self.pontuacao -= 5
                self.clientes_insatisfeitos += 1
                mesa.cliente = random.choice(CLIENTES)
                mesa.novo_pedido(self.frutas_atuais)

        if self.clientes_insatisfeitos >= 3 or self.pontuacao < 0:
            self.estado = "game_over"
            self.salvar_resultado()
            return

        if self.pontuacao >= dados["meta"]:
            if self.fase < len(FASES):
                self.fase += 1
                self.criar_fase()
                self.estado = "nivel"
            else:
                self.estado = "vitoria"
                self.salvar_resultado()

    def salvar_resultado(self):
        if self.pontuacao_salva:
            return
        salvar_pontuacao(self.nome_jogador.strip() or "Jogador", self.pontuacao)
        self.pontuacao_salva = True

    def desenhar_cenario(self):
        tela.fill(FUNDO_JOGO)
        pygame.draw.rect(tela, MARROM_ESCURO, (0, 0, LARGURA, 78))
        pygame.draw.rect(tela, BEGE, (30, 98, LARGURA - 60, ALTURA - 128), border_radius=20)
        pygame.draw.rect(tela, BEGE_ESCURO, (30, 98, LARGURA - 60, ALTURA - 128), 3, border_radius=20)

        painel_frutas = pygame.Rect(50, 112, 230, ALTURA - 170)
        painel_mesas = pygame.Rect(LARGURA - 375, 112, 325, ALTURA - 170)
        desenhar_painel(painel_frutas, ROSA_CLARO, (226, 172, 181), 18, 2)
        desenhar_painel(painel_mesas, CREME, BEGE_ESCURO, 18, 2)

        desenhar_texto("FRUTAS", fonte_media, MARROM_ESCURO, 118, 128)
        pygame.draw.line(tela, (225, 173, 183), (78, 164), (252, 164), 2)
        desenhar_texto("MESAS", fonte_media, MARROM_ESCURO, LARGURA - 273, 128)
        pygame.draw.line(tela, BEGE_ESCURO, (LARGURA - 347, 164), (LARGURA - 78, 164), 2)

        area_x = 310
        area_largura = LARGURA - 735
        pygame.draw.rect(tela, (235, 220, 199), (area_x, 112, area_largura, ALTURA - 170), border_radius=18)
        pygame.draw.rect(tela, (222, 203, 180), (area_x, 112, area_largura, ALTURA - 170), 2, border_radius=18)
        desenhar_texto("ÁREA DE ATENDIMENTO", fonte_pequena, (153, 126, 101), area_x + 25, 128)

        for parede in self.paredes:
            pygame.draw.rect(tela, SOMBRA, (parede.x + 7, parede.y + 7, parede.width, parede.height), border_radius=12)
            pygame.draw.rect(tela, MARROM, parede, border_radius=12)
            pygame.draw.rect(tela, MARROM_ESCURO, parede, 3, border_radius=12)

    def desenhar_hud(self):
        dados = FASES[self.fase - 1]
        desenhar_texto(f"FASE {self.fase}/{len(FASES)}", fonte_media, BRANCO, 22, 9)
        desenhar_texto(dados["nome"], fonte_pequena, (244, 226, 213), 22, 45)

        caixa_pontos = pygame.Rect(LARGURA - 430, 10, 215, 56)
        caixa_clientes = pygame.Rect(LARGURA - 200, 10, 178, 56)
        pygame.draw.rect(tela, (80, 55, 43), caixa_pontos, border_radius=13)
        pygame.draw.rect(tela, (80, 55, 43), caixa_clientes, border_radius=13)
        pontos = fonte_media.render(f"{self.pontuacao}/{dados['meta']} pts", True, BRANCO)
        clientes = fonte_pequena.render(f"Clientes: {self.clientes_insatisfeitos}/3", True, BRANCO)
        tela.blit(pontos, (caixa_pontos.centerx - pontos.get_width() // 2, caixa_pontos.y + 15))
        tela.blit(clientes, (caixa_clientes.centerx - clientes.get_width() // 2, caixa_clientes.y + 18))

    def desenhar_jogo(self):
        self.desenhar_cenario()
        for balcao in self.balcoes:
            balcao.desenhar()
        for mesa in self.mesas:
            mesa.desenhar()
        self.jogador.desenhar()
        self.desenhar_hud()

    def desenhar_logo(self, y=90):
        texto_centralizado("CAT", fonte_logo, MARROM_ESCURO, y)
        texto_centralizado("RUSH", fonte_logo, ROSA, y + 72)
        pygame.draw.line(tela, VERDE_ESCURO, (LARGURA // 2 - 145, y + 164), (LARGURA // 2 + 145, y + 164), 5)
        texto_centralizado("FRUIT CAFÉ", fonte_pequena, MARROM, y + 176)

    def desenhar_inicio(self, mouse_pos):
        tela.fill(FUNDO)
        pygame.draw.circle(tela, ROSA_CLARO, (LARGURA // 2, 220), 215)
        pygame.draw.circle(tela, VERDE_CLARO, (150, ALTURA - 95), 90)
        pygame.draw.circle(tela, PESSEGO, (LARGURA - 130, 120), 70)
        self.desenhar_logo(62)
        texto_centralizado("Sirva frutas, atenda os clientes e bata a meta!", fonte_media, MARROM, 330)
        desenhar_botao(self.botao_iniciar, "INICIAR JOGO", mouse_pos)
        desenhar_botao(self.botao_ranking, "VER RANKING", mouse_pos)
        texto_centralizado("ESC - Sair", fonte_pequena, CINZA, ALTURA - 48)

    def desenhar_nome(self):
        tela.fill(FUNDO)
        self.desenhar_logo(42)
        texto_centralizado("Antes de começar...", fonte_grande, MARROM_ESCURO, 285)
        texto_centralizado("Digite seu nome para aparecer no ranking", fonte_media, MARROM, 330)

        caixa = pygame.Rect(LARGURA // 2 - 230, 380, 460, 64)
        desenhar_painel(caixa, BRANCO, VERDE_ESCURO, 13, 3)
        superficie = fonte_media.render(self.nome_jogador or "Digite seu nome", True, PRETO if self.nome_jogador else CINZA)
        tela.blit(superficie, (caixa.x + 18, caixa.y + 17))
        texto_centralizado("ENTER - Começar", fonte_media, VERDE_ESCURO, 470)
        texto_centralizado("ESC - Voltar", fonte_pequena, CINZA, 520)

    def desenhar_nivel(self, mouse_pos):
        tela.fill(FUNDO)
        pygame.draw.circle(tela, VERDE_CLARO, (LARGURA // 2, 255), 175)
        texto_centralizado("FASE CONCLUÍDA!", fonte_titulo, VERDE_ESCURO, 125)
        texto_centralizado(f"Você avançou para a fase {self.fase}", fonte_grande, MARROM_ESCURO, 235)
        texto_centralizado(FASES[self.fase - 1]["nome"], fonte_titulo, ROSA, 300)
        descricao = FASES[self.fase - 1].get("descricao")
        if descricao:
            texto_centralizado(descricao, fonte_media, MARROM, 365)
        texto_centralizado(f"Pontuação atual: {self.pontuacao}", fonte_media, MARROM, 420)
        desenhar_botao(self.botao_continuar, "CONTINUAR", mouse_pos)
        texto_centralizado("ENTER - Continuar", fonte_pequena, CINZA, 595)
        texto_centralizado("ESC - Sair", fonte_pequena, CINZA, 625)


    def desenhar_vitoria(self):
        tela.fill(FUNDO)
        texto_centralizado("VITÓRIA!", fonte_titulo, VERDE_ESCURO, 115)
        texto_centralizado("Você completou as 8 fases!", fonte_grande, MARROM_ESCURO, 210)
        texto_centralizado(f"Pontuação final: {self.pontuacao}", fonte_grande, MARROM, 280)
        texto_centralizado("R - Ver ranking", fonte_media, MARROM_ESCURO, 380)
        texto_centralizado("ENTER - Jogar novamente", fonte_media, MARROM_ESCURO, 425)
        texto_centralizado("ESC - Sair", fonte_pequena, CINZA, 480)

    def desenhar_game_over(self):
        tela.fill(FUNDO)
        texto_centralizado("GAME OVER", fonte_titulo, VERMELHO, 115)
        texto_centralizado("Os clientes ficaram insatisfeitos.", fonte_grande, MARROM_ESCURO, 210)
        texto_centralizado(f"Pontuação: {self.pontuacao}", fonte_grande, MARROM, 280)
        texto_centralizado("R - Ver ranking", fonte_media, MARROM_ESCURO, 380)
        texto_centralizado("ENTER - Tentar novamente", fonte_media, MARROM_ESCURO, 425)
        texto_centralizado("ESC - Sair", fonte_pequena, CINZA, 480)

    def desenhar_ranking(self):
        tela.fill(FUNDO)
        texto_centralizado("RANKING GERAL", fonte_titulo, MARROM_ESCURO, 48)
        texto_centralizado("Os melhores garçons do CatRush", fonte_media, MARROM, 120)

        ranking = carregar_ranking()
        if not ranking:
            texto_centralizado("Nenhuma pontuação registrada ainda.", fonte_media, MARROM, 250)
        else:
            largura = 650
            x = LARGURA // 2 - largura // 2
            y = 175
            for i, jogador in enumerate(ranking[:10]):
                rect = pygame.Rect(x, y, largura, 50)
                desenhar_painel(rect, BRANCO if i % 2 == 0 else CREME, BEGE_ESCURO, 11, 1)
                pos = fonte_media.render(f"{i + 1}º", True, ROSA if i < 3 else MARROM)
                tela.blit(pos, (x + 18, y + 10))
                nome = fonte_media.render(str(jogador.get("nome", "Jogador"))[:22], True, MARROM_ESCURO)
                tela.blit(nome, (x + 85, y + 10))
                pts = fonte_media.render(f"{jogador.get('pontuacao', 0)} pts", True, VERDE_ESCURO)
                tela.blit(pts, (x + largura - pts.get_width() - 20, y + 10))
                y += 56

        texto_centralizado("ENTER - Jogar novamente", fonte_media, MARROM, ALTURA - 105)
        texto_centralizado("ESC - Voltar", fonte_pequena, CINZA, ALTURA - 60)


jogo = CatRush()
executando = True

while executando:
    dt = relogio.tick(FPS) / 1000
    mouse_pos = pygame.mouse.get_pos()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            executando = False

        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            if jogo.estado == "inicio":
                executando = False
            elif jogo.estado in ("ranking", "nome"):
                jogo.estado = "inicio"
            elif jogo.estado == "nivel":
                jogo.estado = "jogando"
            else:
                executando = False
            continue

        if jogo.estado == "inicio":
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if jogo.botao_iniciar.collidepoint(evento.pos):
                    jogo.nome_jogador = ""
                    jogo.estado = "nome"
                elif jogo.botao_ranking.collidepoint(evento.pos):
                    jogo.estado = "ranking"

        elif jogo.estado == "nome":
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    if jogo.nome_jogador.strip():
                        jogo.iniciar()
                elif evento.key == pygame.K_BACKSPACE:
                    jogo.nome_jogador = jogo.nome_jogador[:-1]
                elif len(jogo.nome_jogador) < 18 and evento.unicode.isprintable():
                    jogo.nome_jogador += evento.unicode

        elif jogo.estado == "nivel":
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if jogo.botao_continuar.collidepoint(evento.pos):
                    jogo.estado = "jogando"
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_RETURN:
                jogo.estado = "jogando"

        elif jogo.estado == "vitoria":
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    jogo.iniciar()
                elif evento.key == pygame.K_r:
                    jogo.estado = "ranking"

        elif jogo.estado == "game_over":
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    jogo.iniciar()
                elif evento.key == pygame.K_r:
                    jogo.estado = "ranking"

        elif jogo.estado == "ranking":
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_RETURN:
                jogo.iniciar()

    jogo.atualizar(dt)

    if jogo.estado == "inicio":
        jogo.desenhar_inicio(mouse_pos)
    elif jogo.estado == "nome":
        jogo.desenhar_nome()
    elif jogo.estado == "jogando":
        jogo.desenhar_jogo()
    elif jogo.estado == "nivel":
        jogo.desenhar_nivel(mouse_pos)
    elif jogo.estado == "vitoria":
        jogo.desenhar_vitoria()
    elif jogo.estado == "game_over":
        jogo.desenhar_game_over()
    elif jogo.estado == "ranking":
        jogo.desenhar_ranking()

    pygame.display.flip()

pygame.quit()
sys.exit()
