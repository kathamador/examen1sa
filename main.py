# Server
import socket
import mysql.connector
import threading
from datetime import datetime
import random
import string

# Función principal para manejar las conexiones de los clientes
def handle_client(conn, address, cursor, db_connection):
    print("Conexión desde: " + str(address))
    while True:
        data = conn.recv(1024).decode()
        print(str(data))

        if not data:
            break
        print("Desde el usuario conectado: " + str(data))

        if data.startswith('c'):
            id_cliente = data[1:]
            # Verificar si el cliente existe en la base de datos
            query = f"SELECT ID_CLIENTE, CUOTA, MONTO, FECHA_PAGO FROM pago_clientes WHERE ID_CLIENTE = {id_cliente} AND (ESTADO ='C' OR ESTADO ='P')"
            cursor.execute(query)
            result = cursor.fetchall()
            formatted_data = [(row[0], row[1], row[2], row[3].strftime('%Y-%m-%d')) for row in result]
            validar= str(formatted_data)

            if result:
                # El cliente existe, realizar la consulta principal
                query = f"SELECT ID_CLIENTE, CUOTA, MONTO, FECHA_PAGO FROM pago_clientes WHERE ID_CLIENTE = {id_cliente} AND  ESTADO ='P'"
                cursor.execute(query)
                result = cursor.fetchall()
                formatted_data = [(row[0], row[1], row[2], row[3].strftime('%Y-%m-%d')) for row in result]
                conn.send(str(formatted_data).encode())
            else:
                # El cliente no existe, enviar un mensaje de cliente inexistente
                conn.send("Cliente inexistente".encode())

        elif data.startswith('A'):
            data = data[1:].split('|')
            queries = []
            for item in data:
                id_cliente, cuota = item.split(':')
                fecha_actual = datetime.now().strftime("%Y-%m-%d")
                # Genera una cadena aleatoria de 4 caracteres alfanuméricos
                referencia_aleatoria = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
                # Concatena la cadena aleatoria con el ID del cliente
                referencia_factura = referencia_aleatoria + '-' +str(id_cliente)
                print("estos valores estoy recibiendo: ",id_cliente,cuota,fecha_actual)
                query = f"UPDATE pago_clientes SET ESTADO ='C', PAGO_FECHA_REALIZACION = '{fecha_actual}', REFERENCIA = '{referencia_factura}' WHERE ID_CLIENTE = {id_cliente} AND CUOTA = {cuota}"
                queries.append(query)
                print(referencia_factura.encode())
            try:
                for query in queries:
                    cursor.execute(query)
                db_connection.commit()
                print("Actualización realizada correctamente.")
                conn.send("Actualización realizada correctamente.".encode())
            except Exception as e:
                print("Error durante la actualización:", e)
                conn.send("Error durante la actualización.".encode())

        elif data.startswith('b'):
            referencia = data[1:]
            # Verificar si la referencia existe en la base de datos
            query = "SELECT ID_CLIENTE, CUOTA, MONTO, PAGO_FECHA_REALIZACION, REFERENCIA FROM pago_clientes WHERE (REFERENCIA = '" + referencia + "' OR ID_CLIENTE = '" + referencia + "') AND ESTADO ='C'"
            cursor.execute(query)
            result = cursor.fetchall()
            formatted_data = [(row[0], row[1], row[2], row[3].strftime('%Y-%m-%d'), row[4]) for row in result]
            validar = str(formatted_data)

            if result:
                # Enviar datos
                conn.send(str(formatted_data).encode())
            else:
                # No hay datos, enviar un mensaje de referencia inexistente
                conn.send("Referencia inexistente".encode())
        elif data.startswith('r'):
            referencia = data[1:]
            # Verificar si la referencia existe en la base de datos
            try:
                query = "UPDATE pago_clientes SET estado = 'P', REFERENCIA = '', PAGO_FECHA_REALIZACION = '0000-00-00' WHERE REFERENCIA = '"+referencia+"' AND ESTADO ='C'"
                print(query)
                cursor.execute(query)
                db_connection.commit()

                if result:
                    # Enviar datos
                    conn.send("Reversion realizada correctamente.".encode())
            except Exception as e:
                print("Error durante la reversion:", e)
                conn.send("Error durante la reversion.".encode())
        else:
            conn.send(
                "Formato de entrada incorrecto. Por favor, ingrese 'C' seguido del ID del cliente o 'A' para actualizar.".encode())
    conn.close()


# Función principal del servidor
def server_program():
    try:
        host = socket.gethostname()
        port = 5000
        server_socket = socket.socket()
        server_socket.bind((host, port))
        server_socket.listen(5)

        db_connection = mysql.connector.connect(
            host="localhost",
            user="root",
            database="examen1p"
        )

        if db_connection.is_connected():
            print("Conexión a la base de datos exitosa.")

        cursor = db_connection.cursor()

        while True:
            conn, address = server_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, address, cursor, db_connection))
            client_thread.start()

    except KeyboardInterrupt:
        print("Servidor interrumpido por el usuario.")
    except Exception as e:
        print("Se produjo un error:", str(e))
    finally:
        cursor.close()
        db_connection.close()


if __name__ == '__main__':
    server_program()