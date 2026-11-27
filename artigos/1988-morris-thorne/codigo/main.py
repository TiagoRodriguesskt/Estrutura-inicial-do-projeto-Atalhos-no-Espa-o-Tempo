"""
Simulação interativa do buraco de minhoca de Morris & Thorne (1988).

Esquerda: o diagrama de imersão (o "funil", um catenóide) em 3D, com raios
de luz percorrendo a superfície. Azul = universo de cima (l > 0),
laranja = universo de baixo (l < 0).

Direita, em cima: o potencial efetivo V(l) = β²/(l² + b0²). O raio só
pode estar onde V ≤ 1. Se o pico (na garganta) passa de 1, o raio volta.

Direita, embaixo: a matéria que as equações de Einstein exigem.
A densidade de energia ρc² é NEGATIVA: é a matéria exótica do artigo.

Controles:
    ↑ / ↓        muda o parâmetro de impacto β (a "mira" do raio)
    ESPAÇO       dispara um raio com o β atual
    F            dispara um leque de raios (β de 0 a 2 b0)
    C            apaga os raios
    arrastar     gira a câmera (botão esquerdo do mouse)
    roda / + -   zoom
    R            volta a câmera ao início
    H            mostra/esconde a ajuda
    ESC          sai

Rodar:  uv run main.py
"""

import argparse
import math
import sys

import pygame

import fisica as f

LARGURA, ALTURA = 1280, 760
PAINEL_X = 800  # onde começa o painel da direita

# Cores
FUNDO = (12, 14, 22)
TEXTO = (225, 228, 235)
TEXTO_FRACO = (140, 146, 160)
AZUL = (80, 150, 255)
LARANJA = (255, 150, 60)
VERMELHO = (255, 90, 90)
VERDE = (110, 220, 140)
GRADE = (45, 50, 65)
CORES_RAIOS = [
    (255, 235, 120), (120, 255, 200), (255, 120, 200), (150, 200, 255),
    (255, 180, 120), (200, 140, 255), (140, 255, 120), (255, 255, 255),
    (120, 220, 255),
]

L_MAX = 6.0          # até onde desenhamos o funil, em unidades de b0
PASSOS_POR_QUADRO = 7  # velocidade da animação dos raios


