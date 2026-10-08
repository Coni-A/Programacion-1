import re
from datetime import datetime   # solo se usa para averiguar la fecha actual

# ======================================================================
# Sistema de gestion de inventarios - TPO Grupo 2
#
# Estructuras de datos usadas:
#   - DICCIONARIO: el inventario. La clave es el codigo del producto
#     (unica) y el valor es otro diccionario con los datos del producto.
#   - MATRIZ (lista de listas): el historial de movimientos.
#   - TUPLAS: fechas (anio, mes, dia), que se comparan directamente, y
#     las opciones del menu (que no deben modificarse).
#   - CONJUNTO: las categorias existentes (sin repetidos).
# ======================================================================

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
    """Imprime un diccionario de productos como tabla alineada (ordenada por nombre)"""
    print("CODIGO".ljust(11) + "CATEGORIA".ljust(12) + "NOMBRE".ljust(38) + "VENCE".ljust(12) + "COSTO".rjust(9) + "CANT.".rjust(8))
    print(linea("-"))
    for codigo in sorted(productos, key=lambda c: productos[c]["nombre"]):
        datos = productos[codigo]
        print(codigo.ljust(11)
              + recortar(datos["categoria"].capitalize(), 11).ljust(12)
              + recortar(datos["nombre"], 36).ljust(38)
              + datos["vence"].ljust(12)
              + f"${datos['costo']}".rjust(9)
              + str(datos["cantidad"]).rjust(8))
    print(linea("-"))
    print(f"Total de productos listados: {len(productos)}")

# ----------------------------------------------------------------------
# Funciones de fechas (sin usar datetime para parsear ni comparar)
# ----------------------------------------------------------------------
def es_bisiesto(anio):
    """Devuelve True si el anio es bisiesto"""
    return (anio % 4 == 0 and anio % 100 != 0) or (anio % 400 == 0)

def dias_en_mes(mes, anio):
    """Devuelve la cantidad de dias que tiene un mes de un anio determinado"""
    if mes in (1, 3, 5, 7, 8, 10, 12):
        return 31
    elif mes in (4, 6, 9, 11):
        return 30
    elif es_bisiesto(anio):
        return 29
    return 28

def fecha_a_tupla(fecha):
    """Convierte un texto AAAA/MM/DD en una tupla (anio, mes, dia) de numeros"""
    anio, mes, dia = fecha.split("/")
    return (int(anio), int(mes), int(dia))

def validar_formato_fecha(fecha):
    """Devuelve True si el texto tiene el formato AAAA/MM/DD (usa expresion regular)"""
    return re.search("^[0-9][0-9][0-9][0-9]/[0-9][0-9]/[0-9][0-9]$", fecha) != None

def fecha_existe(anio, mes, dia):
    """Devuelve True si la fecha existe en el calendario (ej: no hay 30 de febrero)"""
    if mes < 1 or mes > 12:
        return False
    return dia >= 1 and dia <= dias_en_mes(mes, anio)

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

def validar_categoria(categoria):
    """Valida que la categoria tenga solo letras (usa expresion regular) y la devuelve en minusculas"""
    categoria = validar_no_es_vacio(categoria)
    while re.search("^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$", categoria) == None:
        categoria = input("La categoria solo puede tener letras. Ingrese nuevamente: ").strip()
    return categoria.lower()

def validar_nombre(nombre):
    """Valida que el nombre tenga al menos una letra o un numero (usa expresion regular)"""
    nombre = validar_no_es_vacio(nombre)
    while re.search("[A-Za-z0-9ÁÉÍÓÚáéíóúÑñ]", nombre) == None:
        nombre = input("El nombre debe tener letras o numeros. Ingrese nuevamente: ").strip()
    return nombre

def validar_fecha_actual(fecha, hoy):
    """Valida que la fecha tenga formato AAAA/MM/DD, que exista y que no sea una fecha pasada"""
    fecha = validar_no_es_vacio(fecha)
    while True:
        if validar_formato_fecha(fecha):
            anio, mes, dia = fecha_a_tupla(fecha)
            if not fecha_existe(anio, mes, dia):
                print("La fecha ingresada no existe en el calendario.")
            elif (anio, mes, dia) < fecha_a_tupla(hoy):
                print("La fecha ingresada ya paso.")
            else:
                return fecha
        else:
            print("El formato no es valido.")
        fecha = input("Ingrese nuevamente (AAAA/MM/DD): ").strip()

