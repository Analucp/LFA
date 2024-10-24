import re
import string

# Función para leer el archivo de gramática
def leer_archivo(ruta_archivo):
    try:
        with open(ruta_archivo, 'r') as archivo:
            return archivo.read()  # Devuelve el contenido del archivo como string
    except FileNotFoundError:
        print(f"El archivo {ruta_archivo} no se encontró.")
        return None  # Retorna None en caso de error
    except Exception as e:
        print(f"Ocurrió un error: {e}")
        return None  # Retorna None en caso de otro error

# Lista de terminales (incluyendo aquellos que están entre comillas simples y dobles)
terminales = [
    'DIGITO', 'CHARSET', 'LETRA', 'RESERVADAS', 'T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9', 
    'T10', 'T11', 'T12', 'T13', 'T14', 'T15', 'T16', 'T17', 'T40', 'T41', 'T42', 'T43', 'T44', 'T45', 'T46', 'T47', 'T48', 'T49', 'T50', 'T51', 'T52', 'T53',
    "'", '"', "'''", "' '", "':'", "','", "';'", "'='", "'O'", "'R'", "'A'", "'N'", "'D'", "'M'", "'O'", "'D'", "'I'", "'V'", "'N'", "'T'", "'*'", "'('", "')'", "'['", "']'", "'{'", "'}'", "'.'", "'<'", "'>'", "'+'", "'-'"
]

# Incluyendo el terminal completo `'"'`
terminales.append('\'"\'')

# Crear un mapa de letras con tres combinaciones por cada letra (a1, a2, a3, b1, b2, b3, etc.)
def generar_mapa_letras(terminales):
    letras = string.ascii_lowercase
    combinaciones = [f"{letra}{i}" for letra in letras for i in range(1, 4)]  # Generar combinaciones a1, a2, a3, b1, b2, b3, etc.
    return dict(zip(terminales, combinaciones))

mapa_letras = generar_mapa_letras(terminales)

# Lista de operadores: Solo los que NO están entre comillas simples o dobles
operadores = ['(', '*', ')', '|']

# Función para agregar concatenaciones donde sea necesario
def agregar_concatenaciones(expresion):
    resultado = []
    partes = re.findall(r"'''|\"[^\"]*\"|\'[^\']*\'|[\w]+|[.,!?;*()|]", expresion)  # Detecta todo lo que está entre comillas como un solo token
    
    for i in range(len(partes) - 1):
        resultado.append(partes[i])
        # Reglas de concatenación:
        # 1. Concatenar entre dos terminales.
        # 2. Concatenar entre un terminal y un paréntesis de apertura "(".
        # 3. No concatenar entre operadores (excepto después de "(" o antes de ")" si están rodeados de terminales).
        if (partes[i] in terminales or partes[i].startswith("'") or partes[i].startswith('"')) and \
           (partes[i + 1] in terminales or partes[i + 1].startswith("'") or partes[i + 1].startswith('"') or partes[i + 1] == '('):
            resultado.append('.')  # Añadir el símbolo de concatenación
    resultado.append(partes[-1])  # Agregar la última parte

    # Aquí se remueven los espacios en blanco
    return ''.join(resultado)  # Unir todo sin espacios en blanco

# Función para convertir los terminales en letras del abecedario con números (a1, a2, a3, etc.)
def convertir_a_letras(expresion):
    partes = re.findall(r"'''|\"[^\"]*\"|\'[^\']*\'|[\w]+|[.,!?;*()|]", expresion)  # Reconoce comillas simples y dobles
    resultado = []
    
    for parte in partes:
        if parte in mapa_letras:
            resultado.append(mapa_letras[parte])  # Reemplaza el terminal por la letra con número
        else:
            resultado.append(parte)  # Deja operadores y otros caracteres igual
    
    return ''.join(resultado)

# Función para extraer las expresiones regulares de todos los tokens con sus identificadores
def extraer_expresion_regular(texto):
    tokens_matches = re.findall(regex_tokens, texto)
    return tokens_matches if tokens_matches else None

# Expresión regular para extraer todos los tokens y sus números
regex_tokens = r"TOKEN\s+(\d+)\s*=\s*(.*)"

# Función para guardar los tokens extraídos en una sola línea, sin espacios en blanco, separados por "|"
def guardar_expresion_regular_tokens(ruta_salida, tokens_extraidos):
    try:
        with open(ruta_salida, 'w') as archivo_salida:
            # Crear una lista con los tokens en el formato (expresión con concatenaciones) . Tn
            tokens_formateados = [f'({agregar_concatenaciones(expresion_token.strip())}).T{numero_token}' for numero_token, expresion_token in tokens_extraidos]
            # Unir todos los tokens con el separador "|" sin espacios en blanco
            expresion_original = "|".join(tokens_formateados)
            archivo_salida.write(expresion_original + '\n\n')  # Agregar espacio en blanco entre las expresiones

            # Convertir a la versión con letras del abecedario y números
            expresion_letras = convertir_a_letras(expresion_original)
            archivo_salida.write(expresion_letras + '\n\n')  # Guardar la versión con letras

            # Guardar la guía de correspondencias entre terminales y letras
            archivo_salida.write("Guia de correspondencias (Terminal -> Letra):\n")
            for terminal, letra in mapa_letras.items():
                archivo_salida.write(f"{terminal} -> {letra}\n")
        print(f"Tokens guardados exitosamente en {ruta_salida}")
    except Exception as e:
        print(f"Ocurrió un error al intentar guardar el archivo: {e}")

# Leer el archivo de gramática y extraer los tokens
ruta_gramatica = 'C:/Users/Usuario/Downloads/prueba_2-1 (2).txt'  # Aquí puedes colocar la ruta de tu archivo
contenido_gramatica = leer_archivo(ruta_gramatica)

# Definir la ruta de salida del archivo
ruta_salida = 'C:/Users/Usuario/Downloads/salidatokens.txt'  # Aquí puedes cambiar el nombre o ruta del archivo de salida

# Si se extrajo correctamente la sección de tokens, se guarda en el archivo
if contenido_gramatica:
    tokens_extraidos = extraer_expresion_regular(contenido_gramatica)
    if tokens_extraidos:
        guardar_expresion_regular_tokens(ruta_salida, tokens_extraidos)
    else:
        print("No se encontraron tokens para guardar.")
else:
    print("No se pudo leer el archivo de gramática.")



