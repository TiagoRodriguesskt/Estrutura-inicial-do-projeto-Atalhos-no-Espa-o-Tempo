"""
Física do buraco de minhoca de Morris-Thorne (exemplo mais simples do artigo).

Escolhas do artigo (seção 8 da explicação):
    Φ(r) = 0          -> sem gravidade para quem está parado, sem maré radial
    b(r) = b0² / r    -> função de forma; a garganta fica em r = b0

Com a distância própria l (o que uma régua mede ao longo do túnel),
a métrica fica:

    ds² = -c² dt² + dl² + (l² + b0²) (dθ² + sen²θ dφ²)

Unidades: usamos b0 = 1 e c = 1 em tudo. Assim, "l = 3" significa
"3 vezes o raio da garganta". Isso deixa os números simples.

Este arquivo NÃO usa pygame: só matemática. Assim dá para testar e
reaproveitar as funções em outros scripts (por exemplo, num notebook).
"""

import math

B0 = 1.0  # raio da garganta (unidade de comprimento da simulação)


# ---------------------------------------------------------------------------
# 1. Geometria
# ---------------------------------------------------------------------------

def raio_circunferencial(l: float, b0: float = B0) -> float:
    """Raio r das esferas em volta do túnel, na posição l.

    r² = l² + b0²  ->  mínimo r = b0 na garganta (l = 0).
    r é definido pela circunferência: um círculo nessa posição mede 2πr.
    """
    return math.sqrt(l * l + b0 * b0)


def funcao_forma(r: float, b0: float = B0) -> float:
    """b(r) = b0² / r, a função de forma escolhida no artigo."""
    return b0 * b0 / r


def altura_imersao(l: float, b0: float = B0) -> float:
    """Altura z do diagrama de imersão (o "funil") na posição l.

    Do artigo: dz/dr = ±(r/b - 1)^(-1/2). Para b = b0²/r isso integra em
    z = ±b0·arccosh(r/b0). Escrevendo em termos de l, com o sinal certo
    de cada lado: z = b0·asinh(l/b0). A superfície é um catenóide.
    """
    return b0 * math.asinh(l / b0)


def ponto_3d(l: float, phi: float, b0: float = B0) -> tuple[float, float, float]:
    """Converte (l, φ) num ponto (x, y, z) do funil desenhado em 3D."""
    r = raio_circunferencial(l, b0)
    return (r * math.cos(phi), r * math.sin(phi), altura_imersao(l, b0))


# ---------------------------------------------------------------------------
# 2. Matéria necessária (equações de Einstein)
# ---------------------------------------------------------------------------
# Em unidades de c⁴/(8πG b0²). Com Φ = 0 e b = b0²/r, as fórmulas do
# artigo dão (ε = b0²/r⁴):
#     densidade de energia   ρc² = -ε   (NEGATIVA em todo lugar!)
#     tensão radial          τ   = +ε
#     pressão lateral        p   = +ε

def densidade_energia(l: float, b0: float = B0) -> float:
    """ρc² na posição l, em unidades de c⁴/(8πG b0²). Sempre negativa."""
    r = raio_circunferencial(l, b0)
    return -(b0 ** 4) / r ** 4


def tensao_radial(l: float, b0: float = B0) -> float:
    """τ na posição l, em unidades de c⁴/(8πG b0²)."""
    r = raio_circunferencial(l, b0)
    return (b0 ** 4) / r ** 4


def tensao_garganta_pascal(b0_metros: float) -> float:
    """Tensão na garganta em pascal (N/m²) para uma garganta real.

    τ0 = c⁴ / (8πG b0²). Para b0 = 10 m dá ~5e40 Pa.
    """
    c = 299_792_458.0
    G = 6.674_30e-11
    return c ** 4 / (8 * math.pi * G * b0_metros ** 2)


# ---------------------------------------------------------------------------
# 3. Raios de luz (geodésicas nulas no plano do equador)
# ---------------------------------------------------------------------------
# Quantidades conservadas: energia E e momento angular L.
# Parâmetro de impacto β = L·c/E (a "mira" do raio).
#
#   (dl/dλ)² = 1 - β²/(l² + b0²)          (equação de "energia")
#   dφ/dλ    = β/(l² + b0²)
#
# Derivando a primeira em relação a λ, sai a equação de 2ª ordem que
# integramos numericamente (evita o problema do sinal da raiz quadrada):
#
#   d²l/dλ² = β² l / (l² + b0²)²

