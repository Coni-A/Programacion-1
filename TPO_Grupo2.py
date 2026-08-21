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

def mostrar_menu():
    print("Menu de inicio")
    print("1. Mostrar inventario")
    print("2. Agregar producto")





print("\n")
print("Sistema de gestion de inventario")
mostrar_menu()
opcion = input("Elija una opción: ")
while opcion != "3":

    if opcion == "1":
        imprimir_inventario()

    elif opcion == "2":
        codigo = input("Ingrese el codigo del producto: ")
        categoria = input("Ingrese la categoria del producto: ")
        nombre= input("Ingrese el nombre del producto: ")
        fecha_ven = input("Ingrese la fecha de vencimiento del producto (DD:MM:AAAA): ")
        costo = int(input("Ingrese el costo del producto: "))
        cantidad = int(input("Ingrese la cantidad de articulos disponibles: "))
        agregar_producto(codigo, categoria, nombre, fecha_ven, costo, cantidad)

    elif opcion == "3":
        print("Programa finalizado")

    else:
        print("Opción inválida. Intente nuevamente.")

    mostrar_menu()
    opcion = input("Elija una opción: ") 

