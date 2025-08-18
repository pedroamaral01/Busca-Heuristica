import tkinter as tk
import heapq
import itertools

# --- Custos conforme especificação ---
CUSTOS_HYRULE = {
    '0': 10,    # Grama (G)
    '1': 20,    # Areia (S)
    '2': 100,   # Floresta (F)
    '3': 150,   # Montanha (M)
    '4': 180,   # Água (A)
    '5': 0,     # Master Sword (MS)
    'A': 0,     # Entrada da Masmorra 1
    'B': 0,     # Entrada da Masmorra 2
    'C': 0,     # Entrada da Masmorra 3
    '7': 0,     # Lost Woods (LW)
    '8': 0      # Início do Link (L)
}

CUSTOS_MASMORRA = {
    '0': float('inf'),  # Parede
    '1': 10,            # Caminho
    '3': 0,             # Entrada/Saída
    '4': 0              # Pingente
}

# --- Funções ---
def ler_mapa(arquivo):
    with open(arquivo, 'r') as f:
        return [list(l.strip()) for l in f]

def localizar(mapa, valor):
    for i, row in enumerate(mapa):
        for j, val in enumerate(row):
            if val == valor:
                return (i, j)
    return None

def a_star(mapa, inicio, fim, custos):
    fila = [(0, 0, inicio, [inicio])]
    visitados = {inicio: 0}
    while fila:
        f, g, atual, caminho = heapq.heappop(fila)
        if atual == fim:
            return caminho, g
        x, y = atual
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < len(mapa) and 0 <= ny < len(mapa[0]):
                terreno = mapa[nx][ny]
                custo = custos.get(terreno, float('inf'))
                if custo == float('inf'):
                    continue
                ng = g + custo
                if ng < visitados.get((nx, ny), float('inf')):
                    visitados[(nx, ny)] = ng
                    h = abs(nx - fim[0]) + abs(ny - fim[1])
                    heapq.heappush(fila, (ng+h, ng, (nx, ny), caminho+[(nx, ny)]))
    return None, float('inf')

# --- Carregar mapas ---
mapa_principal = ler_mapa("hyrule.txt")
masmorras = [ler_mapa("masmorra1.txt"),
             ler_mapa("masmorra2.txt"),
             ler_mapa("masmorra3.txt")]

# --- Localizar pontos ---
pos_link = localizar(mapa_principal, '8')
pos_lost_woods = localizar(mapa_principal, '7')
entradas = {1: localizar(mapa_principal, 'A'),
            2: localizar(mapa_principal, 'B'),
            3: localizar(mapa_principal, 'C')}

masm_info = []
for idx, mapa_masm in enumerate(masmorras, start=1):
    entrada = localizar(mapa_masm, '3')
    pingente = localizar(mapa_masm, '4')
    masm_info.append({
        "portao": entradas[idx],
        "entrada": entrada,
        "pingente": pingente,
        "mapa": mapa_masm
    })

# --- Melhor caminho ---
ordens = list(itertools.permutations(range(len(masm_info))))
melhor_custo = float('inf')
melhor_caminho_total = None

for ordem in ordens:
    custo_total = 0
    caminho_total_temp = []
    pos_atual = pos_link
    for idx_masm in ordem:
        masm = masm_info[idx_masm]
        # até portão
        cam, custo = a_star(mapa_principal, pos_atual, masm["portao"], CUSTOS_HYRULE)
        caminho_total_temp += [("main", p) for p in cam]
        custo_total += custo
        # entrada → pingente → entrada
        for a, b in [(masm["entrada"], masm["pingente"]),
                     (masm["pingente"], masm["entrada"])]:
            cam, custo = a_star(masm["mapa"], a, b, CUSTOS_MASMORRA)
            caminho_total_temp += [(f"M{idx_masm+1}", p) for p in cam]
            custo_total += custo
        pos_atual = masm["portao"]

    # saída da última masmorra → Lost Woods (destino final)
    cam, custo = a_star(mapa_principal, pos_atual, pos_lost_woods, CUSTOS_HYRULE)
    caminho_total_temp += [("main", p) for p in cam]
    custo_total += custo

    if custo_total < melhor_custo:
        melhor_custo = custo_total
        melhor_caminho_total = caminho_total_temp

