import re
from datetime import datetime   # solo se usa para averiguar la fecha actual

# ======================================================================
# Sistema de gestion de inventarios - TPO Grupo 2
#
# Estructuras de datos usadas:
#   - DICCIONARIO: el inventario. La clave es una TUPLA (codigo, vencimiento),
#     asi un mismo producto puede tener varios lotes con distinta fecha de
#     vencimiento. El valor es otro diccionario con los datos del lote.
#   - MATRIZ (lista de listas): el historial de movimientos.
#   - TUPLAS: las claves del inventario, las fechas (anio, mes, dia), que se
#     comparan directamente, las categorias definidas y las opciones del menu.
#   - CONJUNTO: las categorias con productos y los codigos distintos.
# ======================================================================

# Categorias definidas: el usuario elige por numero, no las escribe
CATEGORIAS = ("lacteos", "limpieza", "conservas", "almacen", "bebidas", "higiene")

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

def imprimir_productos(productos):
    """Imprime un diccionario de lotes como tabla alineada (ordenada por nombre y vencimiento)"""
    print("CODIGO".ljust(11) + "CATEGORIA".ljust(12) + "NOMBRE".ljust(38) + "VENCE".ljust(12) + "COSTO".rjust(9) + "CANT.".rjust(8))
    print(linea("-"))
    for clave in sorted(productos, key=lambda c: (productos[c]["nombre"], c[1])):
        datos = productos[clave]
        print(clave[0].ljust(11)
              + recortar(datos["categoria"].capitalize(), 11).ljust(12)
              + recortar(datos["nombre"], 36).ljust(38)
              + clave[1].ljust(12)
              + f"${datos['costo']}".rjust(9)
              + str(datos["cantidad"]).rjust(8))
    print(linea("-"))
    print(f"Total de lotes listados: {len(productos)}")

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

def fecha_proxima_a_vencer(hoy, dias):
    """Calcula la fecha limite (anio, mes, dia) sumando 'dias' a la fecha de hoy"""
    anio, mes, dia = fecha_a_tupla(hoy)
    dia += dias
    while dia > dias_en_mes(mes, anio):
        dia -= dias_en_mes(mes, anio)
        mes += 1
        if mes > 12:
            mes = 1
            anio += 1
    return (anio, mes, dia)

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
    """Valida que el numero ingresado sea entero y positivo, y lo devuelve como int"""
    numero = validar_no_es_vacio(numero)
    while not numero.isdigit() or int(numero) <= 0:
        numero = input("Ingrese un numero positivo y valido: ").strip()
    return int(numero)

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
    texto = input("Ingrese el numero de la categoria: ").strip()
    while not texto.isdigit() or int(texto) < minimo or int(texto) > len(CATEGORIAS):
        texto = input("Numero invalido. Ingrese un numero de la lista: ").strip()
    if int(texto) == 0:
        return ""
    return CATEGORIAS[int(texto) - 1]

# ----------------------------------------------------------------------
# Datos iniciales
# ----------------------------------------------------------------------
def crear_inventario():
    """Crea y devuelve el inventario inicial (diccionario: (codigo, vence) -> datos del lote)"""
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
    """Crea y devuelve el historial de movimientos (matriz: una fila por movimiento).
    Orden de cada fila:
    [codigo, categoria, nombre, fecha, tipo, cantidad, costo unitario, costo total, detalle]
    tipo: ALTA, BAJA o MODIF. La cantidad es positiva en las altas y negativa en las bajas."""
    return [["123456789", "lacteos",   "Leche entera La Serenisima por 1l",   "2026/07/30", "ALTA", 200, 3000, 600000, ""],
            ["123456789", "lacteos",   "Leche entera La Serenisima por 1l",   "2026/08/10", "ALTA", 60, 3000, 180000, ""],
            ["987654321", "lacteos",   "Queso muzzarela La Blanca por 500gm", "2026/03/20", "BAJA", -20, 7000, 140000, ""],
            ["579246813", "limpieza",  "Desinfectante Lysoform por 360ml",    "2026/08/12", "ALTA", 50, 4200, 210000, ""],
            ["813579246", "conservas", "Pure de tomate Arcor por 520gm",      "2026/08/05", "BAJA", -20, 1900, 38000, ""],
            ["369258147", "lacteos",   "Crema de leche Tregar por 200ml",     "2026/07/18", "ALTA", 50, 2200, 110000, ""],
            ["246813579", "limpieza",  "Detergente Magistral por 750ml",      "2026/08/20", "BAJA", -20, 2800, 56000, ""],
            ["753159456", "almacen",   "Azucar Ledesma por 1kg",              "2026/06/25", "ALTA", 100, 1700, 170000, ""],
            ["135792468", "limpieza",  "Lavandina Ayudin por 1l",             "2026/08/15", "ALTA", 50, 1800, 90000, ""]]

