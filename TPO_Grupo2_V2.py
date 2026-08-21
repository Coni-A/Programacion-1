# - datetime.now() se usa unicamente para obtener el dia de hoy
# - La validacion de que una fecha ingresada exista realmente (ej: no hay
#   30 de febrero) se hace a mano, con es_bisiesto() y dias_en_mes()
# - La comparacion de fechas para "productos por vencer" tambien se hace
#   a mano, convirtiendo cada fecha a un numero de dia con fecha_a_numero()
#
# Mantiene todas las funciones ya pedidas por el equipo (dar de baja,
# stock por categoria, verificaciones de input, etc.)

from datetime import datetime

# Funciones Principales
""" El inventario llevara el siguiente orden de caracteristicas: [codigo, sub categoria, nombre, fecha de vencimiento, costo, cantidad]"""

inventario = [[123456789, 'lacteos', 'Leche entera la Scerenisima por 1l', '10/09/2027', 3000, 200],
              [987654321, 'lacteos', 'Queso muzzarela La Blanca por 500gm', '13/12/2027', 7000, 120]]


def imprimir_inventario():
    print("Productos registrados en el inventario:")
    for i, producto in enumerate(inventario):
        print(i+1,". Codigo de identificacion: ", producto[0],'\n' " Categoria: ", producto[1], '\n' " Nombre : ", producto[2],'\n' " Fecha de vencimiento: ", producto[3],'\n' " Costo: $", producto[4], '\n'" Cantidad disponibles: ", producto[5])
    if inventario == [ ]:
        print("No hay productos registrados en el inventario.")


def codigo_existe(codigo):
    for producto in inventario:
        if str(producto[0]) == str(codigo):
            return True
    return False


def agregar_producto(codigo, sub_categoria, nombre, fecha_de_vencimiento, costo, cantidad):
    if codigo_existe(codigo):
        print("Ya existe un producto con el codigo", codigo, ". No se agrego el producto.")
        return
    producto = [codigo, sub_categoria, nombre, fecha_de_vencimiento, costo, cantidad]
    inventario.append(producto)
    print("Se a agregado el producto.",producto[2],"con éxito.")


def dar_de_baja(codigo, cantidad_baja):
    for producto in inventario:
        if str(producto[0]) == str(codigo):
            if cantidad_baja >= producto[5]:
                inventario.remove(producto)
                print("Se elimino el producto", producto[2], "del inventario (stock en 0).")
            else:
                producto[5] = producto[5] - cantidad_baja
                print("Se dieron de baja", cantidad_baja, "unidad(es) de", producto[2], ". Quedan", producto[5], ".")
            return
    print("No se encontro ningun producto con el codigo", codigo)


def buscar_producto(termino):
    encontrados = []
    for producto in inventario:
        if termino.lower() in str(producto[0]).lower() or termino.lower() in producto[2].lower():
            encontrados.append(producto)

    if encontrados == []:
        print("No se encontraron productos con ese criterio.")
    else:
        print("Se encontraron", len(encontrados), "producto(s):")
        for producto in encontrados:
            print("- Codigo:", producto[0], " Nombre:", producto[2], " Categoria:", producto[1],
                  " Costo: $", producto[4], " Cantidad:", producto[5])


# --- Manejo de fechas SIN datetime.strptime (solo aritmetica manual) ---

def es_bisiesto(anio):
    return (anio % 4 == 0 and anio % 100 != 0) or (anio % 400 == 0)


def dias_en_mes(mes, anio):
    dias_por_mes = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if mes == 2 and es_bisiesto(anio):
        return 29
    return dias_por_mes[mes - 1]


def fecha_valida(fecha_texto):
    # Formato esperado: DD/MM/AAAA
    partes = fecha_texto.split("/")
    if len(partes) != 3:
        return False

    dia_texto, mes_texto, anio_texto = partes

    if es_numero(dia_texto) == False or es_numero(mes_texto) == False or es_numero(anio_texto) == False:
        return False

    dia = int(dia_texto)
    mes = int(mes_texto)
    anio = int(anio_texto)

    if mes < 1 or mes > 12:
        return False
    if anio < 1:
        return False
    if dia < 1 or dia > dias_en_mes(mes, anio):
        return False

    return True


def fecha_a_numero(dia, mes, anio):
    # Convierte una fecha a una cantidad de dias transcurridos desde el
    # año 1, para poder comparar dos fechas sin usar datetime.strptime.
    total_dias = 0
    for a in range(1, anio):
        total_dias = total_dias + (366 if es_bisiesto(a) else 365)
    for m in range(1, mes):
        total_dias = total_dias + dias_en_mes(m, anio)
    total_dias = total_dias + dia
    return total_dias


def productos_por_vencer(dias_limite):
    hoy = datetime.now()  # unico uso permitido de datetime: la fecha actual
    hoy_numero = fecha_a_numero(hoy.day, hoy.month, hoy.year)

    print("Productos que vencen dentro de los proximos", dias_limite, "dias:")
    encontrados = False

    for producto in inventario:
        dia, mes, anio = producto[3].split("/")
        venc_numero = fecha_a_numero(int(dia), int(mes), int(anio))
        dias_restantes = venc_numero - hoy_numero

        if dias_restantes >= 0 and dias_restantes <= dias_limite:
            print("-", producto[2], "vence en", dias_restantes, "dia(s) (", producto[3], ")")
            encontrados = True

    if encontrados == False:
        print("No hay productos por vencer en ese rango.")