# ----------------------------------------------------------------------
# Datos iniciales
# ----------------------------------------------------------------------
def crear_inventario():
    """Crea y devuelve el inventario inicial (diccionario: codigo -> datos del producto)"""
    return {
        "123456789": {"categoria": "lacteos",   "nombre": "Leche entera La Serenisima por 1l",   "vence": "2027/12/30", "costo": 3000, "cantidad": 200},
        "987654321": {"categoria": "lacteos",   "nombre": "Queso muzzarela La Blanca por 500gm", "vence": "2026/09/20", "costo": 7000, "cantidad": 120},
        "579246813": {"categoria": "limpieza",  "nombre": "Desinfectante Lysoform por 360ml",    "vence": "2028/12/05", "costo": 4200, "cantidad": 70},
        "813579246": {"categoria": "conservas", "nombre": "Pure de tomate Arcor por 520gm",      "vence": "2028/11/20", "costo": 1900, "cantidad": 150},
        "369258147": {"categoria": "lacteos",   "nombre": "Crema de leche Tregar por 200ml",     "vence": "2026/10/08", "costo": 2200, "cantidad": 90},
        "246813579": {"categoria": "limpieza",  "nombre": "Detergente Magistral por 750ml",      "vence": "2029/01/20", "costo": 2800, "cantidad": 100},
        "753159456": {"categoria": "almacen",   "nombre": "Azucar Ledesma por 1kg",              "vence": "2028/03/25", "costo": 1700, "cantidad": 210},
        "135792468": {"categoria": "limpieza",  "nombre": "Lavandina Ayudin por 1l",             "vence": "2028/09/15", "costo": 1800, "cantidad": 130}
    }

def crear_historial():
    """Crea y devuelve el historial de movimientos (matriz: una fila por movimiento).
    Orden de cada fila: [codigo, categoria, nombre, fecha, costo unitario, costo total, cantidad]
    Si es una baja, la cantidad figura con signo negativo."""
    return [["123456789", "lacteos",   "Leche entera La Serenisima por 1l",   "2026/07/30", 3000, 600000, 200],
            ["987654321", "lacteos",   "Queso muzzarela La Blanca por 500gm", "2026/03/20", 7000, 140000, -20],
            ["579246813", "limpieza",  "Desinfectante Lysoform por 360ml",    "2026/08/12", 4200, 210000, 50],
            ["813579246", "conservas", "Pure de tomate Arcor por 520gm",      "2026/08/05", 1900, 38000, -20],
            ["369258147", "lacteos",   "Crema de leche Tregar por 200ml",     "2026/07/18", 2200, 110000, 50],
            ["246813579", "limpieza",  "Detergente Magistral por 750ml",      "2026/08/20", 2800, 56000, -20],
            ["753159456", "almacen",   "Azucar Ledesma por 1kg",              "2026/06/25", 1700, 170000, 100],
            ["135792468", "limpieza",  "Lavandina Ayudin por 1l",             "2026/08/15", 1800, 90000, 50]]

def obtener_categorias(inventario):
    """Devuelve un conjunto con las categorias que existen en el inventario (sin repetidos)"""
    categorias = set()
    for datos in inventario.values():
        categorias.add(datos["categoria"])
    return categorias

# ----------------------------------------------------------------------
# Funciones principales
# ----------------------------------------------------------------------
def imprimir_inventario(inventario):
    """Muestra por terminal todos los productos que se encuentren en el inventario"""
    imprimir_titulo("Inventario")
    if inventario == {}:
        print("No hay productos registrados en el inventario.")
    else:
        imprimir_productos(inventario)

def agregar_producto(inventario, historial, codigo, categoria, nombre, vence, costo, cantidad, hoy):
    """Agrega un producto nuevo al inventario y registra el alta en el historial"""
    inventario[codigo] = {"categoria": categoria, "nombre": nombre, "vence": vence, "costo": costo, "cantidad": cantidad}
    historial.append([codigo, categoria, nombre, hoy, costo, costo * cantidad, cantidad])
    print(f"\n>> Se agrego el producto '{nombre}' con exito.")

def reponer_stock(inventario, historial, codigo, cantidad, hoy):
    """Suma unidades a un producto que ya existe y registra el alta en el historial"""
    producto = inventario[codigo]
    producto["cantidad"] = producto["cantidad"] + cantidad
    historial.append([codigo, producto["categoria"], producto["nombre"], hoy, producto["costo"], producto["costo"] * cantidad, cantidad])
    print(f"\n>> Se sumaron {cantidad} unidad(es) a '{producto['nombre']}'. Ahora hay {producto['cantidad']}.")