def obtener_categorias(inventario):
    """Devuelve un conjunto con las categorias que tienen productos (sin repetidos)"""
    categorias = set()
    for datos in inventario.values():
        categorias.add(datos["categoria"])
    return categorias

def obtener_codigos(inventario):
    """Devuelve un conjunto con los codigos distintos del inventario"""
    codigos = set()
    for clave in inventario:
        codigos.add(clave[0])
    return codigos

# ----------------------------------------------------------------------
# Funciones auxiliares sobre el inventario y el historial
# ----------------------------------------------------------------------
def lotes_de_codigo(inventario, codigo):
    """Devuelve un diccionario con todos los lotes (distintos vencimientos) de un codigo"""
    lotes = {}
    for clave in inventario:
        if clave[0] == codigo:
            lotes[clave] = inventario[clave]
    return lotes

def lotes_de_categoria(inventario, categoria):
    """Devuelve un diccionario con los lotes de una categoria"""
    lotes = {}
    for clave in inventario:
        if inventario[clave]["categoria"] == categoria:
            lotes[clave] = inventario[clave]
    return lotes

def elegir_lote(inventario, codigo):
    """Devuelve la clave (codigo, vence) del lote a usar. Si el codigo tiene un solo lote lo toma directo;
    si tiene varios, los muestra y pide el vencimiento. Devuelve None si el codigo no existe."""
    lotes = lotes_de_codigo(inventario, codigo)
    if lotes == {}:
        print(f"\n>> No se encontro ningun producto con el codigo {codigo}.")
        return None
    if len(lotes) == 1:
        for clave in lotes:
            return clave
    print("\nEse producto tiene varios lotes:")
    imprimir_productos(lotes)
    vence = input("Ingrese el vencimiento del lote (AAAA/MM/DD): ").strip()
    while (codigo, vence) not in lotes:
        vence = input("Ese lote no existe. Ingrese un vencimiento de la lista: ").strip()
    return (codigo, vence)

def registrar_movimiento(historial, clave, producto, tipo, cantidad, detalle=""):
    """Agrega una fila al historial con la fecha de hoy. Se usa en altas, bajas y modificaciones"""
    historial.append([clave[0], producto["categoria"], producto["nombre"], fecha_hoy(), tipo,
                      cantidad, producto["costo"], producto["costo"] * abs(cantidad), detalle])

# ----------------------------------------------------------------------
# Funciones principales
# ----------------------------------------------------------------------
def imprimir_inventario(inventario):
    """Muestra el inventario agrupado por categoria, con el total de unidades de cada una"""
    imprimir_titulo("Inventario por categoria")
    if inventario == {}:
        print("No hay productos registrados en el inventario.")
        return
    presentes = obtener_categorias(inventario)
    for categoria in CATEGORIAS:
        if categoria in presentes:
            lotes = lotes_de_categoria(inventario, categoria)
            unidades = 0
            for datos in lotes.values():
                unidades = unidades + datos["cantidad"]
            print()
            print(f">>> {categoria.upper()} ({unidades} unidades)")
            imprimir_productos(lotes)

def agregar_producto(inventario, historial, codigo, categoria, nombre, vence, costo, cantidad):
    """Agrega un lote nuevo al inventario y registra el alta en el historial"""
    clave = (codigo, vence)
    inventario[clave] = {"categoria": categoria, "nombre": nombre, "costo": costo, "cantidad": cantidad}
    registrar_movimiento(historial, clave, inventario[clave], "ALTA", cantidad)
    print(f"\n>> Se agrego el producto '{nombre}' (vence {vence}) con exito.")

