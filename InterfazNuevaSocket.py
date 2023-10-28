
import socket
import customtkinter
from tkinter import ttk
from tkinter import messagebox as mb
import os
from datetime import datetime
import datetime
from PIL import Image
#librerias para pdf
from tkinter import Tk, Button
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph,PageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch  # Importa la unidad "inch"
from PIL import ImageTk
from reportlab.platypus import Image as RLImage
import random

# Conexion con el servidor socket
host = socket.gethostname()
port = 5000
client_socket = socket.socket()

try:
    client_socket.connect((host, port))
except ConnectionRefusedError:
    mb.showerror("Error (Conexion)", "No se pudo conectar al servidor. Asegúrate de que el servidor esté activo.")
    exit()  # Salir de la aplicación si no se puede conectar al servidor

def select_frame_by_name(name):
    # establecer el color del boton seleccionado
    home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
    frame_2_button.configure(fg_color=("gray75", "gray25") if name == "frame_2" else "transparent")
    frame_3_button.configure(fg_color=("gray75", "gray25") if name == "frame_3" else "transparent")

    # mostrar frame seleccionado
    if name == "home":
        home_frame.grid(row=0, column=1, sticky="nsew")
    else:
        home_frame.grid_forget()
    if name == "frame_2":
        second_frame.grid(row=0, column=1, sticky="nsew")
    else:
        second_frame.grid_forget()
    if name == "frame_3":
        third_frame.grid(row=0, column=1, sticky="nsew")
    else:
        third_frame.grid_forget()

def home_button_event():
    select_frame_by_name("home")

def frame_2_button_event():
    select_frame_by_name("frame_2")

def frame_3_button_event():
    select_frame_by_name("frame_3")

def change_appearance_mode_event(new_appearance_mode):
    customtkinter.set_appearance_mode(new_appearance_mode)

def enviar_y_recibir_datos():
    global data1
    try:
        # Obtener el dato ingresado por el usuario
        dato_ingresado = home_frame_entry.get()
        if not dato_ingresado:
            mb.showerror("Error", "Por favor, ingrese un código de cliente para realizar la búsqueda.")
            return
        # Enviar el dato al servidor
        client_socket.send(f"c{dato_ingresado}".encode())

        # Recibir la respuesta del servidor

        data1 = client_socket.recv(1024).decode()
        print('Recibido del servidor: ' + data1)

        if data1 == "[]":
            mb.showinfo("Sin Cuotas Pendientes", "El cliente no tiene cuotas Pendientes.")
            for record in tabla.get_children():
                tabla.delete(record)
            return
        if data1 == "Cliente inexistente":
            mb.showerror("Error", "Codigo de cliente inexistente.")
            for record in tabla.get_children():
                tabla.delete(record)
            return
        # Limpiar la tabla antes de insertar nuevos datos
        for record in tabla.get_children():
            tabla.delete(record)

        # Convertir las tuplas en listas y luego insertar en la tabla
        for row in eval(data1):
            # Convertir la tupla en una lista
            row_list = list(row)
            # Insertar los datos en la tabla
            tabla.insert("", "end", values=row_list)
        return data1
        # Cerrar la conexión con el servidor
    #  client_socket.close()

    except Exception as e:
        print("Se produjo un error:", str(e))

