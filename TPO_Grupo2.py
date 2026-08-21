from datetime import datetime

# Funciones Principales



def crear_inventario():
    """Crea y devuelve el inventario inicial. El inventario llevara el siguiente orden de caracteristicas: [codigo, sub categoria, nombre, fecha de vencimiento, costo, cantidad"""
    return [[123456789, 'lacteos', 'Leche entera la Scerenisima por 1l', '2027/12/30', 3000, 200],
            [987654321, 'lacteos', 'Queso muzzarela La Blanca por 500gm', '2027/09/20', 7000, 120]]


def validar_no_es_vacio(cadena):
    """Valida que la cadena ingresada no esté vacía"""

    while cadena == "": 
        cadena = input("El valor no puede estar vacío. Ingrese nuevamente: ")
    return cadena

def validar_numero(num):
    """Valida que el numero ingresado sea positivo y valido"""

    num = validar_no_es_vacio(num)
    while not num.isdigit() or int(num) <= 0:
        num = input("Ingrese un numero positivo y valido: ")
    return int(num)

def validar_codigo(cod):
    "Valida que el codigo de identificacion tenga los 9 caracteres necesarios"
    cod = validar_no_es_vacio(cod)
    while len(cod) != 9:
        cod = input("Ingrese un codigo de nueve (9) caracteres: ")
    return(cod)
    
def validar_fecha(fecha):
    """Valida que la fecha ingresada esté en el formato AAAA/MM/DD y no sea una fecha pasada"""

    fecha = validar_no_es_vacio(fecha)
    valido = False
    while not valido:
        if len(fecha) == 10 and fecha[4] == '/' and fecha[7] == '/' and fecha[:4].isdigit() and fecha[5:7].isdigit() and fecha[8:].isdigit():

            anio = int(fecha[:4])
            mes = int(fecha[5:7])
            dia = int(fecha[8:])

            if 1 <= mes <= 12 and 1 <= dia <= 31:
                hoy = datetime.now()
                hoy_anio = int(str(hoy)[:4])
                hoy_mes = int(str(hoy)[5:7])
                hoy_dia = int(str(hoy)[8:10])

                if (anio > hoy_anio) or (anio == hoy_anio and mes > hoy_mes) or (anio == hoy_anio and mes == hoy_mes and dia >= hoy_dia):
                    valido = True
                    continue
        fecha = input("Error, formato de fecha inválido o fecha pasada. Ingreselo nuevamente (AAAA/MM/DD): ")

    return fecha

def imprimir_inventario(inventario):
    "la funcion imprimir_inventario muestra por terminal todos los productos, con sus categorias, que se encuentren en el inventario"
    print("Productos registrados en el inventario:")
    for i, producto in enumerate(inventario):
        print('\n')
        print(i+1,". Codigo de identificacion: ", producto[0],'\n' " Categoria: ", producto[1], '\n' " Nombre : ", producto[2],'\n' " Fecha de vencimiento: ", producto[3],'\n' " Costo: $", producto[4], '\n'" Cantidad disponibles: ", producto[5])
    if inventario == [ ]:
        print("No hay productos registrados en el inventario.")

def agregar_producto(inventario, codigo, sub_categoria, nombre, fecha_de_vencimiento, costo, cantidad):
    "Agrega un producto nuevo al inventario"
    producto = [codigo, sub_categoria, nombre, fecha_de_vencimiento, costo, cantidad]
    inventario.append(producto)
    print("Se a agregado el producto.",producto[2],"con éxito.")

def mostrar_menu():
    print("Menu de inicio")
    print("1. Mostrar inventario")
    print("2. Agregar producto")
    print("3. Salir")


# Programa principal 
inventario = crear_inventario()
print("\n")
print("Sistema de gestion de inventario")
mostrar_menu()
opcion = validar_numero(input("Elija una opción: "))
while opcion != 3:

    if opcion == 1:
        imprimir_inventario(inventario)

    elif opcion == 2:
        codigo_producto = validar_codigo(input("Ingrese el codigo del producto: "))
        categoria = input("Ingrese la categoria del producto: ")
        nombre_producto = input("Ingrese el nombre del producto: ")
        fecha_ven = validar_fecha(input("Ingrese la fecha de vencimiento del producto (AAAA/MM/DD): "))
        costo = validar_numero(input("Ingrese el costo del producto: "))
        cantidad_disponible = validar_numero(input("Ingrese la cantidad de articulos disponibles: "))
        agregar_producto(inventario, codigo_producto, categoria, nombre_producto, fecha_ven, costo, cantidad_disponible)
    else:
        print("Opción inválida. Intente nuevamente.")

    mostrar_menu()
    opcion = validar_numero(input("Elija una opción: ")) 
print("Programa finalizado")