def reponer_stock(inventario, historial, clave, cantidad):
    """Suma unidades a un lote que ya existe y registra el alta en el historial"""
    producto = inventario[clave]
    producto["cantidad"] = producto["cantidad"] + cantidad
    registrar_movimiento(historial, clave, producto, "ALTA", cantidad)
    print(f"\n>> Se sumaron {cantidad} unidad(es) a '{producto['nombre']}'. Ahora hay {producto['cantidad']}.")

def dar_de_baja(historial, inventario, clave, cantidad_baja):
    """Da de baja una cantidad de un lote. Si baja todo el stock, el lote se elimina del inventario"""
    producto = inventario[clave]
    if cantidad_baja > producto["cantidad"]:
        print(f"\n>> No es posible dar de baja {cantidad_baja}: solo hay {producto['cantidad']} unidad(es).")
    elif cantidad_baja == producto["cantidad"]:
        registrar_movimiento(historial, clave, producto, "BAJA", -cantidad_baja)
        inventario.pop(clave)
        print(f"\n>> Se elimino el lote de '{producto['nombre']}' del inventario (stock en 0).")
    else:
        producto["cantidad"] = producto["cantidad"] - cantidad_baja
        registrar_movimiento(historial, clave, producto, "BAJA", -cantidad_baja)
        print(f"\n>> Se dieron de baja {cantidad_baja} unidad(es) de '{producto['nombre']}'. Quedan {producto['cantidad']}.")

def modificar_producto(inventario, historial, clave, opcion, nuevo_valor):
    """Modifica la categoria (1), el costo (2) o la cantidad (3) y registra la modificacion en el historial.
    El nuevo valor llega ya validado. La categoria se cambia en todos los lotes del mismo codigo."""
    producto = inventario[clave]
    if opcion == 1:
        for clave_lote, lote in lotes_de_codigo(inventario, clave[0]).items():
            detalle = f"Categoria: {lote['categoria']} -> {nuevo_valor}"
            lote["categoria"] = nuevo_valor
            registrar_movimiento(historial, clave_lote, lote, "MODIF", 0, detalle)
    elif opcion == 2:
        detalle = f"Costo: ${producto['costo']} -> ${nuevo_valor}"
        producto["costo"] = nuevo_valor
        registrar_movimiento(historial, clave, producto, "MODIF", 0, detalle)
    elif opcion == 3:
        diferencia = nuevo_valor - producto["cantidad"]
        detalle = f"Cantidad: {producto['cantidad']} -> {nuevo_valor}"
        producto["cantidad"] = nuevo_valor
        registrar_movimiento(historial, clave, producto, "MODIF", diferencia, detalle)
    print(f"\n>> Se modifico el producto '{producto['nombre']}' con exito.")

def buscar_producto(inventario, termino):
    """Busca lotes por codigo, nombre, categoria o vencimiento (coincidencia parcial)"""
    termino = termino.strip().lower()
    encontrados = {}
    for clave in inventario:
        datos = inventario[clave]
        if termino in clave[0] or termino in clave[1] or termino in datos["nombre"].lower() or termino in datos["categoria"]:
            encontrados[clave] = datos

    imprimir_titulo("Resultado de la busqueda")
    if encontrados == {}:
        print("No se encontraron productos con ese criterio.")
    else:
        imprimir_productos(encontrados)

def productos_proximos_a_vencer(inventario, dias):
    """Imprime los lotes ya vencidos y los que vencen dentro de los proximos 'dias' dias"""
    hoy = fecha_hoy()
    hoy_tupla = fecha_a_tupla(hoy)
    limite = fecha_proxima_a_vencer(hoy, dias)
    vencidos = {}
    proximos = {}
    for clave in inventario:
        vence = fecha_a_tupla(clave[1])
        if vence < hoy_tupla:
            vencidos[clave] = inventario[clave]
        elif vence <= limite:
            proximos[clave] = inventario[clave]

    imprimir_titulo("Productos ya vencidos")
    if vencidos == {}:
        print("No hay productos vencidos.")
    else:
        imprimir_productos(vencidos)

    imprimir_titulo(f"Productos que vencen en los proximos {dias} dias")
    if proximos == {}:
        print("No hay productos proximos a vencer en ese periodo.")
    else:
        imprimir_productos(proximos)

