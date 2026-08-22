from datetime import datetime

#QUE FALTA: 
# 1. HISTORIAL 
# 2. FUNCION PARA CAMBIAR PRECIOS DE PRODUCTOS, LA MISMA SE PODRIA SUMAR A LA FUNCION BAJAS Y PODRIAMOS RENOMBRARLA COMO FUNCION MODIFICAR PRODUCTO
# 3. QUE LA FUNCION DAR DE BAJA TENGA UN CICLO WHILE
# 4. podriamos conciderar la opcion de dar un menu de categorias pre-definidas (es algo a pensar no algo definitivo por ahora no creeo necesario el cambio)
# 5. FALTA DOCUMENTAR MUCHAS FUNCIONES (escribir que hacen entre " " para el comando help)

# Funciones Principales

def crear_inventario():
    """Crea y devuelve el inventario inicial. El inventario llevara el siguiente orden de caracteristicas: [codigo, sub categoria, nombre, fecha de vencimiento, costo, cantidad"""
    return [[123456789, 'lacteos', 'Leche entera la Scerenisima por 1l', '2027/12/30', 3000, 200],
            [987654321, 'lacteos', 'Queso muzzarela La Blanca por 500gm', '2026/09/20', 7000, 120]]

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

def validar_codigo_existe(codigo):
    for producto in inventario:
        while str(producto[0]) == str(codigo):
            codigo = input("Ya existe un producto con el codigo", codigo, "Ingrese un codigo valido:")
        return codigo
    
def validar_fecha(fecha):
    """Valida que la fecha ingresada esté en el formato AAAA/MM/DD y no sea una fecha pasada"""
    fecha = validar_no_es_vacio(fecha)
    valido = False

    hoy = datetime.now()
    hoy_anio = int(str(hoy)[:4])
    hoy_mes = int(str(hoy)[5:7])
    hoy_dia = int(str(hoy)[8:10])

    while not valido:
        
        if len(fecha) == 10 and fecha[4] == '/' and fecha[7] == '/' and fecha[:4].isdigit() and fecha[5:7].isdigit() and fecha[8:].isdigit():

            anio = int(fecha[:4])
            mes = int(fecha[5:7])
            dia = int(fecha[8:])

            if mes < 1 or mes > 12:
                print("El mes ingresado no es válido.")
            elif mes in [1, 3, 5, 7, 8, 10, 12] and (dia < 1 or dia > 31):
                print("El día no es válido para ese mes.")
            elif mes in [4, 6, 9, 11] and (dia < 1 or dia > 30):
                print("El día no es válido para ese mes.")
            elif mes == 2:
                if (anio % 4 == 0 and anio % 100 != 0) or (anio % 400 == 0):
                    if dia < 1 or dia > 29:
                        print("El día no es válido para febrero en año bisiesto.")
                    else:
                        valido = True
                else:
                    if dia < 1 or dia > 28:
                        print("El día no es válido para febrero.")
                    else:
                        valido = True
            else:
                valido = True

            if valido:
                if (anio < hoy_anio) or (anio == hoy_anio and mes < hoy_mes) or (anio == hoy_anio and mes == hoy_mes and dia < hoy_dia):
                    print("La fecha ingresada ya pasó.")
                    valido = False
                else:
                    return fecha
        else:
            print("El formato no es válido.")
        fecha = input("Ingrese nuevamente (YYYY-MM-DD): ")
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
    validar_codigo_existe(codigo)
    producto = [codigo, sub_categoria, nombre, fecha_de_vencimiento, costo, cantidad]
    inventario.append(producto)
    print("Se a agregado el producto.",producto[2],"con éxito.")

