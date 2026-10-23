import re
import json
from datetime import datetime   # solo se usa para averiguar la fecha actual

# ======================================================================
# Sistema de gestion de inventarios - TPO Grupo 2
#
# Los datos NUNCA se cargan completos en memoria: cada operacion abre el
# archivo, lo recorre REGISTRO POR REGISTRO y lo cierra. Para volver a
# recorrer un archivo ya abierto se usa seek(0). Para modificar o borrar un
# lote se graba una version modificada en un archivo auxiliar y despues se
# copia el auxiliar de vuelta al original.
#
# Archivos en formato JSON Lines (un objeto JSON por linea):
#   - inventario.jsonl: un diccionario por lote
#     {"codigo", "vence", "categoria", "nombre", "costo", "cantidad"}
#   - historial.jsonl: una lista por movimiento
#     [codigo, categoria, nombre, fecha, tipo, cantidad, costo, total, detalle]
#
# Estructuras de datos usadas:
#   - TUPLAS: la clave de cada lote (codigo, vencimiento), las fechas
#     (anio, mes, dia), que se comparan directamente, las categorias y el menu.
#   - DICCIONARIOS: los datos de cada lote que se lee del archivo.
#   - MATRIZ (lista de listas): los totales por categoria en las estadisticas
#     y los datos iniciales del historial.
#   - CONJUNTOS: las categorias con productos y los codigos distintos.
#   - EXCEPCIONES: try/except al convertir numeros, try/except/finally al
#     abrir, leer, grabar y cerrar archivos, lineas con formato incorrecto
#     y la interrupcion con Ctrl+C. Ademas, pruebas con assert al iniciar.
#   - RECURSIVIDAD: la suma de dias a una fecha (vencimientos) y la
#     valorizacion del inventario, que lee el archivo con readline.
# ======================================================================

# Categorias definidas: el usuario elige por numero, no las escribe
CATEGORIAS = ("lacteos", "limpieza", "conservas", "almacen", "bebidas", "higiene")

# Archivos donde se guardan los datos (se crean en la carpeta desde donde se ejecuta el programa)
ARCHIVO_INVENTARIO = "inventario.jsonl"
ARCHIVO_HISTORIAL = "historial.jsonl"
ARCHIVO_AUXILIAR = "inventario_aux.jsonl"

# Maximo de dias a futuro para revisar vencimientos (limita la profundidad de la recursion,
# que en Python es de unas 1000 llamadas)
MAX_DIAS = 3650

# ----------------------------------------------------------------------
# Funciones de impresion (formato de tablas)
# ----------------------------------------------------------------------
ANCHO = 90

def linea(caracter="="):
    """Devuelve una linea horizontal del ancho de la tabla"""
    return caracter * ANCHO

def imprimir_titulo(texto):
    """Imprime un titulo centrado entre dos lineas"""
    print()
    print(linea("="))
    print(texto.upper().center(ANCHO))
    print(linea("="))

def recortar(texto, largo):
    """Recorta un texto largo agregando '...' para que no desalinee la tabla"""
    texto = str(texto)
    if len(texto) > largo:
        return texto[:largo - 3] + "..."
    return texto

def imprimir_encabezado_lotes():
    """Imprime los titulos de las columnas de la tabla de lotes"""
    print("CODIGO".ljust(11) + "CATEGORIA".ljust(12) + "NOMBRE".ljust(38) + "VENCE".ljust(12) + "COSTO".rjust(9) + "CANT.".rjust(8))
    print(linea("-"))

def imprimir_lote(clave, datos):
    """Imprime un lote como una fila de la tabla"""
    print(clave[0].ljust(11)
          + recortar(datos["categoria"].capitalize(), 11).ljust(12)
          + recortar(datos["nombre"], 36).ljust(38)
          + clave[1].ljust(12)
          + f"${datos['costo']}".rjust(9)
          + str(datos["cantidad"]).rjust(8))

# ----------------------------------------------------------------------
# Funciones de fechas (sin usar datetime para parsear ni comparar)
# ----------------------------------------------------------------------
def fecha_hoy():
    """Devuelve la fecha actual como texto AAAA/MM/DD (se consulta en cada operacion)"""
    return str(datetime.now())[:10].replace("-", "/")

def dias_en_mes(mes, anio):
    """Devuelve la cantidad de dias que tiene un mes de un anio determinado"""
    if mes in (1, 3, 5, 7, 8, 10, 12):
        return 31
    elif mes in (4, 6, 9, 11):
        return 30
    elif (anio % 4 == 0 and anio % 100 != 0) or anio % 400 == 0:
        return 29
    return 28

def fecha_a_tupla(fecha):
    """Convierte un texto AAAA/MM/DD en una tupla (anio, mes, dia) de numeros"""
    anio, mes, dia = fecha.split("/")
    return (int(anio), int(mes), int(dia))

def fecha_valida(fecha):
    """Devuelve True si el texto tiene formato AAAA/MM/DD (regex) y la fecha existe en el calendario"""
    if re.search("^[0-9][0-9][0-9][0-9]/[0-9][0-9]/[0-9][0-9]$", fecha) == None:
        return False
    anio, mes, dia = fecha_a_tupla(fecha)
    return mes >= 1 and mes <= 12 and dia >= 1 and dia <= dias_en_mes(mes, anio)