def imprimir_por_categoria(inventario, categoria):
    """Imprime los lotes de una categoria y el total de unidades disponibles"""
    encontrados = lotes_de_categoria(inventario, categoria)
    imprimir_titulo(f"Stock de la categoria {categoria}")
    if encontrados == {}:
        print(f"No hay productos registrados en la categoria {categoria}.")
        return
    total_categoria = 0
    for datos in encontrados.values():
        total_categoria = total_categoria + datos["cantidad"]
    imprimir_productos(encontrados)
    print(f"Total de unidades en {categoria}: {total_categoria}")

def imprimir_historial(historial, categoria, fecha):
    """Muestra los movimientos del historial (altas, bajas y modificaciones).
    Se puede filtrar por categoria y/o por fecha (vacio = todos)"""
    encontrados = []
    for movimiento in historial:
        if (categoria == "" or movimiento[1] == categoria) and (fecha == "" or movimiento[3] == fecha):
            encontrados.append(movimiento)

    imprimir_titulo("Historial de movimientos")
    if categoria != "":
        print(f"Categoria: {categoria}")
    if fecha != "":
        print(f"Fecha: {fecha}")
    if encontrados == []:
        print("No hay movimientos registrados con esos criterios.")
        return

    print("FECHA".ljust(11) + "TIPO".ljust(7) + "CODIGO".ljust(11) + "CATEGORIA".ljust(12) + "NOMBRE".ljust(25)
          + "CANT.".rjust(6) + "UNITARIO".rjust(9) + "TOTAL".rjust(9))
    print(linea("-"))
    for mov in encontrados:
        cantidad = str(mov[5])
        if mov[5] > 0:
            cantidad = "+" + cantidad
        print(mov[3].ljust(11) + mov[4].ljust(7) + mov[0].ljust(11) + recortar(mov[1].capitalize(), 11).ljust(12)
              + recortar(mov[2], 23).ljust(25) + cantidad.rjust(6) + f"${mov[6]}".rjust(9) + f"${mov[7]}".rjust(9))
        if mov[8] != "":
            print("    -> " + mov[8])
    print(linea("-"))
    print(f"Total de movimientos: {len(encontrados)}")

def valorizar_inventario(inventario):
    """Calcula el valor total del inventario (costo por cantidad de cada lote)"""
    imprimir_titulo("Valorizacion del inventario")
    if inventario == {}:
        print("No hay productos registrados en el inventario.")
        return
    total = 0
    for datos in inventario.values():
        total = total + datos["costo"] * datos["cantidad"]
    print("Productos distintos:".ljust(30) + str(len(obtener_codigos(inventario))).rjust(15))
    print("Lotes en el inventario:".ljust(30) + str(len(inventario)).rjust(15))
    print("Valor total del inventario:".ljust(30) + f"${total}".rjust(15))