def on_row_select(event):
    global valor1
    # Verificar si alguna fila ha sido seleccionada
    selected_items = tabla.selection()
    if not selected_items:
        mb.showerror("Error", "Por favor, seleccione al menos una fila antes de continuar.")
        return
    cuota_minima = float('inf')  # Inicializa con un valor infinito
    datos_filas = []

    # Obtener los valores de ID_CLIENTE y CUOTA de las filas seleccionadas
    for selected_item in selected_items:
        id_cliente = tabla.item(selected_item, "values")[0]
        cuota = float(tabla.item(selected_item, "values")[1])  # Convertir cuota a número decimal
        datos_filas.append(f"{id_cliente}:{cuota}")
        valor1= id_cliente

        # Actualiza la cuota mínima si encontramos una cuota menor
        if cuota < cuota_minima:
            cuota_minima = cuota

    cuota_menor_encontrada = False
    # Verificar si hay alguna fila con cuota menor que la cuota mínima
    all_items = tabla.get_children()
    for item in all_items:
        item_cuota = float(tabla.item(item, "values")[1])  # Convertir cuota a número decimal
        if item_cuota < cuota_minima:
            cuota_menor_encontrada = True
            break

    if cuota_menor_encontrada:
        mb.showerror("Error", "Por favor efectue el pago de la cuota más próxima a vencer")

    else:
        # Enviar datos al servidor
        client_socket.send(f"A{'|'.join(datos_filas)}".encode())
        data = client_socket.recv(1024).decode()
        print(data)

        # Comparar la respuesta del servidor y mostrar la ventana emergente correspondiente
        if data == "Actualización realizada correctamente.":
            # mb.showinfo("Pago efectuado", "La actualización se realizó correctamente.")
            respuesta = mb.askquestion("Confirmación",
                                       "La actualización se ha realizado correctamente. ¿Desea ver sus pagos?")
            if respuesta == 'yes':
                generar_factura()
                #   # Llama a la función para ver las facturas
            else:
                pass  # No se realiza ninguna acción adicional en caso de "No"
            home_frame_entry.delete(0, "end")
            client_socket.send(f"c{id_cliente}".encode())
            data1 = client_socket.recv(1024).decode()
            # Limpiar la tabla antes de insertar nuevos datos
            for record in tabla.get_children():
                tabla.delete(record)
            for row in eval(data1):
                # Convertir la tupla en una lista
                row_list = list(row)
                # Insertar los datos en la tabla
                tabla.insert("", "end", values=row_list)
        else:
            mb.showerror("Error al realizar el pago", "Hubo un error al procesar el pago.")

def pagar():
    on_row_select(None)

    
    
def generar_factura():
    # Crear un nuevo documento PDF
    doc = SimpleDocTemplate("facturacliente.pdf", pagesize=letter)
    story = []

    # Crear un rectángulo para dividir la tabla y el encabezado
    rectangulo = Table([[Paragraph("<u></u>", getSampleStyleSheet()['Normal'])]], colWidths=[600])
    rectangulo.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), '#2579db'),  # Color del fondo del rectángulo
        ('LINEABOVE', (0, 0), (0, 0), 1, colors.black),  # Línea superior
        ('LINEBELOW', (0, 0), (0, 0), 1, colors.black),  # Línea inferior
    ]))

    # Agregar el rectángulo a la historia
    story.append(rectangulo)
    # Ruta de la imagen que deseas agregar
    imagen_path = "../examen1sa/logo.png"

    #generamos el numero de factura
    numero_factura = random.randint(0, 99999999)
    # Formatea el número de factura en el formato deseado
    factura_formateada = f"{numero_factura:08d}"
    # Construye el número de factura completo
    numero_completo = f"000-002-01-{factura_formateada}"

    #para la hora
    # Obtener la hora actual
    hora_actual = datetime.datetime.now().strftime("%I:%M %p")

    # Crear un párrafo con la hora en el formato deseado
    hora_paragraph = f": {hora_actual}"


    # Crear una tabla para el encabezado
    encabezado_data = [
        [
            # Paragraph("<b>FACTURA</b><br/>", getSampleStyleSheet()['Normal']),
            RLImage(imagen_path, width=1.5 * inch, height=1 * inch),  # Agregar la imagen aquí
            '',
            Paragraph(
                f"<b>Factura: {numero_completo}</b><br/>Fecha: {fecha_actual}<br/>Hora: {hora_paragraph}<br/>si desea reversion sobre su factura tiene 24 horas disponibles",
                getSampleStyleSheet()['Normal'])
        ]
    ]
    # Definir el ancho de las columnas
    col_widths = [1 * inch, 3.5 * inch, 2 * inch, 1 * inch]

    # Definir la tabla del encabezado
    encabezado = Table(encabezado_data, colWidths=col_widths)

    # Estilo de la tabla
    encabezado.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
    ]))

    story.append(encabezado)

    # Crear un rectángulo para dividir la tabla y el encabezado
    rectangulo = Table([[Paragraph("<u></u>", getSampleStyleSheet()['Normal'])]], colWidths=[600])
    rectangulo.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), '#2579db'),  # Color del fondo del rectángulo
        ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),  # Línea superior
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),  # Línea inferior
    ]))

    # Agregar el rectángulo a la historia
    story.append(rectangulo)
    story.append(Spacer(1, 15))  # Espacio entre el encabezado y la tabla

    # esta tabla es para los datos que se van a seleccionar
    # Crear una lista de datos para la tabla
    data = [
        ["ID_CLIENTE", "CUOTA", "MONTO", "PAGO_FECHA_REALIZACION", "REFERENCIA"]
    ]

    #obtener todo el monto
    monto_total = 0

    client_socket.send(f"b{valor1}".encode())
    data1 = client_socket.recv(1024).decode()
    print("estoy recibiendo esto: ", data1)
    for row in eval(data1):
            # Convertir la tupla en una lista
        row_list = list(row)
            # Insertar los datos en la tabla
        data.append(row_list)
    for row in data[1:]:
        # Obtener el valor en la columna "MONTO" (la tercera columna, índice 2)
        monto = float(row[2])
        # Sumar el monto al monto total
        monto_total += monto
    
    # Crear la tabla y establecer el estilo
    table = Table(data)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), '#2579db'),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    table.setStyle(style)
    story.append(table)

    story.append(Spacer(1, 12))  # Espacio entre la tabla y el texto "total en letras"

    subtotal = monto_total
    
    total = subtotal + (subtotal * 0.15)

    story.append(Spacer(1, 12))  # Espacio entre el texto "subtotal" y el pie de página

    sub = "Subtotal: " + str(subtotal)
    tot = "total: " + str(total)
    # Estilo del párrafo
    style = getSampleStyleSheet()['Normal']
    style.alignment = 2  # 0=Izquierda, 1=Centro, 2=Derecha
    # Crear el objeto Paragraph con el estilo y el texto
    centered_paragraph1 = Paragraph(sub, style)
    centered_paragraph2 = Paragraph(tot, style)
    story.append(centered_paragraph1)
    story.append(centered_paragraph2)

    story.append(Spacer(1, 140))
    # pie de  # Espacio entre la tabla y el texto"
    mensaje = "De acuerdo con nuestras políticas, tiene un período de 24 horas para solicitar una reversión del pago si así lo desea. Después de este plazo, el pago será considerado permanente y no podrá ser revertido. Gracias por su comprensión y colaboración."
    style1 = getSampleStyleSheet()['Normal']
    style1.alignment = 1  # 0=Izquierda, 1=Centro, 2=Derecha
    text = Paragraph(mensaje, style1)
    # Luego, puedes agregar el párrafo al documento 'story' como lo estás haciendo
    story.append(text)
    story.append(Spacer(1, 120))
    # Texto que deseas alinear al centro
    pie_pagina = "La factura es beneficio de todos. Exíjala."
    # Estilo del párrafo
    style = getSampleStyleSheet()['Normal']
    style.alignment = 1  # 0=Izquierda, 1=Centro, 2=Derecha
    # Crear el objeto Paragraph con el estilo y el texto
    centered_paragraph = Paragraph(pie_pagina, style)
    # Luego, puedes agregar el párrafo al documento 'story' como lo estás haciendo
    story.append(centered_paragraph)

    # Generar el PDF
    doc.build(story)
    

