import re

class Nodo:
    def __init__(self, valor):
        self.valor = valor  # Valor del nodo (puede ser operador o terminal)
        self.izquierdo = None  # Hijo izquierdo
        self.derecho = None  # Hijo derecho

class Pila:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if not self.esta_vacia():
            return self.items.pop()
        else:
            raise Exception("Error: Pila vacía")

    def peek(self):
        if not self.esta_vacia():
            return self.items[-1]
        else:
            return None

    def esta_vacia(self):
        return len(self.items) == 0

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

# Función para dividir la expresión en tokens
def tokenizar_expresion(expresion_regular):
    # Usamos una expresión regular para agrupar terminales alfanuméricos como 'a1', 'b2', y los operadores individuales
    tokens = re.findall(r'[a-zA-Z]\d*|[().*|]', expresion_regular)
    return tokens

# Función para construir el árbol de expresión basado en el algoritmo proporcionado
def construir_arbol(expresion_regular):
    pila_tokens = Pila()  # Pila de operadores (T)
    pila_arboles = Pila()  # Pila de árboles (S)

    tokens = tokenizar_expresion(expresion_regular)  # Tokenizamos la expresión

    # Iteramos sobre cada token en la expresión regular
    for token in tokens:
        if re.match(r'[a-zA-Z]\d*', token):  # Si es un símbolo terminal (st)
            nuevo_nodo = Nodo(token)
            pila_arboles.push(nuevo_nodo)

        elif token == '(':  # Si el token es un paréntesis de apertura
            pila_tokens.push(token)

        elif token == ')':  # Si el token es un paréntesis de cierre
            while not pila_tokens.esta_vacia() and pila_tokens.peek() != '(':
                operador = pila_tokens.pop()

                if pila_arboles.esta_vacia():
                    raise Exception("Error: Faltan operandos para el operador")

                # Procesar operador
                nodo = Nodo(operador)

                if operador == '*':  # Si el operador es unario
                    nodo.izquierdo = pila_arboles.pop()
                else:  # Si es binario
                    nodo.derecho = pila_arboles.pop()
                    if pila_arboles.esta_vacia():
                        raise Exception("Error: Faltan operandos para el operador")
                    nodo.izquierdo = pila_arboles.pop()

                pila_arboles.push(nodo)
            pila_tokens.pop()  # Quitar el paréntesis de apertura

        elif es_operador(token):  # Si es un operador
            while not pila_tokens.esta_vacia() and pila_tokens.peek() != '(' and precedencia(pila_tokens.peek()) >= precedencia(token):
                operador = pila_tokens.pop()

                nodo = Nodo(operador)

                if operador == '*':  # Operador unario
                    nodo.izquierdo = pila_arboles.pop()
                else:  # Operadores binarios
                    nodo.derecho = pila_arboles.pop()
                    nodo.izquierdo = pila_arboles.pop()

                pila_arboles.push(nodo)

            pila_tokens.push(token)  # Añadir el operador actual a la pila

        else:
            raise Exception(f"Token no reconocido: {token}")

    # Procesar los operadores restantes
    while not pila_tokens.esta_vacia():
        operador = pila_tokens.pop()

        if pila_arboles.esta_vacia():
            raise Exception("Error: Faltan operandos para el operador")

        nodo = Nodo(operador)

        if operador == '*':
            nodo.izquierdo = pila_arboles.pop()
        else:
            nodo.derecho = pila_arboles.pop()
            nodo.izquierdo = pila_arboles.pop()

        pila_arboles.push(nodo)

    # Al final, debería quedar un solo árbol en la pila
    if len(pila_arboles.items) != 1:
        raise Exception("Error: Expresión incorrecta, operandos faltantes")

    return pila_arboles.pop()

# Función para imprimir el árbol de expresión en forma visual con mayor claridad
def imprimir_arbol_ordenado(nodo, prefijo="", es_izquierdo=True):
    if nodo is not None:
        imprimir_arbol_ordenado(nodo.derecho, prefijo + ("│   " if es_izquierdo else "    "), False)
        print(prefijo + ("└── " if es_izquierdo else "┌── ") + nodo.valor)
        imprimir_arbol_ordenado(nodo.izquierdo, prefijo + ("    " if es_izquierdo else "│   "), True)

# Ejemplo de uso con una expresión regular combinada con números
expresion = "(a1.a1*).b2|(w2.a2.w2|m2.a2.m2).b3|(o1).c2|(v1.v2).c3|(v1).d1|(v2).d2|(v2.o1).d3|(v1.o1).e1|(v3).e2|(w1).e3|(q2.o3).f1|(s2).f2|(p1.r3.q3).f3|(q1.q2.q3).g1|(q3.r1.r2).g2|(r3.q2.s1).g3|(s3.s2).h1|(s2.t1).h2|(n3).h3|(u3).i1|(u1).i2|(u2).i3|(s3).j1|(t1).j2|(t2).j3|(t3).k1|(u3.u3).k2|(n1).k3|(n2).l1|(n1.o1).l2|(a3.(a3|a1)*b1.()).c1"

# Construimos el árbol a partir de la expresión
arbol = construir_arbol(expresion)

# Imprimimos el árbol para visualizarlo de manera más ordenada
imprimir_arbol_ordenado(arbol)