def potencial_efetivo(l: float, beta: float, b0: float = B0) -> float:
    """V(l) = β²/(l² + b0²). O raio só existe onde V(l) ≤ 1.

    O máximo de V é na garganta: V(0) = β²/b0².
      β < b0  -> máximo < 1  -> o raio passa para o outro lado
      β > b0  -> máximo > 1  -> o raio bate na "barreira" e volta
    """
    return beta * beta / (l * l + b0 * b0)


def _derivadas(estado, beta, b0):
    """Lado direito das EDOs. estado = (l, dl/dλ, φ)."""
    l, dl, _phi = estado
    s = l * l + b0 * b0
    return (dl, beta * beta * l / (s * s), beta / s)


def passo_rk4(estado, beta, h, b0=B0):
    """Um passo de Runge-Kutta de 4ª ordem (o mesmo do Projeto 2 do plano)."""
    def soma(a, k, f):
        return tuple(ai + f * ki for ai, ki in zip(a, k))

    k1 = _derivadas(estado, beta, b0)
    k2 = _derivadas(soma(estado, k1, h / 2), beta, b0)
    k3 = _derivadas(soma(estado, k2, h / 2), beta, b0)
    k4 = _derivadas(soma(estado, k3, h), beta, b0)
    return tuple(
        e + h / 6 * (a + 2 * b + 2 * c + d)
        for e, a, b, c, d in zip(estado, k1, k2, k3, k4)
    )


def estado_inicial(beta: float, l0: float = 6.0, phi0: float = 0.0, b0: float = B0):
    """Raio que parte de l0 (universo de cima) indo em direção à garganta."""
    v = 1.0 - potencial_efetivo(l0, beta, b0)
    if v < 0:
        raise ValueError("Com esse β o raio não pode estar em l0; aumente l0.")
    return (l0, -math.sqrt(v), phi0)


def trajetoria(beta: float, l0: float = 6.0, phi0: float = 0.0,
               h: float = 0.01, l_max: float = 6.5, passos_max: int = 20_000,
               b0: float = B0) -> list[tuple[float, float]]:
    """Integra o raio inteiro e devolve a lista de pontos (l, φ)."""
    estado = estado_inicial(beta, l0, phi0, b0)
    pontos = [(estado[0], estado[2])]
    for _ in range(passos_max):
        estado = passo_rk4(estado, beta, h, b0)
        pontos.append((estado[0], estado[2]))
        if abs(estado[0]) > l_max:
            break
    return pontos


def destino(beta: float, b0: float = B0) -> str:
    """Previsão analítica: para onde o raio vai?"""
    if abs(beta) < b0:
        return "atravessa"
    if abs(beta) > b0:
        return "reflete"
    return "orbita"


# ---------------------------------------------------------------------------
# Autoteste: `uv run python fisica.py`
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # A integração numérica concorda com a regra analítica?
    for beta in (0.0, 0.5, 0.9, 1.1, 1.5, 2.0):
        l_final = trajetoria(beta)[-1][0]
        lado = "atravessa" if l_final < 0 else "reflete"
        assert lado == destino(beta), (beta, lado)
        print(f"β = {beta:.1f} b0 -> {lado:9s} (l final = {l_final:+.2f} b0)")

    # A energia (dl/dλ)² + V(l) = 1 se conserva ao longo do raio?
    estado = estado_inicial(0.7)
    for _ in range(1500):
        estado = passo_rk4(estado, 0.7, 0.01)
    erro = abs(estado[1] ** 2 + potencial_efetivo(estado[0], 0.7) - 1.0)
    assert erro < 1e-8, erro
    print(f"Conservação da energia: erro = {erro:.1e}")

    print(f"Tensão na garganta de 10 m: {tensao_garganta_pascal(10):.2e} Pa")
    print("Tudo certo.")