def sumar_dias(anio, mes, dia, dias):
    """Suma 'dias' a una fecha de forma RECURSIVA y devuelve la tupla (anio, mes, dia).
    Caso base: los dias a sumar entran en el mes actual.
    Caso recursivo: se pasa al dia 1 del mes siguiente y se llama a si misma con los dias que faltan."""
    if dia + dias <= dias_en_mes(mes, anio):
        return (anio, mes, dia + dias)
    dias_restantes = dias - (dias_en_mes(mes, anio) - dia + 1)
    if mes == 12:
        return sumar_dias(anio + 1, 1, 1, dias_restantes)
    return sumar_dias(anio, mes + 1, 1, dias_restantes)

def fecha_proxima_a_vencer(hoy, dias):
    """Calcula la fecha limite (anio, mes, dia) sumando 'dias' a la fecha de hoy"""
    anio, mes, dia = fecha_a_tupla(hoy)
    return sumar_dias(anio, mes, dia, dias)

# ----------------------------------------------------------------------
# Funciones de validacion de datos ingresados
# ----------------------------------------------------------------------
def validar_no_es_vacio(cadena):
    """Valida que la cadena ingresada no este vacia (ni solo espacios)"""
    cadena = cadena.strip()
    while cadena == "":
        cadena = input("El valor no puede estar vacio. Ingrese nuevamente: ").strip()
    return cadena

def validar_numero(numero):
    """Valida que el numero ingresado sea entero y positivo, y lo devuelve como int.
    Si int() no puede convertir el texto se produce un ValueError, que se atrapa y se vuelve a pedir."""
    while True:
        try:
            valor = int(numero)
            if valor > 0:
                return valor
            print("El numero debe ser mayor a cero.")
        except ValueError:
            print("Debe ingresar un numero entero.")
        numero = input("Ingrese un numero positivo y valido: ")

def validar_codigo(codigo):
    """Valida que el codigo tenga exactamente 9 digitos (usa expresion regular)"""
    codigo = validar_no_es_vacio(codigo)
    while re.search("^[0-9]+$", codigo) == None or len(codigo) != 9:
        codigo = input("Ingrese un codigo de nueve (9) digitos numericos: ").strip()
    return codigo

def validar_nombre(nombre):
    """Valida que el nombre tenga al menos una letra o un numero (usa expresion regular)"""
    nombre = validar_no_es_vacio(nombre)
    while re.search("[A-Za-z0-9ÁÉÍÓÚáéíóúÑñ]", nombre) == None:
        nombre = input("El nombre debe tener letras o numeros. Ingrese nuevamente: ").strip()
    return nombre

def validar_fecha_actual(fecha):
    """Valida que la fecha sea AAAA/MM/DD, que exista y que no sea una fecha pasada"""
    hoy = fecha_hoy()
    fecha = validar_no_es_vacio(fecha)
    while True:
        if not fecha_valida(fecha):
            print("La fecha no es valida (formato AAAA/MM/DD y debe existir en el calendario).")
        elif fecha_a_tupla(fecha) < fecha_a_tupla(hoy):
            print("La fecha ingresada ya paso.")
        else:
            return fecha
        fecha = input("Ingrese nuevamente (AAAA/MM/DD): ").strip()

def elegir_categoria(permitir_todas=False):
    """Muestra las categorias definidas y devuelve la elegida por numero.
    Si permitir_todas es True, el 0 devuelve '' (sin filtro)."""
    for i, categoria in enumerate(CATEGORIAS):
        print("   " + str(i + 1).rjust(2) + ".  " + categoria.capitalize())
    if permitir_todas:
        print("    0.  Todas")
    minimo = 1
    if permitir_todas:
        minimo = 0
    texto = input("Ingrese el numero de la categoria: ")
    while True:
        try:
            numero = int(texto)
            if numero >= minimo and numero <= len(CATEGORIAS):
                break
        except ValueError:
            pass
        texto = input("Numero invalido. Ingrese un numero de la lista: ")
    if numero == 0:
        return ""
    return CATEGORIAS[numero - 1]

# ----------------------------------------------------------------------
# Datos iniciales: se graban en los archivos solo si todavia no existen
# ----------------------------------------------------------------------
def crear_inventario():
    """Devuelve los lotes iniciales (diccionario: (codigo, vence) -> datos del lote)"""
    return {
        ("123456789", "2027/12/30"): {"categoria": "lacteos",   "nombre": "Leche entera La Serenisima por 1l",   "costo": 3000, "cantidad": 200},
        ("123456789", "2026/11/15"): {"categoria": "lacteos",   "nombre": "Leche entera La Serenisima por 1l",   "costo": 3000, "cantidad": 60},
        ("987654321", "2026/09/20"): {"categoria": "lacteos",   "nombre": "Queso muzzarela La Blanca por 500gm", "costo": 7000, "cantidad": 120},
        ("579246813", "2028/12/05"): {"categoria": "limpieza",  "nombre": "Desinfectante Lysoform por 360ml",    "costo": 4200, "cantidad": 70},
        ("813579246", "2028/11/20"): {"categoria": "conservas", "nombre": "Pure de tomate Arcor por 520gm",      "costo": 1900, "cantidad": 150},
        ("369258147", "2026/10/08"): {"categoria": "lacteos",   "nombre": "Crema de leche Tregar por 200ml",     "costo": 2200, "cantidad": 90},
        ("246813579", "2029/01/20"): {"categoria": "limpieza",  "nombre": "Detergente Magistral por 750ml",      "costo": 2800, "cantidad": 100},
        ("753159456", "2028/03/25"): {"categoria": "almacen",   "nombre": "Azucar Ledesma por 1kg",              "costo": 1700, "cantidad": 210},
        ("135792468", "2028/09/15"): {"categoria": "limpieza",  "nombre": "Lavandina Ayudin por 1l",             "costo": 1800, "cantidad": 130}
    }