def imprimir_por_categoria(categoria):
    encontrados = []
    for producto in inventario:
        if producto[1].lower() == categoria.lower():
            encontrados.append(producto)

    if encontrados == []:
        print("No hay productos registrados en la categoria", categoria)
        return

    print("Stock disponible en la categoria", categoria, ":")
    total_categoria = 0
    for producto in encontrados:
        print("-", producto[2], ": ", producto[5], "unidad(es)")
        total_categoria = total_categoria + producto[5]
    print("Total de unidades en", categoria, ":", total_categoria)


def valorizar_inventario():
    total = 0
    for producto in inventario:
        total = total + (producto[4] * producto[5])
    print("Valor total del inventario: $", total)


# --- Funciones de verificacion de inputs ---

def es_numero(valor):
    try:
        float(valor)
        return True
    except ValueError:
        return False


def es_alfabetico(valor):
    return valor.replace(" ", "").isalpha()


def no_vacio(valor):
    return valor.strip() != ""


def verificacion_codigo(codigo):
    if no_vacio(codigo) == False:
        print("El codigo no puede estar vacio.")
        return False
    if es_numero(codigo) == False:
        print("El codigo debe ser numerico.")
        return False
    if codigo_existe(codigo):
        print("Ya existe un producto con ese codigo.")
        return False
    return True


def pedir_fecha_valida():
    fecha_ok = False
    while fecha_ok == False:
        fecha_ven = input("Ingrese la fecha de vencimiento del producto (DD/MM/AAAA): ")
        if fecha_valida(fecha_ven):
            fecha_ok = True
        else:
            print("Fecha invalida. Revise el formato DD/MM/AAAA y que el dia y el mes existan (ej: no hay 30 de febrero).")
    return fecha_ven


def mostrar_menu():
    print("Menu de inicio")
    print("1. Mostrar inventario")
    print("2. Agregar producto")
    print("3. Dar de baja producto")
    print("4. Buscar producto")
    print("5. Ver productos por vencer")
    print("6. Imprimir stock por categoria")
    print("7. Valorizar inventario")
    print("8. Salir")


print("\n")
print("Sistema de gestion de inventario")
mostrar_menu()
opcion = input("Elija una opción: ")
while opcion != "8":

    if opcion == "1":
        imprimir_inventario()

    elif opcion == "2":
        codigo = input("Ingrese el codigo del producto: ")
        while verificacion_codigo(codigo) == False:
            codigo = input("Ingrese el codigo del producto: ")

        categoria = input("Ingrese la categoria del producto: ")
        while no_vacio(categoria) == False:
            categoria = input("La categoria no puede estar vacia. Ingrese la categoria del producto: ")

        nombre = input("Ingrese el nombre del producto: ")
        while no_vacio(nombre) == False:
            nombre = input("El nombre no puede estar vacio. Ingrese el nombre del producto: ")

        fecha_ven = pedir_fecha_valida()

        costo = input("Ingrese el costo del producto: ")
        while es_numero(costo) == False:
            costo = input("El costo debe ser un numero. Ingrese el costo del producto: ")
        costo = int(float(costo))

        cantidad = input("Ingrese la cantidad de articulos disponibles: ")
        while es_numero(cantidad) == False:
            cantidad = input("La cantidad debe ser un numero. Ingrese la cantidad de articulos disponibles: ")
        cantidad = int(float(cantidad))

        agregar_producto(codigo, categoria, nombre, fecha_ven, costo, cantidad)

    elif opcion == "3":
        codigo = input("Ingrese el codigo del producto a dar de baja: ")
        while no_vacio(codigo) == False or es_numero(codigo) == False:
            codigo = input("Codigo invalido. Ingrese el codigo del producto a dar de baja: ")

        cantidad_baja = input("Ingrese la cantidad a dar de baja: ")
        while es_numero(cantidad_baja) == False:
            cantidad_baja = input("La cantidad debe ser un numero. Ingrese la cantidad a dar de baja: ")
        cantidad_baja = int(float(cantidad_baja))

        dar_de_baja(codigo, cantidad_baja)

    elif opcion == "4":
        termino = input("Ingrese el codigo o nombre del producto a buscar: ")
        buscar_producto(termino)

    elif opcion == "5":
        dias = input("¿Productos que vencen en los proximos cuantos dias? (ej: 90 para 3 meses): ")
        while es_numero(dias) == False:
            dias = input("Ingrese un numero de dias valido: ")
        productos_por_vencer(int(float(dias)))

    elif opcion == "6":
        categoria = input("Ingrese la categoria a consultar (ej: lacteos, higiene): ")
        imprimir_por_categoria(categoria)

    elif opcion == "7":
        valorizar_inventario()

    elif opcion == "8":
        print("Programa finalizado")

    else:
        print("Opción inválida. Intente nuevamente.")

    if opcion != "8":
        mostrar_menu()
        opcion = input("Elija una opción: ")
