import csv
from estructura import Cliente
import os
import re
from unidecode import unidecode
import sys
import pywhatkit
import datetime
import time

def enviar_wp(datos,localidad,num_msg):
    v_clientes = []
    with open(datos, 'r', encoding='utf-8') as file2:
        reader = csv.reader(file2)
        encabezado = next(reader)
        for row in reader:
            cliente = Cliente(row[0])
            cliente.categoria = row[1]
            cliente.subcategoria = row[2]
            cliente.tlf_fijo = row[3]
            cliente.tlf_movil = row[4]
            cliente.mail = row[5]
            cliente.web = row[6]
            cliente.localidad = row[7]
            if cliente.tlf_movil != -1 and (cliente.tlf_movil[0] == "6" or cliente.tlf_movil[0] == "7") and len(cliente.tlf_movil) == 9 and cliente.localidad == localidad and cliente.whatsapp_enviado == -1:
                v_clientes.append(cliente)
        espera = 60
        hora_actual = datetime.datetime.now()
        for i in range(num_msg):  # enviar 10 mensajes
            hora_envio = hora_actual + datetime.timedelta(minutes=i)  # programar el envío de cada mensaje
            hora_envio_str = hora_envio.strftime("%H:%M")  # convertir la hora de envío a una cadena de texto
            print(f"Enviando mensaje {i + 1} a las {hora_envio_str}...")
            numero = "+34" + v_clientes[i].tlf_movil
            mensaje = "açò és una prova"
            pywhatkit.sendwhatmsg(numero, mensaje, hora_envio.hour, hora_envio.minute, wait_time=10)
            v_clientes[i].whatsapp_enviado = "si"
            time.sleep(espera)