def crear_historial():
    """Devuelve los movimientos iniciales (matriz: una fila por movimiento, ordenadas por fecha).
    Orden de cada fila:
    [codigo, categoria, nombre, fecha, tipo, cantidad, costo unitario, costo total, detalle]
    tipo: ALTA, BAJA o MODIF. La cantidad es positiva en las altas y negativa en las bajas."""
    return [["987654321", "lacteos",   "Queso muzzarela La Blanca por 500gm", "2026/03/20", "BAJA", -20, 7000, 140000, ""],
            ["753159456", "almacen",   "Azucar Ledesma por 1kg",              "2026/06/25", "ALTA", 100, 1700, 170000, ""],
            ["369258147", "lacteos",   "Crema de leche Tregar por 200ml",     "2026/07/18", "ALTA", 50, 2200, 110000, ""],
            ["123456789", "lacteos",   "Leche entera La Serenisima por 1l",   "2026/07/30", "ALTA", 200, 3000, 600000, ""],
            ["813579246", "conservas", "Pure de tomate Arcor por 520gm",      "2026/08/05", "BAJA", -20, 1900, 38000, ""],
            ["123456789", "lacteos",   "Leche entera La Serenisima por 1l",   "2026/08/10", "ALTA", 60, 3000, 180000, ""],
            ["579246813", "limpieza",  "Desinfectante Lysoform por 360ml",    "2026/08/12", "ALTA", 50, 4200, 210000, ""],
            ["135792468", "limpieza",  "Lavandina Ayudin por 1l",             "2026/08/15", "ALTA", 50, 1800, 90000, ""],
            ["246813579", "limpieza",  "Detergente Magistral por 750ml",      "2026/08/20", "BAJA", -20, 2800, 56000, ""]]


# ----------------------------------------------------------------------
# Conversion de registros (JSON Lines)
# ----------------------------------------------------------------------
def lote_a_linea(clave, datos):
    """Convierte un lote en una linea JSON para el archivo de inventario"""
    registro = {"codigo": clave[0], "vence": clave[1], "categoria": datos["categoria"],
                "nombre": datos["nombre"], "costo": datos["costo"], "cantidad": datos["cantidad"]}
    return json.dumps(registro) + "\n"

def linea_a_lote(linea_archivo):
    """Convierte una linea JSON del inventario en una tupla (clave, datos).
    Si la linea tiene un formato incorrecto devuelve None."""
    try:
        registro = json.loads(linea_archivo)
        for campo in ("codigo", "vence", "categoria", "nombre", "costo", "cantidad"):
            if campo not in registro:
                raise ValueError("Falta el campo " + campo)
        clave = (registro["codigo"], registro["vence"])
        datos = {"categoria": registro["categoria"], "nombre": registro["nombre"],
                 "costo": int(registro["costo"]), "cantidad": int(registro["cantidad"])}
        return (clave, datos)
    except (ValueError, TypeError):
        print(f">> Se ignoro un registro con formato incorrecto en '{ARCHIVO_INVENTARIO}'.")
        return None

def movimiento_a_linea(movimiento):
    """Convierte un movimiento (lista de 9 campos) en una linea JSON para el historial"""
    return json.dumps(movimiento) + "\n"

def linea_a_movimiento(linea_archivo):
    """Convierte una linea JSON del historial en una lista de 9 campos. Si tiene formato incorrecto devuelve None."""
    try:
        movimiento = json.loads(linea_archivo)
        if len(movimiento) != 9:
            raise ValueError("El movimiento no tiene 9 campos")
        return movimiento
    except (ValueError, TypeError):
        print(f">> Se ignoro un registro con formato incorrecto en '{ARCHIVO_HISTORIAL}'.")
        return None

# ----------------------------------------------------------------------
# Funciones de archivos
# ----------------------------------------------------------------------
def crear_archivo_inicial(nombre_archivo, lineas):
    """Graba un archivo con una lista de lineas (se usa solo para los datos iniciales)"""
    try:
        arch = open(nombre_archivo, "wt")
        arch.writelines(lineas)
    except OSError as mensaje:
        print("No se puede grabar el archivo:", mensaje)
    finally:
        try:
            arch.close()
        except NameError:
            pass

def inicializar_archivos():
    """Si los archivos no existen, los crea con los datos iniciales"""
    try:
        arch = open(ARCHIVO_INVENTARIO, "rt")
        arch.close()
    except FileNotFoundError:
        print(f">> No se encontro '{ARCHIVO_INVENTARIO}'. Se crea con los datos iniciales.")
        inventario_inicial = crear_inventario()
        lineas = []
        for clave in inventario_inicial:
            lineas.append(lote_a_linea(clave, inventario_inicial[clave]))
        crear_archivo_inicial(ARCHIVO_INVENTARIO, lineas)
    try:
        arch = open(ARCHIVO_HISTORIAL, "rt")
        arch.close()
    except FileNotFoundError:
        print(f">> No se encontro '{ARCHIVO_HISTORIAL}'. Se crea con los datos iniciales.")
        lineas = []
        for movimiento in crear_historial():
            lineas.append(movimiento_a_linea(movimiento))
        crear_archivo_inicial(ARCHIVO_HISTORIAL, lineas)