def enviar_y_recibir_datos_rev():
    global data1
    try:
        # Obtener el dato ingresado por el usuario
        dato_ingresado = second_frame_entry.get()
        if not dato_ingresado:
            mb.showerror("Error", "Por favor, ingrese un código de cliente o referencia para realizar la búsqueda.")
            return
        # Enviar el dato al servidor
        client_socket.send(f"b{dato_ingresado}".encode())
        # Recibir la respuesta del servidor
        data1 = client_socket.recv(1024).decode()
        print('Recibido del servidor: ' + data1)
        if data1 == "[]":
            mb.showinfo("Sin Cuotas Pagadas", "El cliente no ha efectuado el pago de cuotas.")
            for record in tabla2.get_children():
                tabla2.delete(record)
            return
        if data1 == "Referencia inexistente":
            mb.showerror("Error", "Codigo de cliente o referencia inexistente.")
            for record in tabla2.get_children():
                tabla2.delete(record)
            return

        # Limpiar la tabla antes de insertar nuevos datos
        for record in tabla2.get_children():
            tabla2.delete(record)
        # Convertir las tuplas en listas y luego insertar en la tabla
        for row in eval(data1):
            # Convertir la tupla en una lista
            row_list = list(row)
            # Insertar los datos en la tabla
            tabla2.insert("", "end", values=row_list)
        return data1
        # Cerrar la conexión con el servidor
    except Exception as e:
        print("Se produjo un error:", str(e))