#Yo le agrgaria un ciclo while para que la persona pueda seguir trabajando sobre el mismo producto si se equivoca
#pero con estos cambio ahora ya no te deja sacar productos de mas 
def dar_de_baja(codigo, cantidad_baja):
    for producto in inventario:
        if str(producto[0]) == str(codigo):

            if cantidad_baja == producto[5]:
                inventario.remove(producto)
                print("Se elimino el producto", producto[2], "del inventario (stock en 0).")
            elif cantidad_baja< producto[5]:
                producto[5] = producto[5] - cantidad_baja
                print("Se dieron de baja", cantidad_baja, "unidad(es) de", producto[2], ". Quedan", producto[5], ".")
            else:
                print("No es posible eliminar más unidades de las que se encuentran disponibles en el inventario ")
    print("No se encontro ningun producto con el codigo", codigo)

def buscar_producto(termino, inventario):
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

def Fecha_proxima_a_vencer(dias):
    hoy = datetime.now()
    anio_limite = int(str(hoy)[:4])
    mes_limite = int(str(hoy)[5:7])
    dia_limite = int(str(hoy)[8:10])

    dia_limite += dias

    while True:
        if mes_limite in [1, 3, 5, 7, 8, 10, 12]:
            max_dias = 31
        elif mes_limite in [4, 6, 9, 11]:
            max_dias = 30
        else:
            if (anio_limite % 4 == 0 and anio_limite % 100 != 0) or (anio_limite % 400 == 0):
                max_dias = 29
            else:
                max_dias = 28

        if dia_limite > max_dias:
            dia_limite -= max_dias
            mes_limite += 1
            if mes_limite > 12:
                mes_limite = 1
                anio_limite += 1

        return anio_limite, mes_limite, dia_limite

def productos_proximos_a_vencer(inventario, dias):
    anio_limite, mes_limite, dia_limite = Fecha_proxima_a_vencer(dias)
    encontrados = []
    for producto in inventario:
        anio_ven, mes_ven, dia_ven = producto[3].split("/")
        anio_ven, mes_ven, dia_ven = int(anio_ven), int(mes_ven), int(dia_ven)

        if anio_ven < anio_limite:
            encontrados.append(producto)
        elif anio_ven == anio_limite and mes_ven < mes_limite:
            encontrados.append(producto)
        elif anio_ven == anio_limite and mes_ven == mes_limite and dia_ven < dia_limite:
            encontrados.append(producto)

    if encontrados == []:
        print("No se han encontrado productos")
    else:
        for producto in encontrados:
            print(producto)


def imprimir_por_categoria(categoria, inventario):

    encontrados = []
    for producto in inventario:
        if producto[1].lower() == categoria.lower():
            encontrados.append(producto)

    if encontrados == []:
        print("No hay productos registrados en la categoria", categoria)
        
    print("Stock disponible en la categoria", categoria, ":")
    total_categoria = 0
    for producto in encontrados:
        print("-", producto[2], ": ", producto[5], "unidad(es)")
        total_categoria = total_categoria + producto[5]
    print("Total de unidades en", categoria, ":", total_categoria)

def valorizar_inventario():
    "La funcion se encarga de computar el precio de cada producto por la cantidad disponible del mismo y asi devolver el valor total de los activos del inventario"
    total = 0
    for producto in inventario:
        total += (producto[4] * producto[5])
    print("Valor total del inventario: $", total)

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

# Programa principal 
inventario = crear_inventario()
print("\n")
print("Sistema de gestion de inventario")
mostrar_menu()
opcion = validar_numero(input("Elija una opción: "))
while opcion != 8:

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
    elif opcion == 3:
        codigo = validar_codigo(input("Ingrese el codigo del producto a dar de baja: "))
        dar_de_baja(codigo)
    elif opcion == 4:
        buscar_producto()
        #no estoy convencida de la funcion yo pondria un menu de busqueda
    elif opcion == 5:
        dias = validar_numero(input("Ingrese la cantidad de dias a futuro para revisar vencimientos: "))
        productos_proximos_a_vencer(inventario, dias)
    elif opcion == 6:
        categoria = input("Ingrese la categoria a consultar (ej: lacteos, higiene): ")
        imprimir_por_categoria(categoria)
    elif opcion == 7:
        valorizar_inventario()
    else: 
        print("Opción inválida. Intente nuevamente.")

    mostrar_menu()
    opcion = validar_numero(input("Elija una opción: ")) 
print("Programa finalizado")