def copiar_archivo(origen, destino):
    """Copia un archivo en otro registro por registro. Devuelve True si se pudo copiar"""
    exito = False
    try:
        entrada = open(origen, "rt")
        salida = open(destino, "wt")
        for linea_archivo in entrada:
            salida.write(linea_archivo)
        exito = True
    except FileNotFoundError as mensaje:
        print("No se puede abrir el archivo:", mensaje)
    except OSError as mensaje:
        print("ERROR:", mensaje)
    finally:
        try:
            entrada.close()
            salida.close()
        except NameError:
            pass
    return exito

# ----------------------------------------------------------------------
# Funciones que recorren un archivo de inventario ya abierto.
# Empiezan con seek(0) para poder recorrerlo varias veces sin reabrirlo.
# ----------------------------------------------------------------------
def cumple_filtro(clave, datos, tipo_filtro, valor):
    """Devuelve True si el lote cumple el filtro pedido:
    'codigo' y 'categoria': igual al valor; 'texto': el valor aparece en codigo, vencimiento, nombre o categoria;
    'vencidos': vence antes de la fecha valor; 'proximos': vence entre las dos fechas de la tupla valor."""
    if tipo_filtro == "codigo":
        return clave[0] == valor
    elif tipo_filtro == "categoria":
        return datos["categoria"] == valor
    elif tipo_filtro == "texto":
        return valor in clave[0] or valor in clave[1] or valor in datos["nombre"].lower() or valor in datos["categoria"]
    elif tipo_filtro == "vencidos":
        return fecha_a_tupla(clave[1]) < valor
    elif tipo_filtro == "proximos":
        return fecha_a_tupla(clave[1]) >= valor[0] and fecha_a_tupla(clave[1]) <= valor[1]
    return False

def listar_lotes(arch, tipo_filtro, valor, mensaje_vacio):
    """Recorre el inventario e imprime en una tabla los lotes que cumplen el filtro (ver cumple_filtro).
    Devuelve la cantidad de unidades de los lotes listados."""
    arch.seek(0)
    lotes = 0
    unidades = 0
    for linea_archivo in arch:
        lote = linea_a_lote(linea_archivo)
        if lote != None and cumple_filtro(lote[0], lote[1], tipo_filtro, valor):
            if lotes == 0:
                imprimir_encabezado_lotes()
            imprimir_lote(lote[0], lote[1])
            lotes = lotes + 1
            unidades = unidades + lote[1]["cantidad"]
    if lotes == 0:
        print(mensaje_vacio)
    else:
        print(linea("-"))
        print(f"Total de lotes listados: {lotes}")
    return unidades

def buscar_lote(arch, clave):
    """Busca un lote por su clave (codigo, vence). Devuelve sus datos o None si no existe"""
    arch.seek(0)
    for linea_archivo in arch:
        lote = linea_a_lote(linea_archivo)
        if lote != None and lote[0] == clave:
            return lote[1]
    return None

def buscar_codigo(arch, codigo):
    """Devuelve una tupla (cantidad de lotes del codigo, clave del ultimo, datos del ultimo)"""
    arch.seek(0)
    cantidad = 0
    clave = None
    datos = None
    for linea_archivo in arch:
        lote = linea_a_lote(linea_archivo)
        if lote != None and lote[0][0] == codigo:
            cantidad = cantidad + 1
            clave = lote[0]
            datos = lote[1]
    return (cantidad, clave, datos)

def obtener_categorias(arch):
    """Devuelve un conjunto con las categorias que tienen productos (sin repetidos)"""
    arch.seek(0)
    categorias = set()
    for linea_archivo in arch:
        lote = linea_a_lote(linea_archivo)
        if lote != None:
            categorias.add(lote[1]["categoria"])
    return categorias

def valor_desde_archivo(arch):
    """Calcula de forma RECURSIVA el valor (costo x cantidad) de los lotes que quedan por leer en el archivo.
    Caso base: no hay mas registros (readline devuelve ''), vale 0.
    Caso recursivo: el valor del lote leido mas el valor del resto del archivo."""
    linea_archivo = arch.readline()
    if linea_archivo == "":
        return 0
    lote = linea_a_lote(linea_archivo)
    if lote == None:
        return valor_desde_archivo(arch)
    return lote[1]["costo"] * lote[1]["cantidad"] + valor_desde_archivo(arch)

# ----------------------------------------------------------------------
# Funciones que graban en los archivos
# ----------------------------------------------------------------------
def registrar_movimiento(arch_historial, clave, producto, tipo, cantidad, detalle=""):
    """Graba un movimiento con la fecha de hoy en el historial (que llega abierto en modo 'at')"""
    movimiento = [clave[0], producto["categoria"], producto["nombre"], fecha_hoy(), tipo,
                  cantidad, producto["costo"], producto["costo"] * abs(cantidad), detalle]
    arch_historial.write(movimiento_a_linea(movimiento))