def on_row_select_rev(event):
    # Verificar si alguna fila ha sido seleccionada
    selected_items = tabla2.selection()
    if not selected_items:
        mb.showerror("Error", "Por favor, seleccione una fila antes de continuar.")
        return
    # Obtener la fila seleccionada
    selected_item = tabla2.selection()[0]
    # Obtener los valores de ID_CLIENTE y CUOTA de la fila seleccionada
    fecha_actual2 = datetime.datetime.now().strftime("%Y-%m-%d")
    id_cliente = tabla2.item(selected_item, "values")[0]
    cuota = tabla2.item(selected_item, "values")[1]
    fechapagado = tabla2.item(selected_item, "values")[3]
    referencia = tabla2.item(selected_item, "values")[4]
    if fechapagado != fecha_actual2:
        mb.showerror("Error", "El lapso de 24h para realizar la reversion ha caducado.")
        return
    print("ID_CLIENTE:", id_cliente)
    print("CUOTA:", cuota)
    print("fecha pagado:", fechapagado)
    print("Referencia:", referencia)

    client_socket.send(f"r{referencia}".encode())
    data = client_socket.recv(1024).decode()
    print(data)
    # Comparar la respuesta del servidor y mostrar la ventana emergente correspondiente
    if data == "Reversion realizada correctamente.":
        mb.showinfo("Reversion Realizada", "La Reversion del pago se realizó correctamente.")
        second_frame_entry.delete(0, "end")
        client_socket.send(f"b{id_cliente}".encode())
        data1 = client_socket.recv(1024).decode()
        # Limpiar la tabla antes de insertar nuevos datos
        for record in tabla2.get_children():
            tabla2.delete(record)
        try:
            for row in eval(data1):
                # Convertir la tupla en una lista
                row_list = list(row)
                # Insertar los datos en la tabla
                tabla2.insert("", "end", values=row_list)
        except Exception as e:
            print("desde el servidor:", e)
            mb.showinfo("Sin cuotas por revertir", "No se encontraron mas cuotas pagadas.")

def revertir():
    on_row_select_rev(None)

def valor(event):
    # Verificar si alguna fila ha sido seleccionada
    selected_items = tabla2.selection()
    if not selected_items:
        mb.showerror("Error", "Por favor, seleccione una fila antes de continuar.")
        return
    # Obtener la fila seleccionada
    selected_item = tabla2.selection()[0]
    # Obtener el valor de ID_CLIENTE de la fila seleccionada
    referencia = tabla2.item(selected_item, "values")[4]
    # Colocar el valor de id_cliente en la entrada
    second_frame_entry.delete(0, "end")
    second_frame_entry.insert(0, referencia)

# Obtener la fecha y hora actual

fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d")

# Obtiene el directorio del script actual
script_dir = os.path.dirname(os.path.realpath(__file__))

# Crear una ventana
app = customtkinter.CTk()

app.title("Examen_IP.py")
app.geometry("850x550")

# Obtener el ancho y alto de la pantalla
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()

# Calcular las coordenadas X e Y para centrar la ventana en la pantalla
x = (screen_width - 850) // 2  # Ajusta 850 al ancho deseado de la ventana
y = (screen_height - 550) // 2  # Ajusta 550 al alto deseado de la ventana

# Establecer la geometría de la ventana para centrarla
app.geometry(f"850x550+{x}+{y}")

# crear dos fuentes personalizadas
fuente1 = customtkinter.CTkFont(size=20, weight="bold")
fuente2 = customtkinter.CTkFont(size=18, weight="bold")

# set grid layout 1x2
app.grid_rowconfigure(0, weight=1)
app.grid_columnconfigure(1, weight=1)

# cargar imagenes con modo claro y oscuro imagen
image_path = os.path.join(script_dir, "test_images")
logo_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "CustomTkinter_logo_single.png")), size=(26, 26))
large_test_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "large_test_image2.png")), size=(500, 150))
bg_gradient = customtkinter.CTkImage(Image.open(os.path.join(image_path, "bg_gradient.jpg")), size=(550, 450))

buscar_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "buscar_negro.png")),
                                             dark_image=Image.open(os.path.join(image_path, "buscar_blanco.png")), size=(20, 20))

pagar_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "pagar_negro.png")),
                                             dark_image=Image.open(os.path.join(image_path, "pagar_blanco.png")), size=(20, 20))

reversion_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "reversion_negro.png")),
                                             dark_image=Image.open(os.path.join(image_path, "reversion_blanco.png")), size=(20, 20))
home_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "home_dark.png")),
                                             dark_image=Image.open(os.path.join(image_path, "home_light.png")), size=(20, 20))
chat_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "reversion_negro.png")),
                                             dark_image=Image.open(os.path.join(image_path, "reversion_blanco.png")), size=(20, 20))
add_user_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "add_user_dark.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "add_user_light.png")), size=(20, 20))

salir_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "salir_negro.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "salir_blanco.png")), size=(20, 20))

