# Programacion-1

*Sistema de gestion de inventarios:*
- fecha de vencimiento
- codigo de identificacion
- costo
- cantidad
- nombre del producto o articulo
- tipo de producto (secciones o sub categorias ej: lacteos, higiene, etc.)

*modulos necesarios para el sistema*
- fecha de vencimiento:datetime (comparacion fecha de vencimiento con fecha actual)

*Funciones necesarias para el sistema*
- funcion que imprima el inventario ((funciona)) 

- funcion que permita dar de baja productos, el decir reducir la cantidad que quedan del mismo y en caso de que su cantidad sea igual a 0 se lo elimine

- funcion para agregar productos al inventario (debe de agragar todas las categorias de forma obligatoria). (funciona)

- funcion de busqueda de un producto en especifico por nombre o codigo

- funcion que imprima todos los productos "prontos a vencer" (vencimiento cercano, se debe elegir una fecha a futuro de la actual por ejemplo en los proximos tres meses)

- funcion impresion por categorias, se debe poder imprimir el stock disponible por sub categoria 

*Funciones respecto a los input*

- funcion verificacion es numero (funciona)
- funcion verificacion es alphabetico
- funcion verificacion no es vacio (funciona)
- funcion verificacion de codigo (funciona)

*QUE FALTA:*
 - FUNCION PARA CAMBIAR PRECIOS DE PRODUCTOS, LA MISMA SE PODRIA SUMAR A LA FUNCION BAJAS Y PODRIAMOS RENOMBRARLA COMO FUNCION MODIFICAR PRODUCTO
 - QUE LA FUNCION DAR DE BAJA TENGA UN CICLO WHILE Y HAY QUE AGREGARLE EL HISORIAL
 - podriamos conciderar la opcion de dar un menu de categorias pre-definidas (es algo a pensar no algo definitivo por ahora no creeo necesario el cambio)
 - PENSANDO EN UN FUTURO PODRIAMOS CREAR UNA FUNCION DE ANALISIS DE DATOS DONDE LEYENDO EL HISTORIAL SE PODRIA IMPRIMIR LOS PRODUCTOS MAS VENDIDOS, ETC.
 - HABRIA QUE RECONSIDERAR EL CODIGO DE IDENTIFICACION PORQUR VALIDAMOS QUE SEA UNICO CUANDO DEVERIAMOS VALIDAR QUE EL MISMO NO SE REPITA PARA UN PRODUCTO DE NOMBRE DISTINTO