def actualizar_inventario(codigo, vence, campo, nuevo_valor, tipo):
    """Cambia un campo ('categoria', 'costo' o 'cantidad') de los lotes de un codigo.
    Si vence es '' se cambian todos los lotes del codigo; si no, solo el lote de ese vencimiento.
    Graba una version modificada del inventario en el archivo auxiliar y despues la copia al original.
    Si la cantidad queda en 0, el lote no se graba (se elimina). Cada cambio se registra en el historial."""
    exito = False
    try:
        original = open(ARCHIVO_INVENTARIO, "rt")
        auxiliar = open(ARCHIVO_AUXILIAR, "wt")
        historial = open(ARCHIVO_HISTORIAL, "at")
        for linea_archivo in original:
            lote = linea_a_lote(linea_archivo)
            if lote != None:
                clave, datos = lote
                if clave[0] == codigo and (vence == "" or clave[1] == vence):
                    anterior = datos[campo]
                    datos[campo] = nuevo_valor
                    cantidad_movida = 0
                    detalle = ""
                    if campo == "cantidad":
                        cantidad_movida = nuevo_valor - anterior
                    if tipo == "MODIF" and campo == "costo":
                        detalle = f"Costo: ${anterior} -> ${nuevo_valor}"
                    elif tipo == "MODIF":
                        detalle = f"{campo.capitalize()}: {anterior} -> {nuevo_valor}"
                    registrar_movimiento(historial, clave, datos, tipo, cantidad_movida, detalle)
                if datos["cantidad"] > 0:
                    auxiliar.write(lote_a_linea(clave, datos))
        exito = True
    except FileNotFoundError as mensaje:
        print("No se puede abrir el archivo:", mensaje)
    except OSError as mensaje:
        print("ERROR:", mensaje)
    finally:
        try:
            original.close()
            auxiliar.close()
            historial.close()
        except NameError:
            pass
    if exito:
        exito = copiar_archivo(ARCHIVO_AUXILIAR, ARCHIVO_INVENTARIO)
    return exito

# ----------------------------------------------------------------------
# Funciones principales
# ----------------------------------------------------------------------
def consultar_codigo(codigo):
    """Abre el inventario y devuelve (cantidad de lotes del codigo, clave del ultimo, datos del ultimo)"""
    resultado = (0, None, None)
    try:
        arch = open(ARCHIVO_INVENTARIO, "rt")
        resultado = buscar_codigo(arch, codigo)
    except FileNotFoundError as mensaje:
        print("No se puede abrir el archivo:", mensaje)
    except OSError as mensaje:
        print("No se puede leer el archivo:", mensaje)
    finally:
        try:
            arch.close()
        except NameError:
            pass
    return resultado

def consultar_lote(clave):
    """Abre el inventario y devuelve los datos del lote con esa clave, o None si no existe"""
    datos = None
    try:
        arch = open(ARCHIVO_INVENTARIO, "rt")
        datos = buscar_lote(arch, clave)
    except FileNotFoundError as mensaje:
        print("No se puede abrir el archivo:", mensaje)
    except OSError as mensaje:
        print("No se puede leer el archivo:", mensaje)
    finally:
        try:
            arch.close()
        except NameError:
            pass
    return datos

def elegir_lote(codigo):
    """Devuelve el lote a usar como tupla (clave, datos). Si el codigo tiene un solo lote lo toma directo;
    si tiene varios, los muestra y pide el vencimiento. Devuelve None si el codigo no existe
    o si el usuario cancela con Enter."""
    elegido = None
    try:
        arch = open(ARCHIVO_INVENTARIO, "rt")
        cantidad, clave, datos = buscar_codigo(arch, codigo)
        if cantidad == 0:
            print(f"\n>> No se encontro ningun producto con el codigo {codigo}.")
        elif cantidad == 1:
            elegido = (clave, datos)
        else:
            print("\nEse producto tiene varios lotes:")
            listar_lotes(arch, "codigo", codigo, "")
            vence = input("Ingrese el vencimiento del lote (AAAA/MM/DD) o Enter para cancelar: ").strip()
            datos = None
            while vence != "" and datos == None:
                datos = buscar_lote(arch, (codigo, vence))
                if datos == None:
                    vence = input("Ese lote no existe. Ingrese un vencimiento de la lista (Enter para cancelar): ").strip()
            if vence == "":
                print("\n>> Operacion cancelada.")
            else:
                elegido = ((codigo, vence), datos)
    except FileNotFoundError as mensaje:
        print("No se puede abrir el archivo:", mensaje)
    except OSError as mensaje:
        print("No se puede leer el archivo:", mensaje)
    finally:
        try:
            arch.close()
        except NameError:
            pass
    return elegido

def imprimir_inventario():
    """Muestra el inventario agrupado por categoria, con el total de unidades de cada una"""
    imprimir_titulo("Inventario por categoria")
    try:
        arch = open(ARCHIVO_INVENTARIO, "rt")
        presentes = obtener_categorias(arch)
        if len(presentes) == 0:
            print("No hay productos registrados en el inventario.")
        for categoria in CATEGORIAS:
            if categoria in presentes:
                print()
                print(f">>> {categoria.upper()}")
                unidades = listar_lotes(arch, "categoria", categoria, "")
                print(f"Unidades en {categoria}: {unidades}")
    except FileNotFoundError as mensaje:
        print("No se puede abrir el archivo:", mensaje)
    except OSError as mensaje:
        print("No se puede leer el archivo:", mensaje)
    finally:
        try:
            arch.close()
        except NameError:
            pass

def agregar_producto(codigo, categoria, nombre, vence, costo, cantidad):
    """Agrega un lote nuevo al final del inventario y registra el alta en el historial"""
    clave = (codigo, vence)
    datos = {"categoria": categoria, "nombre": nombre, "costo": costo, "cantidad": cantidad}
    try:
        inventario = open(ARCHIVO_INVENTARIO, "at")
        historial = open(ARCHIVO_HISTORIAL, "at")
        inventario.write(lote_a_linea(clave, datos))
        registrar_movimiento(historial, clave, datos, "ALTA", cantidad)
        print(f"\n>> Se agrego el producto '{nombre}' (vence {vence}) con exito.")
    except OSError as mensaje:
        print("No se puede grabar el archivo:", mensaje)
    finally:
        try:
            inventario.close()
            historial.close()
        except NameError:
            pass