# crear marco de frame
navigation_frame = customtkinter.CTkFrame(app, corner_radius=0)
navigation_frame.grid(row=0, column=0, sticky="nsew")
navigation_frame.grid_rowconfigure(4, weight=1)

navigation_frame_label = customtkinter.CTkLabel(navigation_frame, text="  " + fecha_actual, image=logo_image,
                                                         compound="left", font=customtkinter.CTkFont(size=15, weight="bold"))
navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

home_button = customtkinter.CTkButton(navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Inicio",
                                               fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                               image=home_image, anchor="w", command=home_button_event)
home_button.grid(row=1, column=0, sticky="ew")

frame_2_button = customtkinter.CTkButton(navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Reversion",
                                                  fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                  image=chat_image, anchor="w", command=frame_2_button_event)
frame_2_button.grid(row=2, column=0, sticky="ew")

frame_3_button = customtkinter.CTkButton(navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Desarrolladores",
                                                  fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                  image=add_user_image, anchor="w", command=frame_3_button_event)
frame_3_button.grid(row=3, column=0, sticky="ew")

frame_4_button = customtkinter.CTkButton(navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Salir",
                                                  fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("red", "red"),
                                                  image=salir_image, anchor="w", command=app.destroy)
frame_4_button.grid(row=5, column=0, sticky="ew")

appearance_mode_menu = customtkinter.CTkOptionMenu(navigation_frame, values=["Dark", "Light"],
                                                         command=change_appearance_mode_event)
appearance_mode_menu.grid(row=6, column=0, padx=20, pady=20, sticky="s")


# crear frame de inicio
home_frame = customtkinter.CTkFrame(app, corner_radius=0, fg_color="transparent")
home_frame.grid_columnconfigure(0, weight=1)
home_frame.grid_columnconfigure(1, weight=1)
# home_frame.grid_columnconfigure(2, weight=1)
# home_frame.grid_columnconfigure(3, weight=1)

home_frame_large_image_label = customtkinter.CTkLabel(home_frame, text_color="white", font=fuente1, text="Pago de Cuotas", image=large_test_image)
home_frame_large_image_label.grid(row=0, column=0, padx=20, pady=10, columnspan=4, sticky="ew")

home_frame_entry = customtkinter.CTkEntry(home_frame, placeholder_text="Codigo Cliente (Ejemplo: 1001)", justify="center")
home_frame_entry.grid(row=1, column=0, padx=(20, 0), pady=(10, 10), sticky="nsew", columnspan=2)

home_frame_button_2 = customtkinter.CTkButton(home_frame, text="Buscar", image=buscar_image, compound="right", command=enviar_y_recibir_datos)
home_frame_button_2.grid(row=1, column=2, padx=20, pady=10, sticky="ew")

home_frame_button_3 = customtkinter.CTkButton(home_frame, text="Pagar", image=pagar_image, compound="right", command=pagar)
home_frame_button_3.grid(row=1, column=3, padx=(0 , 20), pady=10, sticky="ew")

# lista de columnas de la tabla
table_columns = ('ID_CLIENTE', 'CUOTA', 'MONTO', 'PAGO_FECHA_REALIZACION')

# crear frame para la tabla
table_frame = customtkinter.CTkFrame(home_frame)
table_frame.grid(row=2, column=0, padx=20, pady=10, columnspan=4, sticky="nsew")

# configurar la cuadrícula del frame de la tabla
table_frame.grid_columnconfigure(0, weight=1)  # configura la columna 0 con peso 1
table_frame.grid_rowconfigure(0, weight=1)     # configura la fila 0 con peso 1

# crear la tabla y anclarla al marco
tabla = ttk.Treeview(master=table_frame, columns=table_columns, height=10, selectmode='extended', show='headings')
tabla.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

# configurar columnas de la tabla
tabla.column("#1", anchor="c", minwidth=50, width=100)
tabla.column("#2", anchor="w", minwidth=30, width=50)
tabla.column("#3", anchor="c", minwidth=30, width=50)
tabla.column("#4", anchor="c", minwidth=80, width=100)

# encabezados de la tabla
tabla.heading('ID_CLIENTE', text='ID Cliente')
tabla.heading('CUOTA', text='Cuota')
tabla.heading('MONTO', text='Monto')
tabla.heading('PAGO_FECHA_REALIZACION', text='Pago Fecha Realizacion')