# --- Tkinter ---
cell_size = 12
root = tk.Tk()
root.title("A Jornada de Link - Mapas")

label_custo = tk.Label(root, text="Custo acumulado: 0", font=("Arial", 12))
label_custo.grid(row=1, column=0, columnspan=4, pady=5)

canvas_main = tk.Canvas(root, width=len(mapa_principal[0]) * cell_size,
                        height=len(mapa_principal) * cell_size)
canvas_main.grid(row=0, column=0)
canvas_masmorras = []
for idx, m in enumerate(masmorras, start=1):
    c = tk.Canvas(root, width=len(m[0]) * cell_size,
                  height=len(m) * cell_size)
    c.grid(row=0, column=idx)
    canvas_masmorras.append(c)

def cor(val, masmorra=False):
    if masmorra:
        return {
            '0': "black",
            '1': "white",
            '3': "orange",
            '4': "purple"
        }.get(val, "gray")
    else:
        return {
            '0': "lightgreen",   # Grama
            '1': "khaki",        # Areia
            '2': "forestgreen",  # Floresta
            '3': "saddlebrown",  # Montanha
            '4': "blue",         # Água
            '5': "gold",         # Master Sword
            'A': "red",          # Entrada masmorra 1
            'B': "red",          # Entrada masmorra 2
            'C': "red",          # Entrada masmorra 3
            '7': "purple",       # Lost Woods (destaque roxo)
            '8': "orange"        # Início do Link (destaque laranja)
        }.get(val, "black")

def desenhar(mapa, masmorra=False, canvas=None):
    for i, row in enumerate(mapa):
        for j, val in enumerate(row):
            canvas.create_rectangle(j * cell_size, i * cell_size,
                                    (j + 1) * cell_size, (i + 1) * cell_size,
                                    fill=cor(val, masmorra), outline="black")

# Desenhar todos os mapas
desenhar(mapa_principal, False, canvas_main)
for i, m in enumerate(masmorras):
    desenhar(m, True, canvas_masmorras[i])

# --- Animação ---
idx_anim = 0
custo_acumulado = 0

def animar():
    global idx_anim, custo_acumulado
    if idx_anim >= len(melhor_caminho_total):
        label_custo.config(text=f"Custo final: {custo_acumulado}")
        return

    mapa_id, (r, c) = melhor_caminho_total[idx_anim]

    if mapa_id == "main" and mapa_principal[r][c] == '7':
        custo_acumulado += CUSTOS_HYRULE['7']
        canvas_main.create_oval(c * cell_size + 2, r * cell_size + 2,
                                (c + 1) * cell_size - 2, (r + 1) * cell_size - 2,
                                fill="red")
        label_custo.config(text=f"Custo final : {custo_acumulado}")
        return

    if mapa_id == "main":
        custo_acumulado += CUSTOS_HYRULE[mapa_principal[r][c]]
        canvas_main.create_oval(c * cell_size + 2, r * cell_size + 2,
                                (c + 1) * cell_size - 2, (r + 1) * cell_size - 2,
                                fill="red")
    else:
        num = int(mapa_id[1]) - 1
        custo_acumulado += CUSTOS_MASMORRA[masmorras[num][r][c]]
        canvas_masmorras[num].create_oval(c * cell_size + 2, r * cell_size + 2,
                                          (c + 1) * cell_size - 2, (r + 1) * cell_size - 2,
                                          fill="red")

    label_custo.config(text=f"Custo acumulado: {custo_acumulado}")
    idx_anim += 1
    root.after(50, animar)

animar()
root.mainloop()