def reponer_stock(clave, datos, cantidad):
    """Suma unidades a un lote que ya existe y registra el alta en el historial"""
    nueva_cantidad = datos["cantidad"] + cantidad
    if actualizar_inventario(clave[0], clave[1], "cantidad", nueva_cantidad, "ALTA"):
        print(f"\n>> Se sumaron {cantidad} unidad(es) a '{datos['nombre']}'. Ahora hay {nueva_cantidad}.")

def dar_de_baja(clave, producto, cantidad_baja):
    """Da de baja una cantidad de un lote. Si baja todo el stock, el lote se elimina del inventario"""
    if cantidad_baja > producto["cantidad"]:
        print(f"\n>> No es posible dar de baja {cantidad_baja}: solo hay {producto['cantidad']} unidad(es).")
        return
    quedan = producto["cantidad"] - cantidad_baja
    if actualizar_inventario(clave[0], clave[1], "cantidad", quedan, "BAJA"):
        if quedan == 0:
            print(f"\n>> Se elimino el lote de '{producto['nombre']}' del inventario (stock en 0).")
        else:
            print(f"\n>> Se dieron de baja {cantidad_baja} unidad(es) de '{producto['nombre']}'. Quedan {quedan}.")

def modificar_producto(clave, opcion, nuevo_valor):
    """Modifica la categoria (1), el costo (2) o la cantidad (3) y registra la modificacion en el historial.
    El nuevo valor llega ya validado. La categoria se cambia en todos los lotes del mismo codigo."""
    if opcion == 1:
        exito = actualizar_inventario(clave[0], "", "categoria", nuevo_valor, "MODIF")
    elif opcion == 2:
        exito = actualizar_inventario(clave[0], clave[1], "costo", nuevo_valor, "MODIF")
    else:
        exito = actualizar_inventario(clave[0], clave[1], "cantidad", nuevo_valor, "MODIF")
    if exito:
        print("\n>> Se modifico el producto con exito.")

def mostrar_lotes(titulo, tipo_filtro, valor, mensaje_vacio):
    """Abre el inventario, imprime un titulo y los lotes que cumplen el filtro. Devuelve las unidades listadas"""
    imprimir_titulo(titulo)
    unidades = 0
    try:
        arch = open(ARCHIVO_INVENTARIO, "rt")
        unidades = listar_lotes(arch, tipo_filtro, valor, mensaje_vacio)
    except FileNotFoundError as mensaje:
        print("No se puede abrir el archivo:", mensaje)
    except OSError as mensaje:
        print("No se puede leer el archivo:", mensaje)
    finally:
        try:
            arch.close()
        except NameError:
            pass
    return unidades

def buscar_producto(termino):
    """Busca lotes por codigo, nombre, categoria o vencimiento (coincidencia parcial)"""
    termino = termino.strip().lower()
    mostrar_lotes("Resultado de la busqueda", "texto", termino, "No se encontraron productos con ese criterio.")

def productos_proximos_a_vencer(dias):
    """Imprime los lotes ya vencidos y los que vencen dentro de los proximos 'dias' dias"""
    hoy = fecha_hoy()
    hoy_tupla = fecha_a_tupla(hoy)
    limite = fecha_proxima_a_vencer(hoy, dias)
    try:
        arch = open(ARCHIVO_INVENTARIO, "rt")
        imprimir_titulo("Productos ya vencidos")
        listar_lotes(arch, "vencidos", hoy_tupla, "No hay productos vencidos.")
        imprimir_titulo(f"Productos que vencen en los proximos {dias} dias")
        listar_lotes(arch, "proximos", (hoy_tupla, limite), "No hay productos proximos a vencer en ese periodo.")
    except FileNotFoundError as mensaje:
        print("No se puede abrir el archivo:", mensaje)
    except OSError as mensaje:
        print("No se puede leer el archivo:", mensaje)
    finally:
        try:
            arch.close()
        except NameError:
            pass

def imprimir_por_categoria(categoria):
    """Imprime los lotes de una categoria y el total de unidades disponibles"""
    total_categoria = mostrar_lotes(f"Stock de la categoria {categoria}", "categoria", categoria,
                                    f"No hay productos registrados en la categoria {categoria}.")
    if total_categoria > 0:
        print(f"Total de unidades en {categoria}: {total_categoria}")

def imprimir_historial(categoria, fecha):
    """Muestra los movimientos del historial (altas, bajas y modificaciones), registro por registro.
    Se puede filtrar por categoria y/o por fecha (vacio = todos)"""
    imprimir_titulo("Historial de movimientos")
    if categoria != "":
        print(f"Categoria: {categoria}")
    if fecha != "":
        print(f"Fecha: {fecha}")
    encontrados = 0
    try:
        arch = open(ARCHIVO_HISTORIAL, "rt")
        for linea_archivo in arch:
            mov = linea_a_movimiento(linea_archivo)
            if mov != None and (categoria == "" or mov[1] == categoria) and (fecha == "" or mov[3] == fecha):
                if encontrados == 0:
                    print("FECHA".ljust(11) + "TIPO".ljust(7) + "CODIGO".ljust(11) + "CATEGORIA".ljust(12) + "NOMBRE".ljust(25)
                          + "CANT.".rjust(6) + "UNITARIO".rjust(9) + "TOTAL".rjust(9))
                    print(linea("-"))
                cantidad = str(mov[5])
                if mov[5] > 0:
                    cantidad = "+" + cantidad
                print(mov[3].ljust(11) + mov[4].ljust(7) + mov[0].ljust(11) + recortar(mov[1].capitalize(), 11).ljust(12)
                      + recortar(mov[2], 23).ljust(25) + cantidad.rjust(6) + f"${mov[6]}".rjust(9) + f"${mov[7]}".rjust(9))
                if mov[8] != "":
                    print("    -> " + mov[8])
                encontrados = encontrados + 1
    except FileNotFoundError as mensaje:
        print("No se puede abrir el archivo:", mensaje)
    except OSError as mensaje:
        print("No se puede leer el archivo:", mensaje)
    finally:
        try:
            arch.close()
        except NameError:
            pass
    if encontrados == 0:
        print("No hay movimientos registrados con esos criterios.")
    else:
        print(linea("-"))
        print(f"Total de movimientos: {encontrados}")

