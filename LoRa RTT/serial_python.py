import serial
import time
import random
import string
import matplotlib.pyplot as plt

# Configuración del puerto serial
try:
    ser = serial.Serial('COM3', 115200, timeout=1)  # Cambiar 'COMX' por el puerto de LoRa_Sender
    time.sleep(2)  # Esperar a que el puerto serial se inicialice
except serial.SerialException as e:
    print(f"Error abriendo el puerto serial: {e}")
    exit()

def generar_paquete_aleatorio(tamano):
    caracteres = string.ascii_letters + string.digits + string.punctuation
    caracteres_permitidos = caracteres.replace('\r', '').replace('\n', '').replace(';', '')
    paquete = ''.join(random.choice(caracteres_permitidos) for _ in range(tamano))
    return paquete

def serial_receiver():
    regreso = ""
    rssi = ""
    snr = ""
    freqError = ""
    start_time = time.time()  # Marca el tiempo de inicio
    while True:
        if ser.in_waiting > 0:
            try:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if not regreso:
                    regreso = line
                elif not rssi:
                    rssi = line
                elif not snr:
                    snr = line
                elif not freqError:
                    freqError = line
                    break
            except UnicodeDecodeError:
                continue
        # Verifica si han pasado más de 12 segundos para ""
        if time.time() - start_time > 30:
            regreso = ""
            rssi = "-"
            snr = "-"
            freqError = "-"
            break
    rtt = round(time.time() - start_time, 3) if regreso != "" else "-"
    return regreso, rssi, snr, freqError, rtt

def grafico_packet_loss(lista_loss, lista_rssi, lista_rtt, lista_bytes_loss, lista_snr, lista_freqError, tamano_paquete):
    packet_loss_percentage = 100 * sum(1 for l in lista_loss if l != 0) / len(lista_loss) if lista_loss else 0

    # Calcular promedio de RSSI
    valores_enteros_rssi = []
    for x in lista_rssi:
        try:
            valores_enteros_rssi.append(int(x))
        except (ValueError, TypeError):
            continue
    avg_rssi = sum(valores_enteros_rssi) / len(valores_enteros_rssi) if valores_enteros_rssi else 0

    # Calcular promedio de SNR
    valores_enteros_snr = []
    for x in lista_snr:
        try:
            valores_enteros_snr.append(float(x))
        except (ValueError, TypeError):
            continue
    avg_snr = sum(valores_enteros_snr) / len(valores_enteros_snr) if valores_enteros_snr else 0

    # Calcular promedio de Frequency Error
    valores_enteros_freqError = []
    for x in lista_freqError:
        try:
            valores_enteros_freqError.append(float(x))
        except (ValueError, TypeError):
            continue
    avg_freqError = sum(valores_enteros_freqError) / len(valores_enteros_freqError) if valores_enteros_freqError else 0

    # Calcular promedio de RTT
    valores_enteros_rtt = [float(x) for x in lista_rtt if isinstance(x, (int, float))]
    avg_rtt = sum(valores_enteros_rtt) / len(valores_enteros_rtt) if valores_enteros_rtt else 0

    bytes_loss_rate = sum(lista_bytes_loss) / len(lista_bytes_loss) if lista_bytes_loss else 0

    plt.figure(figsize=(10, 5))
    plt.bar(range(50), lista_loss)
    plt.xlabel('Número de paquetes')
    plt.ylabel('Número de bits perdidos')
    plt.title('Pérdida de bits en los últimos 50 paquetes')
    plt.text(0, max(lista_loss), f'{packet_loss_percentage:.1f}% Packet Loss\n{bytes_loss_rate:.0f}% Bytes Loss Rate\nAverage RSSI: {avg_rssi:.2f} dBm\nAverage SNR: {avg_snr:.2f} dB\nAverage Freq Error: {avg_freqError:.2f} Hz\nAverage RTT: {avg_rtt:.2f} s', fontsize=12, verticalalignment='top', horizontalalignment='left')
    plt.savefig(f"{tamano_paquete}.jpg")  # Guardar el gráfico como imagen .jpg
    plt.show()

def bloc_de_notas(tamano_paquete, lista_datos, lista_regreso, lista_loss, lista_bytes_loss, lista_rssi, lista_rtt):
    nombre_archivo = f"{tamano_paquete}.txt"
    with open(nombre_archivo, 'w', encoding='utf-8') as archivo:  # Agrega encoding='utf-8' aquí
        archivo.write("lista_datos:\n")
        archivo.write('\n'.join(lista_datos) + '\n')
        archivo.write("lista_regreso:\n")
        archivo.write('\n'.join(lista_regreso) + '\n')
        archivo.write("lista_loss:\n")
        archivo.write('\n'.join(map(str, lista_loss)) + '\n')
        archivo.write("lista_bytes_loss:\n")
        archivo.write('\n'.join(map(str, lista_bytes_loss)) + '\n')
        archivo.write("lista_rssi:\n")
        archivo.write('\n'.join(lista_rssi) + '\n')
        archivo.write("lista_rtt:\n")
        archivo.write('\n'.join(map(str, lista_rtt)) + '\n')

