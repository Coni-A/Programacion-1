from datetime import datetime

#QUE FALTA: 
# . HAY QUE HACER UNA FUNCION QUE MODIFIQUE LOS PRODUCTOS (creo que podria modificar precio sub_categoria y cantidad por si se equivoco a la hora ingresar un producto nuevo)
# . podriamos conciderar la opcion de dar un menu de categorias pre-definidas (es algo a pensar no algo definitivo por ahora no creeo necesario el cambio)
# . PENSANDO EN UN FUTURO PODRIAMOS CREAR UNA FUNCION DE ANALISIS DE DATOS DONDE LEYENDO EL HISTORIAL SE PODRIA IMPRIMIR LOS PRODUCTOS MAS VENDIDOS, ETC.
# . TESTEAR 

# Funciones de validacion 
def validar_no_es_vacio(cadena):
    """Valida que la cadena ingresada no esté vacía"""
    while cadena == "": 
        cadena = input("El valor no puede estar vacío. Ingrese nuevamente: ")
    return cadena

def validar_numero(numero):
    """Valida que el numero ingresado sea positivo y valido"""
    numero = validar_no_es_vacio(numero)
    while not numero.isdigit() or int(numero) <= 0:
        numero = input("Ingrese un numero positivo y valido: ")
    return int(numero)

def validar_codigo(codigo):
    """Valida que el codigo de identificacion tenga los 9 caracteres necesarios"""
    codigo = validar_no_es_vacio(codigo)
    while len(codigo) != 9:
        codigo = input("Ingrese un codigo de nueve (9) caracteres: ")
    return(codigo)

def validar_producto_existente(codigo, nombre):
    """Valida que el codigo ingresado se unico para el producto al que se le asigna y no se repita en el inventario"""
    for producto in inventario:
        while str(producto[0]) == str(codigo) and str(producto[2]) != str(nombre):
            codigo = input(f"El codigo no coincide con el nombre del producto ingresado.\nIngrese el codigo nuevamente: ")
            nombre = input("Ingrese el nombre nuevamente:")
    return codigo, nombre
    
def validar_fecha(fecha):
    """Valida que la fecha ingresada este en el formato AAAA/MM/DD y no sea una fecha pasada"""
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
        fecha = input("Ingrese nuevamente (AAAA/MM/DD): ")
    return fecha

#Funciones principales 

def crear_inventario():
    """Crea y devuelve el inventario inicial."""
    #El inventario llevara el siguiente orden de caracteristicas: [codigo, sub categoria, nombre, fecha de vencimiento, costo, cantidad]
    return [[123456789, 'lacteos', 'Leche entera la Scerenisima por 1l', '2027/12/30', 3000, 200],
            [987654321, 'lacteos', 'Queso muzzarela La Blanca por 500gm', '2026/09/20', 7000, 120]]

def crear_historial():
    """Crea y devuelve un historial de los movimientos (bajas y altas) de los productos."""
    #El historial llevara el siguiente orden : [codigo, sub categoria, nombre, fecha de movimiento, precio unitario, precio total, cantidad]
    #En caso de ser una baja deveria figurar un signo '-' (menos o negativo) en la cantidad 
    return [[123456789, 'lacteos', 'Leche entera la Scerenisima por 1l', '2026/07/30', 3000, 600000, 200],
            [987654321, 'lacteos', 'Queso muzzarela La Blanca por 500gm', '2026/03/20', 7000, 140000, -20]]

def imprimir_inventario(inventario):
    """Muestra por terminal todos los productos, con sus categorias, que se encuentren en el inventario"""
    if inventario == []:
        print("No hay productos registrados en el inventario.")
        return
    print("Productos registrados en el inventario:")
    for i, producto in enumerate(inventario):
        print('\n')
        print(i+1,". Codigo de identificacion: ", producto[0],'\n' " Categoria: ", producto[1], '\n' " Nombre : ", producto[2],'\n' " Fecha de vencimiento: ", producto[3],'\n' " Costo: $", producto[4], '\n'" Cantidad disponibles: ", producto[5])
  
def agregar_producto(inventario, codigo, sub_categoria, nombre, fecha_de_vencimiento, costo, cantidad, historial,hoy):
    """Agrega un nuevo producto al inventario"""
    validar_producto_existente(codigo, nombre)
    costo_total = cantidad*costo
    inventario.append([codigo, sub_categoria, nombre, fecha_de_vencimiento, costo, cantidad])
    historial.append([codigo, sub_categoria, nombre, hoy, costo, costo_total, cantidad])
    print("Se a agregado el producto.", nombre,"con éxito.")

