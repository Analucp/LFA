import re

class Nodo:
    def __init__(self, valor):
        self.valor = valor
        self.izquierdo = None
        self.derecho = None
        self.first = set()
        self.last = set()
        self.nullable = False
        self.numero_hoja = None  # Número del nodo hoja si es terminal
        self.follow = set()  # Conjunto Follow

# Precedencia de operadores
def precedencia(token):
    if token == '*':
        return 3
    elif token == '.':
        return 2
    elif token == '|':
        return 1
    else:
        return 0

# Función para verificar si es un operador
def es_operador(token):
    return token in ['.', '|', '*', '(', ')']

# Función para tokenizar la expresión que puede contener terminales como 'a1', 'b2', etc.
def tokenizar_expresion(expresion):
    # Expresión regular para detectar terminales alfanuméricos y operadores
    return re.findall(r'[a-zA-Z]+\d*|[|.*()]', expresion)

# Construir el árbol de expresión y numerar hojas
def construir_arbol(expresion_regular):
    pila_tokens = []
    pila_arboles = []
    contador_hojas = [1]  # Lista para contar las hojas, lo hacemos lista para que sea modificable dentro de funciones anidadas

    def asignar_numeros_hojas(nodo):
        """Función recursiva para asignar números a los nodos hoja de izquierda a derecha"""
        if nodo is None:
            return
        if nodo.izquierdo is None and nodo.derecho is None:  # Si es un nodo hoja
            nodo.numero_hoja = contador_hojas[0]
            contador_hojas[0] += 1
        asignar_numeros_hojas(nodo.izquierdo)
        asignar_numeros_hojas(nodo.derecho)

    # Usamos la nueva función de tokenización
    tokens = tokenizar_expresion(expresion_regular)

    for token in tokens:
        if not es_operador(token) and token not in ['(', ')']:  # Si es un símbolo terminal
            nodo = Nodo(token)
            pila_arboles.append(nodo)
        elif token == '(':
            pila_tokens.append(token)
        elif token == ')':
            while pila_tokens and pila_tokens[-1] != '(':
                operador = pila_tokens.pop()
                nodo = Nodo(operador)

                if operador == '*':  # Operador unario
                    nodo.izquierdo = pila_arboles.pop()
                else:  # Operadores binarios
                    nodo.derecho = pila_arboles.pop()
                    nodo.izquierdo = pila_arboles.pop()

                pila_arboles.append(nodo)
            pila_tokens.pop()  # Quitar el '('
        elif es_operador(token):
            while (pila_tokens and pila_tokens[-1] != '(' and
                   precedencia(pila_tokens[-1]) >= precedencia(token)):
                operador = pila_tokens.pop()
                nodo = Nodo(operador)

                if operador == '*':
                    nodo.izquierdo = pila_arboles.pop()
                else:
                    nodo.derecho = pila_arboles.pop()
                    nodo.izquierdo = pila_arboles.pop()

                pila_arboles.append(nodo)
            pila_tokens.append(token)

    while pila_tokens:
        operador = pila_tokens.pop()
        nodo = Nodo(operador)

        if operador == '*':
            nodo.izquierdo = pila_arboles.pop()
        else:
            nodo.derecho = pila_arboles.pop()
            nodo.izquierdo = pila_arboles.pop()

        pila_arboles.append(nodo)

    arbol_final = pila_arboles.pop()
    asignar_numeros_hojas(arbol_final)  # Asignar números de hoja

    return arbol_final, contador_hojas[0] - 1  # Devuelve el árbol y el número total de hojas

# Calcular First, Last, Nullable y Follow
def calcular_conjuntos(nodo, follow_dict):
    if nodo is None:
        return

    # Calcular First, Last y Nullable recursivamente
    if nodo.izquierdo:
        calcular_conjuntos(nodo.izquierdo, follow_dict)
    if nodo.derecho:
        calcular_conjuntos(nodo.derecho, follow_dict)

    if nodo.numero_hoja is not None:  # Es un símbolo terminal (hoja numerada)
        nodo.first = {nodo.numero_hoja}
        nodo.last = {nodo.numero_hoja}
        nodo.nullable = False
    elif nodo.valor == '|':
        nodo.first = nodo.izquierdo.first.union(nodo.derecho.first)
        nodo.last = nodo.izquierdo.last.union(nodo.derecho.last)
        nodo.nullable = nodo.izquierdo.nullable or nodo.derecho.nullable
    elif nodo.valor == '.':
        if nodo.izquierdo.nullable:
            nodo.first = nodo.izquierdo.first.union(nodo.derecho.first)
        else:
            nodo.first = nodo.izquierdo.first
        if nodo.derecho.nullable:
            nodo.last = nodo.izquierdo.last.union(nodo.derecho.last)
        else:
            nodo.last = nodo.derecho.last
        nodo.nullable = nodo.izquierdo.nullable and nodo.derecho.nullable

        # Follow para concatenación
        for i in nodo.izquierdo.last:
            follow_dict[i].update(nodo.derecho.first)
    elif nodo.valor == '*':
        nodo.first = nodo.izquierdo.first
        nodo.last = nodo.izquierdo.last
        nodo.nullable = True

        # Follow para *
        for i in nodo.last:
            follow_dict[i].update(nodo.first)

# Función para guardar los resultados de Follow en un archivo de texto
def guardar_follow_en_txt(follow_dict, archivo_txt):
    with open(archivo_txt, 'w') as archivo:
        archivo.write(f"{'SIMBOLO':<10} {'FOLLOW':<10}\n")
        archivo.write("-" * 20 + "\n")
        for simbolo, follow in sorted(follow_dict.items()):
            archivo.write(f"{simbolo:<10} {str(sorted(follow)):<10}\n")

# Ejemplo de uso con la expresión regular 'a1.a1*.b2'
expresion = "(a1.a1*).b2|(w2.a2.w2|m2.a2.m2).b3|(o1).c2|(v1.v2).c3|(v1).d1|(v2).d2|(v2.o1).d3|(v1.o1).e1|(v3).e2|(w1).e3|(q2.o3).f1|(s2).f2|(p1.r3.q3).f3|(q1.q2.q3).g1|(q3.r1.r2).g2|(r3.q2.s1).g3|(s3.s2).h1|(s2.t1).h2|(n3).h3|(u3).i1|(u1).i2|(u2).i3|(s3).j1|(t1).j2|(t2).j3|(t3).k1|(u3.u3).k2|(n1).k3|(n2).l1|(n1.o1).l2|(a3.(a3|a1)*b1.()).c1"

# Construir árbol
arbol, total_hojas = construir_arbol(expresion)

# Diccionario para almacenar los follow de cada nodo hoja numerado (ajustado al número real de hojas)
follow_dict = {i: set() for i in range(1, total_hojas + 1)}

# Calcular First, Last, Nullable y Follow
calcular_conjuntos(arbol, follow_dict)

# Guardar la tabla de follow en un archivo de texto
ruta_salida_follow = 'C:/Users/Usuario/Downloads/tablaFOLLOWS.txt'
guardar_follow_en_txt(follow_dict, ruta_salida_follow)

print(f"Tabla de Follow guardada exitosamente en {ruta_salida_follow}")