def main(lista_datos, lista_regreso, lista_loss, lista_rssi, lista_rtt, lista_bytes_loss, lista_snr, lista_freqError):
    tamano_paquete = input("Elige tu tamaño de paquete (Bajo, Medio, Alto): ").capitalize()
    if tamano_paquete == "Bajo":
        tamano = random.randint(1, 50)
    elif tamano_paquete == "Medio":
        tamano = random.randint(51, 150)
    elif tamano_paquete == "Alto":
        tamano = random.randint(151, 255)
    else:
        print("Tamaño de paquete no válido. Por favor, elige entre Bajo, Medio o Alto.")
        return

    try:
        while True:
            if not ser.is_open:
                print("El puerto serial está cerrado. Intentando reabrir...")
                ser.open()
                time.sleep(1)

            datos = generar_paquete_aleatorio(tamano)
            if len(lista_datos) >= 50:
                lista_datos.pop(0)
            lista_datos.append(datos)  # Almacena los datos enviados

            tamano_enviado = len(datos)
            ser.write(datos.encode('utf-8') + b'\n')
            print(f"Datos enviados ({tamano_enviado} bytes):\n{datos}")
            regreso, rssi, snr, freqError, rtt = serial_receiver()
            if len(lista_regreso) >= 50:
                lista_regreso.pop(0)
            lista_regreso.append(regreso)  # Almacena los datos recibidos
            if len(lista_rssi) >= 50:
                lista_rssi.pop(0)
            lista_rssi.append(rssi)  # Almacena los valores RSSI recibidos
            if len(lista_snr) >= 50:
                lista_snr.pop(0)
            lista_snr.append(snr)  # Almacena los valores SNR recibidos
            if len(lista_freqError) >= 50:
                lista_freqError.pop(0)
            lista_freqError.append(freqError)  # Almacena los valores de error de frecuencia
            if len(lista_rtt) >= 50:
                lista_rtt.pop(0)
            lista_rtt.append(rtt)  # Almacena los valores RTT calculados

            tamano_recibido = len(regreso)
            print(f"Datos recibidos ({tamano_recibido} bytes), RSSI {rssi}, SNR {snr}, Freq Error {freqError}, RTT {rtt} s:\n{regreso}")

            if tamano_recibido == 0:
                loss = tamano_enviado
            elif tamano_recibido > 0:
                loss = sum(1 for d, r in zip(datos, regreso) if d != r)
            if len(lista_loss) >= 50:
                lista_loss.pop(0)
            lista_loss.append(loss)

            print(f"Pérdida de paquetes: {loss}")

            # Calcular lista_bytes_loss si hay pérdida de paquetes
            if loss != 0 and tamano_recibido != 0:
                bytes_loss = (loss / tamano_enviado) * 100
                lista_bytes_loss.append(bytes_loss)

            if tamano_recibido == 0:
                lista_bytes_loss.append(100)

            if len(lista_bytes_loss) >= 50:
                lista_bytes_loss.pop(0)

            # Actualizar el tamaño del paquete de manera aleatoria dentro del mismo rango
            if tamano_paquete == "Bajo":
                tamano = random.randint(1, 50)
            elif tamano_paquete == "Medio":
                tamano = random.randint(51, 150)
            elif tamano_paquete == "Alto":
                tamano = random.randint(151, 255)

            # Graficar cada vez que se alcance 50 paquetes
            if len(lista_datos) == 50:
                grafico_packet_loss(lista_loss, lista_rssi, lista_rtt, lista_bytes_loss, lista_snr, lista_freqError, tamano_paquete)
                
                # Guardar datos en bloc de notas
                bloc_de_notas(tamano_paquete, lista_datos, lista_regreso, lista_loss, lista_bytes_loss, lista_rssi, lista_rtt)
                
                # Limpiar listas
                lista_datos.clear()
                lista_regreso.clear()
                lista_loss.clear()
                lista_rssi.clear()
                lista_rtt.clear()
                lista_bytes_loss.clear()
                lista_snr.clear()
                lista_freqError.clear()
                
                main(lista_datos, lista_regreso, lista_loss, lista_rssi, lista_rtt, lista_bytes_loss, lista_snr, lista_freqError)  # Llamar a la función main nuevamente para reiniciar el proceso

    except (KeyboardInterrupt, serial.SerialException) as e:
        print(f"Terminando el programa debido a: {e}")
    finally:
        ser.close()

if __name__ == "__main__":
    lista_datos = []
    lista_regreso = []
    lista_loss = []
    lista_rssi = []
    lista_rtt = []
    lista_bytes_loss = []
    lista_snr = []
    lista_freqError = []
    main(lista_datos, lista_regreso, lista_loss, lista_rssi, lista_rtt, lista_bytes_loss, lista_snr, lista_freqError)