def dar_de_baja(historial, inventario, codigo, cantidad_baja, hoy):
    """Da de baja una cantidad de productos del inventario, en caso de bajar el total de un producto el mismo se elimina del inventario"""
    for producto in inventario:
        if str(producto[0]) == str(codigo):
            costo_total = cantidad_baja * producto[4]
            if cantidad_baja == producto[5]:
                historial.append([codigo, producto[1], producto[2], hoy, producto[4], costo_total, -cantidad_baja])
                inventario.remove(producto)
                print("Se elimino el producto", producto[2], "del inventario (stock en 0).")
            elif cantidad_baja < producto[5]:
                producto[5] = producto[5] - cantidad_baja
                historial.append([codigo, producto[1], producto[2], hoy, producto[4], costo_total, -cantidad_baja])
                print("Se dieron de baja", cantidad_baja, "unidad(es) de", producto[2], ". Quedan", producto[5], ".")
            else:
                print("No es posible eliminar más unidades de las que se encuentran disponibles en el inventario ")          
    else:
        print("No se encontro ningun producto con el codigo", codigo)  

def Modificar_producto():
    pass

def buscar_producto(termino, inventario):
    """Busca un producto en el inventario por codigo o por nombre"""
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
    """Calcula a partir de la fecha actual y con la cantidad de dias ingresado para calcular la fecha de vencimiento a futuro"""
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
    """Compara e imprime los productos con una fecha de vencimiento menor a la fecha limite"""
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
    """Imprime todos los productos del inventario de la categoria seleccionada"""
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

def imprimir_historial(historial):
    """Muestra por terminal todos los productos, con sus categorias, que se encuentren en el inventario"""
    print("Historial:")
    for i, movimiento in enumerate(historial):
        print('\n')
        print(i+1,". Codigo de identificacion: ", movimiento[0],'\n' " Categoria: ", movimiento[1], '\n' " Nombre : ", movimiento[2],'\n' " Fecha de movimiento: ", movimiento[3],'\n' " Costo unitario: $", movimiento[4],'\n' " Costo total: $", movimiento[5],'\n' " Cantidad: ", movimiento[6])
    if historial == [ ]:
        print("No hay movimientos resgistrados en el historial.")

def valorizar_inventario(inventario):
    "La funcion se encarga de computar el precio de cada producto por la cantidad disponible del mismo y asi devolver el valor total de los activos del inventario"
    total = 0
    for producto in inventario:
        total += (producto[4] * producto[5])
    print("Valor total del inventario: $", total)

def imprimir_menu():
    """Imprime el menu con sus opciones"""
    print("Menu de inicio")
    print("1. Mostrar inventario")
    print("2. Agregar producto")
    print("3. Dar de baja producto")
    print("4. Buscar producto")
    print("5. Ver productos por vencer")
    print("6. Imprimir stock por categoria")
    print("7. Imprimir Historial")
    print("8. Valorizar inventario")
    print("9. Salir")

# Programa principal 
inventario = crear_inventario()
historial = crear_historial()
hoy = datetime.now()
print("\n")
print("Sistema de gestion de inventario")
imprimir_menu()
opcion = validar_numero(input("Elija una opción: "))
while opcion != 9:

    if opcion == 1:
        imprimir_inventario(inventario)
    elif opcion == 2:
        codigo_producto = validar_codigo(input("Ingrese el codigo del producto: "))
        categoria = input("Ingrese la categoria del producto: ")
        nombre_producto = input("Ingrese el nombre del producto: ")
        fecha_ven = validar_fecha(input("Ingrese la fecha de vencimiento del producto (AAAA/MM/DD): "))
        costo = validar_numero(input("Ingrese el costo del producto: "))
        cantidad_disponible = validar_numero(input("Ingrese la cantidad de articulos disponibles: "))
        agregar_producto(inventario, codigo_producto, categoria, nombre_producto, fecha_ven, costo, cantidad_disponible, historial, hoy)
    elif opcion == 3:
        codigo = validar_codigo(input("Ingrese el codigo del producto a dar de baja: "))
        cantidad = validar_numero(input("Ingrese la cantidad de unidades que quiera dar de baja:"))
        
        dar_de_baja(historial, inventario, codigo, cantidad, hoy)
    elif opcion == 4:
        Producto = input("Ingrese el nombre o codigo del producto a buscar ")
        buscar_producto(Producto, inventario)
        #no estoy convencida de la funcion yo pondria un menu de busqueda
    elif opcion == 5:
        dias = validar_numero(input("Ingrese la cantidad de dias a futuro para revisar vencimientos: "))
        productos_proximos_a_vencer(inventario, dias)
    elif opcion == 6:
        categoria = input("Ingrese la categoria a consultar (ej: lacteos, higiene): ")
        imprimir_por_categoria(categoria, inventario)
    elif opcion == 7:
        imprimir_historial(historial)
    elif opcion == 8:
        valorizar_inventario(inventario)
    else: 
        print("Opción inválida. Intente nuevamente.")

    imprimir_menu()
    opcion = validar_numero(input("Elija una opción: ")) 
print("Programa finalizado")
