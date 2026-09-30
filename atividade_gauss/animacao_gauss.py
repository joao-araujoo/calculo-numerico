from fractions import Fraction as F

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.patches import Rectangle

# Sistema: 2x + y - z = 8 ; -3x - y + 2z = -11 ; -2x + y + 2z = -3
M = [[F(2), F(1), F(-1), F(8)],
     [F(-3), F(-1), F(2), F(-11)],
     [F(-2), F(1), F(2), F(-3)]]
n = 3

COR_PIVO = "#f4c542"
COR_ALVO = "#f28b82"
COR_NOVA = "#81c995"
COR_RESOLVIDA = "#8ab4f8"


def fmt(q):
    if q.denominator == 1:
        return str(q.numerator)
    return f"{q.numerator}/{q.denominator}"


def copia(A):
    return [linha[:] for linha in A]


# Cada quadro: (matriz, destaques {(i, j): cor}, título, texto, solução parcial)
quadros = []


def adiciona(A, destaques, titulo, texto, sol=None, repete=1):
    for _ in range(repete):
        quadros.append((copia(A), dict(destaques), titulo, texto, dict(sol or {})))


A = copia(M)
adiciona(A, {}, "Matriz aumentada [A | b]",
         "2x + y − z = 8\n−3x − y + 2z = −11\n−2x + y + 2z = −3", repete=3)

# Eliminação progressiva
for k in range(n - 1):
    adiciona(A, {(k, k): COR_PIVO}, f"Etapa {k + 1}: pivô a{k + 1}{k + 1} = {fmt(A[k][k])}",
             f"Zerar os elementos abaixo do pivô na coluna {k + 1}", repete=2)
    for i in range(k + 1, n):
        m = A[i][k] / A[k][k]
        destaques = {(k, k): COR_PIVO, (i, k): COR_ALVO}
        adiciona(A, destaques, f"Multiplicador m{i + 1}{k + 1}",
                 f"m{i + 1}{k + 1} = {fmt(A[i][k])} / {fmt(A[k][k])} = {fmt(m)}", repete=2)
        A[i] = [A[i][j] - m * A[k][j] for j in range(n + 1)]
        destaques = {(k, k): COR_PIVO}
        destaques.update({(i, j): COR_NOVA for j in range(n + 1)})
        adiciona(A, destaques, f"L{i + 1} ← L{i + 1} − ({fmt(m)})·L{k + 1}",
                 f"Novo elemento na coluna {k + 1}: {fmt(A[i][k])}", repete=2)

adiciona(A, {(i, j): COR_PIVO for i in range(n) for j in range(n) if j >= i},
         "Sistema triangular superior", "Pronto para a substituição regressiva", repete=3)

# Substituição regressiva
nomes = ["x", "y", "z"]
sol = {}
for i in range(n - 1, -1, -1):
    soma = sum(A[i][j] * sol[j] for j in range(i + 1, n))
    sol[i] = (A[i][n] - soma) / A[i][i]
    destaques = {(i, j): COR_NOVA for j in range(i, n + 1)}
    destaques.update({(r, r): COR_RESOLVIDA for r in sol if r != i})
    termos = " − ".join(f"({fmt(A[i][j])})({fmt(sol[j])})" for j in range(i + 1, n))
    numerador = fmt(A[i][n]) + (f" − {termos}" if termos else "")
    adiciona(A, destaques, f"Substituição regressiva: {nomes[i]}",
             f"{nomes[i]} = [{numerador}] / {fmt(A[i][i])} = {fmt(sol[i])}", sol, repete=3)

adiciona(A, {(r, r): COR_RESOLVIDA for r in range(n)}, "Solução",
         "x = 2,   y = 3,   z = −1", sol, repete=5)


fig, ax = plt.subplots(figsize=(7, 5.2), dpi=100)


def desenha(q):
    A, destaques, titulo, texto, sol = quadros[q]
    ax.clear()
    ax.set_xlim(-0.6, 4.8)
    ax.set_ylim(-2.4, 3.9)
    ax.axis("off")
    ax.set_title(titulo, fontsize=15, fontweight="bold")

    for i in range(n):
        for j in range(n + 1):
            x = j + (0.3 if j == n else 0)
            y = 2.6 - i
            cor = destaques.get((i, j), "white")
            ax.add_patch(Rectangle((x - 0.45, y - 0.4), 0.9, 0.8,
                                   facecolor=cor, edgecolor="#bbbbbb"))
            ax.text(x, y, fmt(A[i][j]), ha="center", va="center", fontsize=16)
        ax.text(-0.9 + 0.3, 2.6 - i, f"L{i + 1}", ha="right", va="center",
                fontsize=12, color="#555555")

    ax.plot([n - 0.35, n - 0.35], [0.1, 3.1], color="black", lw=1.5)
    for j, nome in enumerate(nomes + ["b"]):
        ax.text(j + (0.3 if j == n else 0), 3.35, nome, ha="center",
                fontsize=12, color="#555555")

    ax.text(2.1, -0.6, texto, ha="center", va="center", fontsize=13,
            bbox=dict(boxstyle="round", facecolor="#f5f5f5", edgecolor="#cccccc"))

    if sol:
        partes = [f"{nomes[r]} = {fmt(sol[r])}" for r in sorted(sol)]
        ax.text(2.1, -1.9, "   ".join(partes), ha="center", fontsize=14,
                color="#1a73e8", fontweight="bold")


anim = FuncAnimation(fig, desenha, frames=len(quadros), interval=900)
anim.save("eliminacao_gauss.gif", writer=PillowWriter(fps=1.1))
plt.close(fig)
