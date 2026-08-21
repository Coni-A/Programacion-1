# Agrega funciones de búsqueda, control de vencimientos y valorización del inventario
#
# - buscar_producto(termino): busca productos por código o nombre
# - productos_por_vencer(dias_limite=30): compara la fecha de vencimiento con la fecha
#   actual usando datetime y avisa qué productos vencen pronto
# - valorizar_inventario(): calcula el valor total del inventario (costo * cantidad)
# - Se suman las opciones 3, 4 y 5 al menú; "Salir" pasa a la opción 6
#
# Mantiene la estructura y el estilo de código original (imprimir_inventario,
# agregar_producto, inventario como lista de listas)

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


def agregar_producto(codigo, sub_categoria, nombre, fecha_de_vencimiento, costo, cantidad):
    producto = [codigo, sub_categoria, nombre, fecha_de_vencimiento, costo, cantidad]
    inventario.append(producto)
    print("Se a agregado el producto.",producto[2],"con éxito.")


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


def productos_por_vencer(dias_limite=30):
    hoy = datetime.now()
    print("Productos que vencen dentro de los proximos", dias_limite, "dias:")
    encontrados = False

    for producto in inventario:
        fecha_venc = datetime.strptime(producto[3], "%d/%m/%Y")
        dias_restantes = (fecha_venc - hoy).days

        if dias_restantes >= 0 and dias_restantes <= dias_limite:
            print("-", producto[2], "vence en", dias_restantes, "dia(s) (", producto[3], ")")
            encontrados = True

    if encontrados == False:
        print("No hay productos por vencer en ese rango.")


def valorizar_inventario():
    total = 0
    for producto in inventario:
        total = total + (producto[4] * producto[5])
    print("Valor total del inventario: $", total)


def mostrar_menu():
    print("Menu de inicio")
    print("1. Mostrar inventario")
    print("2. Agregar producto")
    print("3. Buscar producto")
    print("4. Ver productos por vencer")
    print("5. Valorizar inventario")
    print("6. Salir")


print("\n")
print("Sistema de gestion de inventario")
mostrar_menu()
opcion = input("Elija una opción: ")
while opcion != "6":

    if opcion == "1":
        imprimir_inventario()

    elif opcion == "2":
        codigo = input("Ingrese el codigo del producto: ")
        categoria = input("Ingrese la categoria del producto: ")
        nombre= input("Ingrese el nombre del producto: ")
        fecha_ven = input("Ingrese la fecha de vencimiento del producto (DD/MM/AAAA): ")
        costo = int(input("Ingrese el costo del producto: "))
        cantidad = int(input("Ingrese la cantidad de articulos disponibles: "))
        agregar_producto(codigo, categoria, nombre, fecha_ven, costo, cantidad)

    elif opcion == "3":
        termino = input("Ingrese el codigo o nombre del producto a buscar: ")
        buscar_producto(termino)

    elif opcion == "4":
        productos_por_vencer()

    elif opcion == "5":
        valorizar_inventario()

    elif opcion == "6":
        print("Programa finalizado")

    else:
        print("Opción inválida. Intente nuevamente.")

    if opcion != "6":
        mostrar_menu()
        opcion = input("Elija una opción: ")