def valorizar_inventario():
    """Muestra la cantidad de productos y lotes y el valor total del inventario (calculado en forma recursiva)"""
    imprimir_titulo("Valorizacion del inventario")
    try:
        arch = open(ARCHIVO_INVENTARIO, "rt")
        codigos = set()
        lotes = 0
        for linea_archivo in arch:
            lote = linea_a_lote(linea_archivo)
            if lote != None:
                codigos.add(lote[0][0])
                lotes = lotes + 1
        arch.seek(0)
        total = valor_desde_archivo(arch)
        if lotes == 0:
            print("No hay productos registrados en el inventario.")
        else:
            print("Productos distintos:".ljust(30) + str(len(codigos)).rjust(15))
            print("Lotes en el inventario:".ljust(30) + str(lotes).rjust(15))
            print("Valor total del inventario:".ljust(30) + f"${total}".rjust(15))
    except FileNotFoundError as mensaje:
        print("No se puede abrir el archivo:", mensaje)
    except OSError as mensaje:
        print("No se puede leer el archivo:", mensaje)
    finally:
        try:
            arch.close()
        except NameError:
            pass

def estadisticas_productos_disponibles():
    """Muestra las categorias ordenadas de mayor a menor cantidad de unidades, con un grafico de barras.
    Usa una matriz con una fila por categoria: [categoria, unidades, lotes, valor]"""
    imprimir_titulo("Categorias con mayor cantidad de productos")
    matriz = []
    for categoria in CATEGORIAS:
        matriz.append([categoria, 0, 0, 0])
    try:
        arch = open(ARCHIVO_INVENTARIO, "rt")
        for linea_archivo in arch:
            lote = linea_a_lote(linea_archivo)
            if lote != None and lote[1]["categoria"] in CATEGORIAS:
                fila = matriz[CATEGORIAS.index(lote[1]["categoria"])]
                fila[1] = fila[1] + lote[1]["cantidad"]
                fila[2] = fila[2] + 1
                fila[3] = fila[3] + lote[1]["costo"] * lote[1]["cantidad"]
    except FileNotFoundError as mensaje:
        print("No se puede abrir el archivo:", mensaje)
        return
    except OSError as mensaje:
        print("No se puede leer el archivo:", mensaje)
        return
    finally:
        try:
            arch.close()
        except NameError:
            pass

    ordenadas = []
    for fila in matriz:
        if fila[1] > 0:
            ordenadas.append(fila)
    if ordenadas == []:
        print("No hay productos registrados en el inventario.")
        return
    ordenadas.sort(key=lambda f: f[1], reverse=True)
    maximo = ordenadas[0][1]

    print("#".ljust(4) + "CATEGORIA".ljust(12) + "LOTES".rjust(6) + "UNIDADES".rjust(10) + "VALOR".rjust(12) + "  GRAFICO")
    print(linea("-"))
    for i, fila in enumerate(ordenadas):
        barra = "#" * (fila[1] * 40 // maximo)
        print(str(i + 1).ljust(4) + fila[0].capitalize().ljust(12) + str(fila[2]).rjust(6) + str(fila[1]).rjust(10)
              + f"${fila[3]}".rjust(12) + "  " + barra)
    print(linea("-"))

# ----------------------------------------------------------------------
# Menu
# ----------------------------------------------------------------------
OPCIONES = ("Mostrar inventario", "Agregar producto", "Dar de baja producto", "Modificar producto",
            "Buscar producto", "Ver productos por vencer", "Imprimir stock por categoria",
            "Imprimir historial", "Valorizar inventario", "Estadisticas de productos disponibles", "Salir")

def imprimir_menu():
    """Imprime el menu con sus opciones"""
    imprimir_titulo("Menu de inicio")
    for i, opcion_menu in enumerate(OPCIONES):
        print("   " + str(i + 1).rjust(2) + ".  " + opcion_menu)
    print(linea("-"))

# ----------------------------------------------------------------------
# Pruebas: se verifican las funciones de calculo con assert al iniciar
# ----------------------------------------------------------------------
def ejecutar_pruebas():
    """Verifica con assert que las funciones de fechas, validacion y conversion den el resultado esperado.
    Si alguna falla, se informa cual (AssertionError) y el programa sigue."""
    try:
        assert dias_en_mes(2, 2024) == 29, "dias_en_mes: febrero de anio bisiesto"
        assert dias_en_mes(2, 2100) == 28, "dias_en_mes: 2100 no es bisiesto"
        assert dias_en_mes(4, 2026) == 30, "dias_en_mes: abril"
        assert fecha_valida("2026/02/29") == False, "fecha_valida: 29 de febrero de 2026 no existe"
        assert fecha_valida("2028/02/29") == True, "fecha_valida: 29 de febrero de 2028 existe"
        assert fecha_valida("2026-10-23") == False, "fecha_valida: formato con guiones"
        assert sumar_dias(2026, 10, 23, 30) == (2026, 11, 22), "sumar_dias: cambio de mes"
        assert sumar_dias(2026, 12, 25, 10) == (2027, 1, 4), "sumar_dias: cambio de anio"
        assert sumar_dias(2028, 2, 28, 1) == (2028, 2, 29), "sumar_dias: anio bisiesto"
        assert fecha_a_tupla("2026/09/20") < fecha_a_tupla("2026/10/08"), "fecha_a_tupla: comparacion de fechas"
        clave = ("123456789", "2027/12/30")
        datos = {"categoria": "lacteos", "nombre": "Leche", "costo": 3000, "cantidad": 200}
        assert linea_a_lote(lote_a_linea(clave, datos)) == (clave, datos), "lote_a_linea / linea_a_lote"
        assert cumple_filtro(clave, datos, "texto", "lech") == True, "cumple_filtro: busqueda parcial"
        assert recortar("Leche entera", 8) == "Leche...", "recortar"
    except AssertionError as mensaje:
        print(">> Fallo una prueba interna:", mensaje)

# ----------------------------------------------------------------------
# Programa principal
# ----------------------------------------------------------------------
ejecutar_pruebas()
inicializar_archivos()

imprimir_titulo("Sistema de gestion de inventario")
try:
    imprimir_menu()
    opcion = validar_numero(input("Elija una opción: "))
    while opcion != 11:
        if opcion == 1:
            imprimir_inventario()

        elif opcion == 2:
            codigo = validar_codigo(input("Ingrese el codigo del producto (9 digitos): "))
            cantidad_lotes, clave_base, base = consultar_codigo(codigo)
            if cantidad_lotes > 0:
                print(f"\n>> El producto ya existe: '{base['nombre']}' ({cantidad_lotes} lote(s)).")
                categoria = base["categoria"]
                nombre = base["nombre"]
            else:
                print("\nCategorias disponibles:")
                categoria = elegir_categoria()
                nombre = validar_nombre(input("Ingrese el nombre del producto: "))
            vence = validar_fecha_actual(input("Ingrese la fecha de vencimiento del producto (AAAA/MM/DD): "))
            existente = consultar_lote((codigo, vence))
            if existente != None:
                print("\n>> Ya existe un lote con ese vencimiento. Se sumaran unidades a su stock.")
                cantidad = validar_numero(input("Ingrese la cantidad de unidades que ingresan: "))
                reponer_stock((codigo, vence), existente, cantidad)
            else:
                costo = validar_numero(input("Ingrese el costo del producto: "))
                cantidad = validar_numero(input("Ingrese la cantidad de articulos disponibles: "))
                agregar_producto(codigo, categoria, nombre, vence, costo, cantidad)

        elif opcion == 3:
            codigo = validar_codigo(input("Ingrese el codigo del producto a dar de baja: "))
            elegido = elegir_lote(codigo)
            if elegido != None:
                cantidad = validar_numero(input("Ingrese la cantidad de unidades que quiera dar de baja: "))
                dar_de_baja(elegido[0], elegido[1], cantidad)

        elif opcion == 4:
            codigo = validar_codigo(input("Ingrese el codigo del producto a modificar: "))
            elegido = elegir_lote(codigo)
            if elegido != None:
                clave = elegido[0]
                print("1. Categoria \n2. Costo \n3. Cantidad \n4. Salir")
                opcion_mod = validar_numero(input("¿Qué desea modificar?: "))
                while opcion_mod < 1 or opcion_mod > 4:
                    opcion_mod = validar_numero(input("Opción inválida. Ingrese una opción válida: "))
                if opcion_mod == 1:
                    nuevo_valor = elegir_categoria()
                    modificar_producto(clave, opcion_mod, nuevo_valor)
                elif opcion_mod != 4:
                    nuevo_valor = validar_numero(input("Ingrese el nuevo valor: "))
                    modificar_producto(clave, opcion_mod, nuevo_valor)

        elif opcion == 5:
            termino = validar_no_es_vacio(input("Ingrese el codigo, nombre, categoria o vencimiento a buscar: "))
            buscar_producto(termino)

        elif opcion == 6:
            dias = validar_numero(input("Ingrese la cantidad de dias a futuro para revisar vencimientos: "))
            while dias > MAX_DIAS:
                dias = validar_numero(input(f"El maximo es {MAX_DIAS} dias. Ingrese nuevamente: "))
            productos_proximos_a_vencer(dias)

        elif opcion == 7:
            print("\nCategorias disponibles:")
            categoria = elegir_categoria()
            imprimir_por_categoria(categoria)

        elif opcion == 8:
            print("\nFiltrar por categoria:")
            categoria = elegir_categoria(True)
            fecha = input("Filtrar por fecha AAAA/MM/DD (Enter para ver todas): ").strip()
            if fecha != "" and not fecha_valida(fecha):
                print("\n>> La fecha no es valida (formato AAAA/MM/DD).")
            else:
                imprimir_historial(categoria, fecha)

        elif opcion == 9:
            valorizar_inventario()

        elif opcion == 10:
            estadisticas_productos_disponibles()

        else:
            print("Opción inválida. Intente nuevamente.")

        imprimir_menu()
        opcion = validar_numero(input("Elija una opción: "))
except KeyboardInterrupt:
    print("\n\n>> Programa interrumpido por el usuario.")

print("Programa finalizado")