def dar_de_baja(historial, inventario, codigo, cantidad_baja, hoy):
    """Da de baja una cantidad de un producto. Si baja todo el stock, el producto se elimina del inventario"""
    if codigo not in inventario:
        print(f"\n>> No se encontro ningun producto con el codigo {codigo}.")
        return

    producto = inventario[codigo]
    costo_total = cantidad_baja * producto["costo"]

    if cantidad_baja > producto["cantidad"]:
        print(f"\n>> No es posible dar de baja {cantidad_baja}: solo hay {producto['cantidad']} unidad(es).")
    elif cantidad_baja == producto["cantidad"]:
        historial.append([codigo, producto["categoria"], producto["nombre"], hoy, producto["costo"], costo_total, -cantidad_baja])
        inventario.pop(codigo)
        print(f"\n>> Se elimino el producto '{producto['nombre']}' del inventario (stock en 0).")
    else:
        producto["cantidad"] = producto["cantidad"] - cantidad_baja
        historial.append([codigo, producto["categoria"], producto["nombre"], hoy, producto["costo"], costo_total, -cantidad_baja])
        print(f"\n>> Se dieron de baja {cantidad_baja} unidad(es) de '{producto['nombre']}'. Quedan {producto['cantidad']}.")

def modificar_producto(inventario, codigo, opcion, nuevo_valor):
    """Modifica la categoria, el costo o la cantidad de un producto existente"""
    if codigo not in inventario:
        print(f"\n>> No se encontro ningun producto con el codigo {codigo}.")
        return

    producto = inventario[codigo]
    if opcion == 1:
        producto["categoria"] = validar_categoria(nuevo_valor)
    elif opcion == 2:
        producto["costo"] = validar_numero(nuevo_valor)
    elif opcion == 3:
        producto["cantidad"] = validar_numero(nuevo_valor)
    print(f"\n>> Se modifico el producto '{producto['nombre']}' con exito.")

def buscar_producto(inventario, termino):
    """Busca productos por codigo, nombre o categoria. Si el codigo es exacto, lo encuentra directo por su clave"""
    termino = termino.strip().lower()
    encontrados = {}
    if termino in inventario:
        encontrados[termino] = inventario[termino]
    else:
        for codigo in inventario:
            datos = inventario[codigo]
            if termino in codigo or termino in datos["nombre"].lower() or termino in datos["categoria"]:
                encontrados[codigo] = datos

    imprimir_titulo("Resultado de la busqueda")
    if encontrados == {}:
        print("No se encontraron productos con ese criterio.")
    else:
        imprimir_productos(encontrados)

def productos_proximos_a_vencer(inventario, dias, hoy):
    """Imprime los productos ya vencidos y los que vencen dentro de los proximos 'dias' dias"""
    hoy_tupla = fecha_a_tupla(hoy)
    limite = fecha_proxima_a_vencer(hoy, dias)
    vencidos = {}
    proximos = {}
    for codigo in inventario:
        vence = fecha_a_tupla(inventario[codigo]["vence"])
        if vence < hoy_tupla:
            vencidos[codigo] = inventario[codigo]
        elif vence <= limite:
            proximos[codigo] = inventario[codigo]

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
    """Imprime los productos de una categoria y el total de unidades disponibles"""
    categoria = categoria.strip().lower()
    encontrados = {}
    total_categoria = 0
    for codigo in inventario:
        if inventario[codigo]["categoria"] == categoria:
            encontrados[codigo] = inventario[codigo]
            total_categoria = total_categoria + inventario[codigo]["cantidad"]

    imprimir_titulo(f"Stock de la categoria {categoria}")
    if encontrados == {}:
        print(f"No hay productos registrados en la categoria {categoria}.")
        return
    imprimir_productos(encontrados)
    print(f"Total de unidades en {categoria}: {total_categoria}")

def imprimir_historial(historial, categoria, fecha):
    """Muestra los movimientos del historial. Se puede filtrar por categoria y/o por fecha (vacio = todos)"""
    categoria = categoria.strip().lower()
    fecha = fecha.strip()
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

    print("FECHA".ljust(11) + "TIPO".ljust(6) + "CODIGO".ljust(11) + "CATEGORIA".ljust(12) + "NOMBRE".ljust(26)
          + "CANT.".rjust(6) + "UNITARIO".rjust(9) + "TOTAL".rjust(9))
    print(linea("-"))
    for mov in encontrados:
        if mov[6] > 0:
            tipo = "ALTA"
        else:
            tipo = "BAJA"
        print(mov[3].ljust(11) + tipo.ljust(6) + mov[0].ljust(11) + recortar(mov[1].capitalize(), 11).ljust(12)
              + recortar(mov[2], 24).ljust(26) + str(abs(mov[6])).rjust(6) + f"${mov[4]}".rjust(9) + f"${mov[5]}".rjust(9))
    print(linea("-"))
    print(f"Total de movimientos: {len(encontrados)}")

