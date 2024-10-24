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

# Función para verificar si es un terminal válido (letras seguidas de números, e.g., a1, b2, etc.)
def es_terminal(token):
    return re.match(r'^[a-zA-Z][0-9]*$', token)

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

    tokens = re.findall(r'[a-zA-Z][0-9]*|[|.*()]{1}', expresion_regular)  # Extraemos los tokens correctamente
    for token in tokens:
        if es_terminal(token):  # Si es un símbolo terminal
            nodo = Nodo(token)
            pila_arboles.append(nodo)
        elif token == '(':
            pila_tokens.append(token)
        elif token == ')':
            while pila_tokens and pila_tokens[-1] != '(':
                operador = pila_tokens.pop() if pila_tokens else None
                if operador:
                    nodo = Nodo(operador)

                    if operador == '*':  # Operador unario
                        if pila_arboles:
                            nodo.izquierdo = pila_arboles.pop()
                    else:  # Operadores binarios
                        if len(pila_arboles) >= 2:
                            nodo.derecho = pila_arboles.pop()
                            nodo.izquierdo = pila_arboles.pop()

                    pila_arboles.append(nodo)
            if pila_tokens:
                pila_tokens.pop()  # Quitar el '('
        elif es_operador(token):
            while (pila_tokens and pila_tokens[-1] != '(' and
                   precedencia(pila_tokens[-1]) >= precedencia(token)):
                operador = pila_tokens.pop() if pila_tokens else None
                if operador:
                    nodo = Nodo(operador)

                    if operador == '*':
                        if pila_arboles:
                            nodo.izquierdo = pila_arboles.pop()
                    else:
                        if len(pila_arboles) >= 2:
                            nodo.derecho = pila_arboles.pop()
                            nodo.izquierdo = pila_arboles.pop()

                    pila_arboles.append(nodo)
            pila_tokens.append(token)

    while pila_tokens:
        operador = pila_tokens.pop()
        nodo = Nodo(operador)

        if operador == '*':
            if pila_arboles:
                nodo.izquierdo = pila_arboles.pop()
        else:
            if len(pila_arboles) >= 2:
                nodo.derecho = pila_arboles.pop()
                nodo.izquierdo = pila_arboles.pop()

        pila_arboles.append(nodo)

    arbol_final = pila_arboles.pop() if pila_arboles else None
    if arbol_final:  # Verificamos que no sea None
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
        nodo.first = nodo.izquierdo.first.union(nodo.derecho.first) if nodo.izquierdo and nodo.derecho else set()
        nodo.last = nodo.izquierdo.last.union(nodo.derecho.last) if nodo.izquierdo and nodo.derecho else set()
        nodo.nullable = (nodo.izquierdo.nullable if nodo.izquierdo else False) or (nodo.derecho.nullable if nodo.derecho else False)
    elif nodo.valor == '.':
        if nodo.izquierdo and nodo.derecho:
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
        else:
            nodo.first = nodo.last = set()
            nodo.nullable = False
    elif nodo.valor == '*':
        if nodo.izquierdo:
            nodo.first = nodo.izquierdo.first
            nodo.last = nodo.izquierdo.last
            nodo.nullable = True

            # Follow para *
            for i in nodo.last:
                follow_dict[i].update(nodo.first)

# Generar tabla de transiciones
def generar_tabla_transiciones(arbol, follow_dict, total_hojas):
    estados = []
    transiciones = {}
    simbolos_hoja = {nodo.numero_hoja: nodo.valor for nodo in obtener_hojas(arbol)}

    # Estado S0 es el first del nodo raíz
    S0 = arbol.first
    if S0:
        estados.append(S0)
        transiciones[tuple(S0)] = {simbolo: set() for simbolo in simbolos_hoja.values()}

    # Expandir el resto de los estados
    for estado in estados:
        for simbolo in simbolos_hoja.values():
            transicion = set()
            for pos in estado:
                if simbolos_hoja[pos] == simbolo:
                    transicion.update(follow_dict[pos])

            if transicion and tuple(transicion) not in transiciones:
                estados.append(transicion)
                transiciones[tuple(transicion)] = {simbolo: set() for simbolo in simbolos_hoja.values()}

            transiciones[tuple(estado)][simbolo] = transicion

    return transiciones, estados

# Guardar la tabla en un archivo .txt con los terminales como encabezados
def guardar_tabla_en_txt(transiciones, estados, simbolos_hoja, archivo_txt):
    with open(archivo_txt, 'w') as archivo:
        # Escribir encabezado con los terminales
        terminales = sorted(simbolos_hoja.values())
        archivo.write(f"{'Estado':<50} " + " ".join(f"{terminal:<50}" for terminal in terminales) + "\n")
        archivo.write("-" * (50 + len(terminales) * 51) + "\n")

        # Escribir los estados y las transiciones
        for i, estado in enumerate(estados):
            estado_str = f"S{i}={str(sorted(estado))}"  # Usamos sorted(estado) y str() para evitar las dobles llaves
            transiciones_str = " ".join(f"{str(sorted(list(transiciones[tuple(estado)][simbolo]))):<50}" 
                                        for simbolo in terminales)
            archivo.write(f"{estado_str:<50} {transiciones_str}\n")

# Obtener todos los nodos hoja del árbol
def obtener_hojas(nodo):
    if nodo is None:
        return []
    if nodo.numero_hoja is not None:
        return [nodo]
    return obtener_hojas(nodo.izquierdo) + obtener_hojas(nodo.derecho)

# Ejemplo de uso
expresion = "(a1.a1*).b2|(w2.a2.w2|m2.a2.m2).b3|(o1).c2|(v1.v2).c3|(v1).d1|(v2).d2|(v2.o1).d3|(v1.o1).e1|(v3).e2|(w1).e3|(q2.o3).f1|(s2).f2|(p1.r3.q3).f3|(q1.q2.q3).g1|(q3.r1.r2).g2|(r3.q2.s1).g3|(s3.s2).h1|(s2.t1).h2|(n3).h3|(u3).i1|(u1).i2|(u2).i3|(s3).j1|(t1).j2|(t2).j3|(t3).k1|(u3.u3).k2|(n1).k3|(n2).l1|(n1.o1).l2|(a3.(a3|a1)*b1.()).c1"
print(f"Expresión a procesar: {expresion}")

# Construir árbol y calcular conjuntos
arbol, total_hojas = construir_arbol(expresion)
follow_dict = {i: set() for i in range(1, total_hojas + 1)}

if arbol:  # Verificamos que no sea None
    calcular_conjuntos(arbol, follow_dict)

    # Generar la tabla de transiciones
    transiciones, estados = generar_tabla_transiciones(arbol, follow_dict, total_hojas)

    # Obtener los símbolos hoja
    simbolos_hoja = {nodo.numero_hoja: nodo.valor for nodo in obtener_hojas(arbol)}

    # Guardar la tabla de transiciones en un archivo de texto
    ruta_salida_txt = 'C:/Users/Usuario/Downloads/tablaTRANSICIONES.txt'
    guardar_tabla_en_txt(transiciones, estados, simbolos_hoja, ruta_salida_txt)

    print(f"Tabla de transiciones guardada exitosamente en {ruta_salida_txt}")
else:
    print("Error: No se pudo construir el árbol a partir de la expresión.")