def limpiar_datos(datos):
    v_clientes = []
    categorias = {}
    ruta_script = os.path.dirname(os.path.abspath(sys.argv[0]))
    ruta_directorio_superior = os.path.dirname(ruta_script)
    ruta_archivo = os.path.join(ruta_directorio_superior, 'categorias.csv')
    with open(ruta_archivo, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        encabezado = next(reader)
        for row in reader:
            if row[0] not in categorias:
                categorias[row[0].lower()] = [row[1].lower()]
            elif row[1] not in categorias[row[0]]:
                categorias[row[0]].append(row[1].lower())

    with open(datos, 'r', encoding='utf-8') as file2:
        reader = csv.reader(file2)
        encabezado = next(reader)
        for row in reader:
            cliente = Cliente(row[0])
            cliente.categoria = row[2]
            cliente.subcategoria = row[3]
            cliente.tlf_fijo = row[5]
            cliente.tlf_movil = row[6]
            cliente.mail = row[7]
            cliente.web = row[10]
            cliente.localidad = row[17]
            v_clientes.append(cliente)

    nombre_archivo, extension = os.path.splitext(datos)
    nombre_archivo_v1 = f"{nombre_archivo[:-3]}_v2.csv"

    while True:
        try:
            with open(nombre_archivo_v1, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(
                    ['Nombre', 'Categoría', 'Subcategoría', 'Tlf Fijo', 'Tlf Móvil', 'Mail', 'Web', 'Localidad', 'Whatsapp eviado', "Mail enviado"])
                for cliente in v_clientes:
                    writer.writerow(
                        [cliente.nombre, cliente.categoria, cliente.subcategoria,
                         cliente.tlf_fijo, cliente.tlf_movil, cliente.mail,
                         cliente.web,cliente.localidad,cliente.whatsapp_enviado,cliente.mail_enviado])
            print("Actualizada v1")
            break
        except FileNotFoundError:
            print(f"Error: El archivo {nombre_archivo_v1} no se encuentra.")
        except PermissionError:
            print(f"Error: No se tienen permisos de escritura para el archivo {nombre_archivo_v1}.")
        except IsADirectoryError:
            print(f"Error: {nombre_archivo_v1} es un directorio, no un archivo.")
        except Exception as e:
            print(f"Error inesperado al crear v1: {e}")


def procesar_datos(datos):
    v_clientes = []
    categorias = {}
    ruta_script = os.path.dirname(os.path.abspath(sys.argv[0]))
    ruta_directorio_superior = os.path.dirname(ruta_script)
    ruta_archivo = os.path.join(ruta_directorio_superior, 'categorias.csv')
    with open(ruta_archivo, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        encabezado = next(reader)
        for row in reader:
            if row[0] not in categorias:
                categorias[row[0].lower()] = [row[1].lower()]
            elif row[1] not in categorias[row[0]]:
                categorias[row[0]].append(row[1].lower())
    with open(datos, 'r', encoding='utf-8') as archivo_original:
        reader = csv.reader(archivo_original)
        encabezado = next(reader)
        for row in reader:
            aux = []
            for e in row:
                e = e.replace("Teléfono", "@")  #@ es T
                e = e.replace("Telèfon","@")
                e = e.replace("Móvil","&")
                e = e.replace("Mòbil","&")
                e = e.replace("Whatsapp", "&")
                e = e.replace("whatsapp", "&")
                e = e.replace("Email", "$")
                e = e.replace("email", "$")
                e = e.replace("correo", "$")
                e = e.replace("Web", "#")
                aux.append(e)

            row = aux

            #Generamos un nuevo cliente

            cliente = Cliente(unidecode(row[2]))
            cliente.url = unidecode(row[3])

            aux = row[4:7]
            for e in aux:
                if len(e)>2:
                    if e[0] == "@" and e[1]=="9":
                        cliente.tlf_fijo = unidecode(e[1:])
                    elif e[0] == "&" or e[0] == "@":
                        cliente.tlf_movil = unidecode(e[1:])
                    elif e[0] == "$":
                        cliente.mail = unidecode(e[1:])
                    elif e[0] == "#":
                        e = e[5:]
                        if e[0] == "s":
                            e = e[4:]
                        else:
                            e = e[3:]
                        cliente.web = unidecode(e)


            cliente.categoria = unidecode(row[8]).lower()
            cliente.subcategoria = unidecode(row[9]).lower()
            cliente.localidad = unidecode(row[10])

            if cliente.categoria not in categorias:
                categorias[cliente.categoria] = [cliente.subcategoria]
            elif cliente.subcategoria not in categorias[cliente.categoria]:
                categorias[cliente.categoria].append(cliente.subcategoria)

            # Comprobamos la info de la web si tiene (ssl, wp, wp version)

            """if cliente.web != -1:
                hostname = cliente.web  # Assuming that cliente.web contains a valid hostname
                context = ssl.create_default_context()

                try:
                    with socket.create_connection((hostname, 443)) as sock:
                        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                            cliente.certificado = "si"
                except ssl.SSLError:
                    pass
                except socket.gaierror:
                    pass
                except socket.timeout:
                    pass
                except ConnectionRefusedError:
                    pass
                except Exception:
                    pass
                if cliente.certificado == "si":
                    cliente.web = hostname

                    url = hostname
                    if not re.match(r'^https?://', url):
                        url = 'http://' + url

                    try:
                        with urllib.request.urlopen(url) as response:
                            html = response.read().decode()
                            if re.search(r'wp-content', html, re.I) or re.search(r'wordpress', html, re.I):
                                match_version = re.search(r'(?i)wordpress\s+(\d+\.\d+\.\d+|\d+\.\d+|\d+)', html)
                                if match_version:
                                    version = match_version.group(1)
                                    cliente.wordpress = "si"
                                    cliente.version_wp = version
                                else:
                                    cliente.wordpress = "si"
                                    pass
                            else:
                                pass
                    except Exception:
                        pass
                print("---Web de cliente analizada---")"""
            if cliente.mail != -1:
                match = re.match(r'^\w+([-+.]\w+)*@(\w+)(\.(\w+))+$', cliente.mail)
                if match:
                    dominio = match.group(2)
                    if dominio == "gmail":
                        cliente.mail_generico = "si"
                        cliente.mail_dominio = "gmail"
                    elif dominio == "outlook" or dominio == "hotmail":
                        cliente.mail_generico = "si"
                        cliente.mail_dominio = "outlook/hotmail"
                    elif dominio == "yahoo":
                        cliente.mail_generico = "si"
                        cliente.mail_dominio = "yahoo"
                    else:
                        cliente.mail_generico = "no"
                        cliente.mail_dominio = dominio
                else:
                    pass
            v_clientes.append(cliente)
            print(f"-----------Cliente hecho: {cliente.nombre}")

    nombre_archivo, extension = os.path.splitext(datos)
    nombre_archivo_v1 = f"{nombre_archivo}_v1.csv"

    while True:
        try:
            with open(nombre_archivo_v1, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(
                    ['Nombre', 'URL', 'Categoría', 'Subcategoría', 'Dirección', 'Tlf Fijo', 'Tlf Móvil', 'Mail',
                     'Mail Genérico', 'Mail Dominio', 'Web', 'Certificado', 'WordPress', 'Versión WP',
                     'Cuerpo Mail Hecho', 'Puntuación', 'Cuerpo Mail', 'Localidad'])
                for cliente in v_clientes:
                    writer.writerow(
                        [cliente.nombre, cliente.url, cliente.categoria, cliente.subcategoria, cliente.direccion,
                         cliente.tlf_fijo, cliente.tlf_movil, cliente.mail, cliente.mail_generico,
                         cliente.mail_dominio, cliente.web, cliente.certificado, cliente.wordpress,
                         cliente.version_wp, cliente.cuerpo_mail_hecho, cliente.puntuación, cliente.cuerpo_mail,cliente.localidad])
            print("Actualizada v1")
            break
        except FileNotFoundError:
            print(f"Error: El archivo {nombre_archivo_v1} no se encuentra.")
        except PermissionError:
            print(f"Error: No se tienen permisos de escritura para el archivo {nombre_archivo_v1}.")
        except IsADirectoryError:
            print(f"Error: {nombre_archivo_v1} es un directorio, no un archivo.")
        except Exception as e:
            print(f"Error inesperado al crear v1: {e}")

    while True:
        try:
            with open(ruta_archivo, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Categoria', 'Subcategorias'])
                for categoria, subcategorias in categorias.items():
                    for subcategoria in subcategorias:
                        writer.writerow([categoria, subcategoria])
            print("Actualizada catergorias")
            break
        except FileNotFoundError:
            print(f"Error: El archivo {ruta_archivo} no se encuentra.")
        except PermissionError:
            print(f"Error: No se tienen permisos de escritura para el archivo {ruta_archivo}.")
        except IsADirectoryError:
            print(f"Error: {ruta_archivo} es un directorio, no un archivo.")
        except Exception as e:
            print(f"Error inesperado al crear categorias: {e}")