# filas ejemplos a la tabla
# tabla.insert("", "end", values=("1001", "1", "200", "2023-10-27"))
# tabla.insert("", "end", values=("2001", "2", "300", "2023-10-27"))

# crear segundo frame
second_frame = customtkinter.CTkFrame(app, corner_radius=0, fg_color="transparent")
second_frame.grid_columnconfigure(0, weight=1)
second_frame.grid_columnconfigure(1, weight=1)

home_frame_large_image_label = customtkinter.CTkLabel(second_frame, text_color="white", font=fuente1, text="Reversion", image=large_test_image)
home_frame_large_image_label.grid(row=0, column=0, padx=20, pady=10, columnspan=4, sticky="ew")

second_frame_entry = customtkinter.CTkEntry(second_frame, placeholder_text="Codigo Cliente o Referencia (1001 o 3ZR3-1001)", justify="center")
second_frame_entry.grid(row=1, column=0, padx=(20, 0), pady=(10, 10), sticky="nsew", columnspan=2)

second_frame_button_2 = customtkinter.CTkButton(second_frame, text="Buscar", image=buscar_image, compound="right", command=enviar_y_recibir_datos_rev)
second_frame_button_2.grid(row=1, column=2, padx=20, pady=10, sticky="ew")

second_frame_button_3 = customtkinter.CTkButton(second_frame, text="Reversion", image=reversion_image, compound="right", command=revertir)
second_frame_button_3.grid(row=1, column=3, padx=(0 , 20), pady=10, sticky="ew")

# lista de columnas de la tabla
table_columns = ('ID_CLIENTE', 'CUOTA', 'MONTO', 'PAGO_FECHA_REALIZACION', 'REFERENCIA')

# crear frame para la tabla
table_second_frame = customtkinter.CTkFrame(second_frame)
table_second_frame.grid(row=2, column=0, padx=20, pady=10, columnspan=4, sticky="nsew")

# configurar la cuadricula del frame de la tabla
table_second_frame.grid_columnconfigure(0, weight=1)  # configura la columna 0 con peso 1
table_second_frame.grid_rowconfigure(0, weight=1)     # configura la fila 0 con peso 1

# crear la tabla y anclarla al marco
tabla2 = ttk.Treeview(master=table_second_frame, columns=table_columns, height=10, selectmode='browse', show='headings')
tabla2.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

# configurar columnas de la tabla
tabla2.column("#1", anchor="c", minwidth=50, width=100)
tabla2.column("#2", anchor="w", minwidth=30, width=50)
tabla2.column("#3", anchor="c", minwidth=30, width=50)
tabla2.column("#4", anchor="c", minwidth=80, width=100)
tabla2.column("#5", anchor="c", minwidth=60, width=70)

# encabezados de la tabla
tabla2.heading('ID_CLIENTE', text='ID Cliente')
tabla2.heading('CUOTA', text='Cuota')
tabla2.heading('MONTO', text='Monto')
tabla2.heading('PAGO_FECHA_REALIZACION', text='Pago Fecha Realizacion')
tabla2.heading('REFERENCIA', text='Referencia')
tabla2.bind("<ButtonRelease-1>", valor)

# filas ejemplos a la tabla
# tabla2.insert("", "end", values=("1001", "1", "200", "2023-10-27", "4MR3-1001"))
# tabla2.insert("", "end", values=("2001", "2", "300", "2023-10-27", "4MR3-1001"))

# crear tercer frame
third_frame = customtkinter.CTkFrame(app, corner_radius=0, fg_color="transparent")
third_frame.grid_rowconfigure(0, weight=1)
third_frame.grid_columnconfigure(0, weight=1)

# Crear una cadena de texto con la descripción y los nombres
descripcion = "Grupo6"
nombres = [
    "Katherin Nicole Amador Maradiaga\n",
    "Mirian Fatima Ordoñez Amador\n",
    "Sharon Vanessa Espinoza Calderón\n",
    "Angela Nohemi Soler Aguilar\n",
    "Christian Isaac Calona Cruz\n",
    "Oscar Joel Gómez Castillo\n",
    "Gleen Alexis Pineda Moreno"
]
texto_resultado = f"{descripcion}\n\n\n"
texto_resultado += "\n".join(nombres)

desarrolladores_frame_large_image_label = customtkinter.CTkLabel(third_frame, text_color="white", font=fuente1, text=texto_resultado, image=bg_gradient)
desarrolladores_frame_large_image_label.grid(row=0, column=0, padx=20, pady=30, sticky="nsew")

# seleccionar el frame por default
select_frame_by_name("home")

app.mainloop()