# ---------------------------------------------------------------------------
# Câmera: transforma pontos 3D do funil em pixels da tela
# ---------------------------------------------------------------------------
class Camera:
    def __init__(self):
        self.reset()

    def reset(self):
        self.yaw = 0.6      # giro em torno do eixo do túnel
        self.pitch = 0.42   # inclinação (0 = de lado, π/2 = de cima)
        self.escala = 52.0  # pixels por b0
        self.centro = (PAINEL_X // 2, ALTURA // 2 + 10)

    def projetar(self, x, y, z):
        """Devolve (x_tela, y_tela, profundidade). Profundidade > 0 = atrás."""
        cy, sy = math.cos(self.yaw), math.sin(self.yaw)
        x1 = x * cy - y * sy
        y1 = x * sy + y * cy
        cp, sp = math.cos(self.pitch), math.sin(self.pitch)
        y2 = y1 * cp - z * sp
        z2 = y1 * sp + z * cp
        return (self.centro[0] + self.escala * x1,
                self.centro[1] - self.escala * z2,
                y2)


def escurecer(cor, fator):
    return tuple(int(c * fator) for c in cor)


# ---------------------------------------------------------------------------
# Raio de luz: a trajetória é calculada inteira no disparo e revelada aos poucos
# ---------------------------------------------------------------------------
class Raio:
    def __init__(self, beta, cor):
        self.beta = beta
        self.cor = cor
        self.pontos = f.trajetoria(beta, l0=L_MAX, l_max=L_MAX + 0.01)
        self.visiveis = 1
        self.resultado = f.destino(beta)

    def avancar(self):
        self.visiveis = min(len(self.pontos), self.visiveis + PASSOS_POR_QUADRO)

    @property
    def terminou(self):
        return self.visiveis >= len(self.pontos)

    @property
    def l_atual(self):
        return self.pontos[self.visiveis - 1][0]


# ---------------------------------------------------------------------------
# Desenho
# ---------------------------------------------------------------------------
def desenhar_funil(tela, cam):
    """Malha do catenóide: anéis (l constante) e meridianos (φ constante)."""
    # Anéis igualmente espaçados em z, que é como o funil "parece" de lado
    z_max = f.altura_imersao(L_MAX)
    n_aneis = 22
    for i in range(n_aneis + 1):
        z = -z_max + 2 * z_max * i / n_aneis
        l = math.sinh(z)
        cor = AZUL if l > 0 else LARANJA
        if abs(l) < 1e-9:
            cor = VERDE  # a garganta
        _polilinha_3d(tela, cam, [(l, 2 * math.pi * k / 72) for k in range(73)], cor,
                      2 if abs(l) < 1e-9 else 1)
    # Meridianos
    ls = [math.sinh(-z_max + 2 * z_max * j / 60) for j in range(61)]
    for k in range(24):
        phi = 2 * math.pi * k / 24
        pts = [(l, phi) for l in ls]
        _polilinha_3d(tela, cam, pts, None, 1)


def _polilinha_3d(tela, cam, pontos_lphi, cor_fixa, largura):
    anterior = None
    for l, phi in pontos_lphi:
        x, y, prof = cam.projetar(*f.ponto_3d(l, phi))
        if anterior is not None:
            cor = cor_fixa or (AZUL if l > 0 else LARANJA)
            fator = 0.28 if (prof + anterior[2]) > 0 else 0.6
            pygame.draw.line(tela, escurecer(cor, fator), anterior[:2], (x, y), largura)
        anterior = (x, y, prof)


def desenhar_raios(tela, cam, raios):
    for raio in raios:
        anterior = None
        for l, phi in raio.pontos[:raio.visiveis:2]:
            x, y, prof = cam.projetar(*f.ponto_3d(l, phi))
            if anterior is not None:
                fator = 0.45 if (prof + anterior[2]) > 0 else 1.0
                pygame.draw.line(tela, escurecer(raio.cor, fator), anterior[:2], (x, y), 3)
            anterior = (x, y, prof)
        # "fóton" na ponta
        l, phi = raio.pontos[raio.visiveis - 1]
        x, y, _ = cam.projetar(*f.ponto_3d(l, phi))
        pygame.draw.circle(tela, (255, 255, 255), (int(x), int(y)), 5)
        pygame.draw.circle(tela, raio.cor, (int(x), int(y)), 3)


def grafico(tela, fonte, ret, titulo, curvas, y_min, y_max, linhas_h=(), marcadores=()):
    """Gráfico simples: eixo l de -L_MAX a +L_MAX."""
    x0, y0, w, h = ret
    pygame.draw.rect(tela, (20, 23, 34), ret)
    pygame.draw.rect(tela, GRADE, ret, 1)

    def px(l):
        return x0 + (l + L_MAX) / (2 * L_MAX) * w

    def py(v):
        v = max(y_min, min(y_max, v))
        return y0 + h - (v - y_min) / (y_max - y_min) * h

    # eixos
    pygame.draw.line(tela, GRADE, (px(0), y0), (px(0), y0 + h))
    if y_min < 0 < y_max:
        pygame.draw.line(tela, GRADE, (x0, py(0)), (x0 + w, py(0)))
    for valor, cor, rotulo in linhas_h:
        pygame.draw.line(tela, cor, (x0, py(valor)), (x0 + w, py(valor)), 1)
        tela.blit(fonte.render(rotulo, True, cor), (x0 + w - fonte.size(rotulo)[0] - 4, py(valor) - 18))
    for funcao, cor, rotulo, i in curvas:
        pts = [(px(l), py(funcao(l))) for l in [-L_MAX + 2 * L_MAX * k / 240 for k in range(241)]]
        pygame.draw.lines(tela, cor, False, pts, 2)
        tela.blit(fonte.render(rotulo, True, cor), (x0 + 8, y0 + 8 + 18 * i))
    for l, v, cor in marcadores:
        pygame.draw.circle(tela, cor, (int(px(l)), int(py(v))), 6)
        pygame.draw.circle(tela, (255, 255, 255), (int(px(l)), int(py(v))), 6, 1)
    tela.blit(fonte.render(titulo, True, TEXTO), (x0, y0 - 22))
    rot_g = "garganta (l = 0)"
    tela.blit(fonte.render(rot_g, True, TEXTO_FRACO), (px(0) - fonte.size(rot_g)[0] // 2, y0 + h + 4))
    tela.blit(fonte.render("universo de baixo", True, LARANJA), (x0 + 4, y0 + h + 4))
    rot = "universo de cima"
    tela.blit(fonte.render(rot, True, AZUL), (x0 + w - fonte.size(rot)[0] - 4, y0 + h + 4))


def desenhar_painel(tela, fontes, beta, raios, mostrar_ajuda):
    fonte, fonte_g, fonte_p = fontes
    x = PAINEL_X + 10
    tela.blit(fonte_g.render("Buraco de minhoca de Morris-Thorne", True, TEXTO), (x, 14))
    tela.blit(fonte.render("Φ = 0,  b(r) = b0²/r   ·   unidades de b0", True, TEXTO_FRACO), (x, 44))

    cor_beta = VERDE if beta < 1 else (VERMELHO if beta > 1 else (255, 255, 120))
    tela.blit(fonte_g.render(f"β = {beta:.2f} b0", True, cor_beta), (x, 74))
    previsao = {"atravessa": "passa pela garganta  →  universo de baixo",
                "reflete": "bate na barreira  →  volta ao universo de cima",
                "orbita": "fica girando em volta da garganta (instável)"}[f.destino(beta)]
    tela.blit(fonte.render(previsao, True, cor_beta), (x, 104))

    # Gráfico 1: potencial efetivo
    # Cada fóton tem "energia" 1: ele fica sobre a linha branca, na posição l atual.
    marc = [(r.l_atual, 1.0, r.cor) for r in raios]
    grafico(tela, fonte_p, (x, 160, 450, 220),
            "Potencial efetivo  V(l) = β² / (l² + b0²)",
            [(lambda l: f.potencial_efetivo(l, beta), cor_beta, "V(l) para o β atual", 0)],
            0.0, 2.0,
            linhas_h=[(1.0, (255, 255, 255), "energia do raio = 1")],
            marcadores=marc)

    # Gráfico 2: matéria exótica
    grafico(tela, fonte_p, (x, 440, 450, 200),
            "Matéria exigida  (unidades de c⁴ / 8πG b0²)",
            [(f.densidade_energia, VERMELHO, "ρc²  densidade de energia  (< 0 !)", 0),
             (f.tensao_radial, (180, 180, 255), "τ  tensão radial", 1)],
            -1.1, 1.1)

    if mostrar_ajuda:
        linhas = ["↑↓ muda β   ESPAÇO dispara   F leque   C limpa",
                  "arraste para girar   roda = zoom   R reinicia câmera   H ajuda"]
        for i, t in enumerate(linhas):
            tela.blit(fonte_p.render(t, True, TEXTO_FRACO), (x, ALTURA - 50 + 20 * i))


def desenhar_legenda_funil(tela, fontes):
    fonte, _, fonte_p = fontes
    tela.blit(fonte.render("Diagrama de imersão (catenóide): z = b0·asinh(l / b0)", True, TEXTO), (14, 14))
    tela.blit(fonte_p.render("azul: universo de cima (l > 0)", True, AZUL), (14, 40))
    tela.blit(fonte_p.render("laranja: universo de baixo (l < 0)", True, LARANJA), (14, 60))
    tela.blit(fonte_p.render("verde: garganta, r = b0", True, VERDE), (14, 80))


# ---------------------------------------------------------------------------
# Laço principal
# ---------------------------------------------------------------------------
def carregar_fontes():
    nomes = "dejavusans,freesans,liberationsans,arial"
    return (pygame.font.SysFont(nomes, 16),
            pygame.font.SysFont(nomes, 22, bold=True),
            pygame.font.SysFont(nomes, 14))


def leque(raios):
    for i in range(9):
        b = 2.0 * i / 8
        raios.append(Raio(b, CORES_RAIOS[i % len(CORES_RAIOS)]))


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--screenshot", help="gera uma imagem PNG e sai (para testes)")
    args = parser.parse_args()

    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Morris & Thorne (1988) · buraco de minhoca atravessável")
    relogio = pygame.time.Clock()
    fontes = carregar_fontes()

    cam = Camera()
    beta = 0.8
    raios: list[Raio] = []
    mostrar_ajuda = True
    arrastando = False
    cor_idx = 0

    if args.screenshot:
        leque(raios)

    quadro = 0
    rodando = True
    while rodando:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                rodando = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    rodando = False
                elif ev.key == pygame.K_UP:
                    beta = min(3.0, round(beta + 0.05, 2))
                elif ev.key == pygame.K_DOWN:
                    beta = max(0.0, round(beta - 0.05, 2))
                elif ev.key == pygame.K_SPACE:
                    raios.append(Raio(beta, CORES_RAIOS[cor_idx % len(CORES_RAIOS)]))
                    cor_idx += 1
                elif ev.key == pygame.K_f:
                    leque(raios)
                elif ev.key == pygame.K_c:
                    raios.clear()
                elif ev.key == pygame.K_r:
                    cam.reset()
                elif ev.key == pygame.K_h:
                    mostrar_ajuda = not mostrar_ajuda
                elif ev.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    cam.escala *= 1.1
                elif ev.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    cam.escala /= 1.1
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and ev.pos[0] < PAINEL_X:
                arrastando = True
            elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                arrastando = False
            elif ev.type == pygame.MOUSEMOTION and arrastando:
                dx, dy = ev.rel
                cam.yaw -= dx * 0.008
                cam.pitch = max(-1.5, min(1.5, cam.pitch + dy * 0.008))
            elif ev.type == pygame.MOUSEWHEEL:
                cam.escala *= 1.1 ** ev.y

        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_LEFT]:
            cam.yaw += 0.03
        if teclas[pygame.K_RIGHT]:
            cam.yaw -= 0.03

        for r in raios:
            r.avancar()

        tela.fill(FUNDO)
        desenhar_funil(tela, cam)
        desenhar_raios(tela, cam, raios)
        desenhar_legenda_funil(tela, fontes)
        pygame.draw.line(tela, GRADE, (PAINEL_X, 0), (PAINEL_X, ALTURA))
        desenhar_painel(tela, fontes, beta, raios, mostrar_ajuda)
        pygame.display.flip()

        quadro += 1
        if args.screenshot and quadro == 150:
            pygame.image.save(tela, args.screenshot)
            rodando = False
        relogio.tick(60 if not args.screenshot else 0)

    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