def valorizar_inventario(inventario):
    """Calcula el valor total del inventario (costo por cantidad de cada producto)"""
    imprimir_titulo("Valorizacion del inventario")
    if inventario == {}:
        print("No hay productos registrados en el inventario.")
        return
    total = 0
    for datos in inventario.values():
        total = total + datos["costo"] * datos["cantidad"]
    print("Cantidad de productos:".ljust(30) + str(len(inventario)).rjust(15))
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
hoy = str(datetime.now())[:10].replace("-", "/")   # fecha de hoy como texto AAAA/MM/DD

imprimir_titulo("Sistema de gestion de inventario")
imprimir_menu()
opcion = validar_numero(input("Elija una opción: "))
while opcion != 11:
    if opcion == 1:
        imprimir_inventario(inventario)

    elif opcion == 2:
        codigo = validar_codigo(input("Ingrese el codigo del producto (9 digitos): "))
        if codigo in inventario:
            print(f"\n>> El producto ya existe: '{inventario[codigo]['nombre']}'. Se sumaran unidades a su stock.")
            cantidad = validar_numero(input("Ingrese la cantidad de unidades que ingresan: "))
            reponer_stock(inventario, historial, codigo, cantidad, hoy)
        else:
            print("Categorias existentes:", ", ".join(sorted(obtener_categorias(inventario))))
            categoria = validar_categoria(input("Ingrese la categoria del producto (existente o nueva): "))
            nombre = validar_nombre(input("Ingrese el nombre del producto: "))
            vence = validar_fecha_actual(input("Ingrese la fecha de vencimiento del producto (AAAA/MM/DD): "), hoy)
            costo = validar_numero(input("Ingrese el costo del producto: "))
            cantidad = validar_numero(input("Ingrese la cantidad de articulos disponibles: "))
            agregar_producto(inventario, historial, codigo, categoria, nombre, vence, costo, cantidad, hoy)

    elif opcion == 3:
        codigo = validar_codigo(input("Ingrese el codigo del producto a dar de baja: "))
        cantidad = validar_numero(input("Ingrese la cantidad de unidades que quiera dar de baja: "))
        dar_de_baja(historial, inventario, codigo, cantidad, hoy)

    elif opcion == 4:
        codigo = validar_codigo(input("Ingrese el codigo del producto a modificar: "))
        if codigo not in inventario:
            print(f"\n>> No se encontro ningun producto con el codigo {codigo}.")
        else:
            print("1. Categoria \n2. Costo \n3. Cantidad \n4. Salir")
            opcion_mod = validar_numero(input("¿Qué desea modificar?: "))
            while opcion_mod < 1 or opcion_mod > 4:
                opcion_mod = validar_numero(input("Opción inválida. Ingrese una opción válida: "))
            if opcion_mod != 4:
                nuevo_valor = input("Ingrese el nuevo valor: ")
                modificar_producto(inventario, codigo, opcion_mod, nuevo_valor)

    elif opcion == 5:
        termino = validar_no_es_vacio(input("Ingrese el codigo, nombre o categoria a buscar: "))
        buscar_producto(inventario, termino)

    elif opcion == 6:
        dias = validar_numero(input("Ingrese la cantidad de dias a futuro para revisar vencimientos: "))
        productos_proximos_a_vencer(inventario, dias, hoy)

    elif opcion == 7:
        print("Categorias existentes:", ", ".join(sorted(obtener_categorias(inventario))))
        categoria = validar_categoria(input("Ingrese la categoria a consultar: "))
        imprimir_por_categoria(inventario, categoria)

    elif opcion == 8:
        categoria = input("Filtrar por categoria (Enter para ver todas): ")
        fecha = input("Filtrar por fecha AAAA/MM/DD (Enter para ver todas): ")
        if fecha.strip() != "" and not validar_formato_fecha(fecha.strip()):
            print("\n>> El formato de la fecha no es valido (AAAA/MM/DD).")
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