def estadisticas_productos_disponibles(inventario):
    """Muestra las categorias ordenadas de mayor a menor cantidad de unidades, con un grafico de barras"""
    imprimir_titulo("Categorias con mayor cantidad de productos")
    if inventario == {}:
        print("No hay productos registrados en el inventario.")
        return

    totales = {}
    for datos in inventario.values():
        categoria = datos["categoria"]
        totales[categoria] = totales.get(categoria, 0) + datos["cantidad"]

    ordenadas = sorted(totales.items(), key=lambda item: item[1], reverse=True)
    maximo = ordenadas[0][1]

    print("#".ljust(4) + "CATEGORIA".ljust(14) + "UNIDADES".rjust(9) + "  GRAFICO")
    print(linea("-"))
    for i, (categoria, unidades) in enumerate(ordenadas):
        barra = "#" * (unidades * 40 // maximo)
        print(str(i + 1).ljust(4) + categoria.capitalize().ljust(14) + str(unidades).rjust(9) + "  " + barra)
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
# Programa principal
# ----------------------------------------------------------------------
inventario = crear_inventario()
historial = crear_historial()

imprimir_titulo("Sistema de gestion de inventario")
imprimir_menu()
opcion = validar_numero(input("Elija una opción: "))
while opcion != 11:
    if opcion == 1:
        imprimir_inventario(inventario)

    elif opcion == 2:
        codigo = validar_codigo(input("Ingrese el codigo del producto (9 digitos): "))
        lotes = lotes_de_codigo(inventario, codigo)
        if lotes != {}:
            for lote in lotes.values():
                base = lote
            print(f"\n>> El producto ya existe: '{base['nombre']}' ({len(lotes)} lote(s)).")
            categoria = base["categoria"]
            nombre = base["nombre"]
        else:
            print("\nCategorias disponibles:")
            categoria = elegir_categoria()
            nombre = validar_nombre(input("Ingrese el nombre del producto: "))
        vence = validar_fecha_actual(input("Ingrese la fecha de vencimiento del producto (AAAA/MM/DD): "))
        if (codigo, vence) in inventario:
            print("\n>> Ya existe un lote con ese vencimiento. Se sumaran unidades a su stock.")
            cantidad = validar_numero(input("Ingrese la cantidad de unidades que ingresan: "))
            reponer_stock(inventario, historial, (codigo, vence), cantidad)
        else:
            costo = validar_numero(input("Ingrese el costo del producto: "))
            cantidad = validar_numero(input("Ingrese la cantidad de articulos disponibles: "))
            agregar_producto(inventario, historial, codigo, categoria, nombre, vence, costo, cantidad)

    elif opcion == 3:
        codigo = validar_codigo(input("Ingrese el codigo del producto a dar de baja: "))
        clave = elegir_lote(inventario, codigo)
        if clave != None:
            cantidad = validar_numero(input("Ingrese la cantidad de unidades que quiera dar de baja: "))
            dar_de_baja(historial, inventario, clave, cantidad)

    elif opcion == 4:
        codigo = validar_codigo(input("Ingrese el codigo del producto a modificar: "))
        clave = elegir_lote(inventario, codigo)
        if clave != None:
            print("1. Categoria \n2. Costo \n3. Cantidad \n4. Salir")
            opcion_mod = validar_numero(input("¿Qué desea modificar?: "))
            while opcion_mod < 1 or opcion_mod > 4:
                opcion_mod = validar_numero(input("Opción inválida. Ingrese una opción válida: "))
            if opcion_mod == 1:
                nuevo_valor = elegir_categoria()
                modificar_producto(inventario, historial, clave, opcion_mod, nuevo_valor)
            elif opcion_mod != 4:
                nuevo_valor = validar_numero(input("Ingrese el nuevo valor: "))
                modificar_producto(inventario, historial, clave, opcion_mod, nuevo_valor)

    elif opcion == 5:
        termino = validar_no_es_vacio(input("Ingrese el codigo, nombre, categoria o vencimiento a buscar: "))
        buscar_producto(inventario, termino)

    elif opcion == 6:
        dias = validar_numero(input("Ingrese la cantidad de dias a futuro para revisar vencimientos: "))
        productos_proximos_a_vencer(inventario, dias)

    elif opcion == 7:
        print("\nCategorias disponibles:")
        categoria = elegir_categoria()
        imprimir_por_categoria(inventario, categoria)

    elif opcion == 8:
        print("\nFiltrar por categoria:")
        categoria = elegir_categoria(True)
        fecha = input("Filtrar por fecha AAAA/MM/DD (Enter para ver todas): ").strip()
        if fecha != "" and not fecha_valida(fecha):
            print("\n>> La fecha no es valida (formato AAAA/MM/DD).")
        else:
            imprimir_historial(historial, categoria, fecha)

    elif opcion == 9:
        valorizar_inventario(inventario)

    elif opcion == 10:
        estadisticas_productos_disponibles(inventario)

    else:
        print("Opción inválida. Intente nuevamente.")

    imprimir_menu()
    opcion = validar_numero(input("Elija una opción: "))
print("Programa finalizado")
