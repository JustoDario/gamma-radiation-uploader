import argparse
import time
import platform
import requests
import json
from datetime import datetime
import uuid

from radiacode import RadiaCode
from radiacode.transports.usb import DeviceNotFound as DeviceNotFoundUSB
from radiacode.transports.bluetooth import DeviceNotFound as DeviceNotFoundBT
from radiacode.types import RareData, RealTimeData, DoseRateDB, RawData, Event

def getDoseRate(data):
    if isinstance(data, (RealTimeData, DoseRateDB, RawData)):
        return data.dose_rate
    elif isinstance(data, RareData):
        return data.dose
    return None

def getCPS(data):
    """Obtiene las cuentas por segundo (CPS)"""
    if isinstance(data, (RealTimeData, DoseRateDB)):
        return data.count_rate
    return None

def getDoseRateError(data):
    """Obtiene el error de la tasa de dosis en %"""
    if isinstance(data, (RealTimeData, DoseRateDB)):
        return data.dose_rate_err
    return None

def getMeasurementTime(data):
    """Obtiene la hora de la medición"""
    if isinstance(data, (RealTimeData, DoseRateDB, RawData, RareData)):
        return data.dt.strftime('%H:%M')
    return None

def getTemperature(data):
    """Obtiene la temperatura del dispositivo"""
    if isinstance(data, RareData):
        return data.temperature
    return None

def send_to_openred(measurement_data, device_id, user_id, latitude, longitude):
    """Envía los datos a la API de OpenRed"""
    api_url = "https://openred.ibercivis.es/api/measurements/"
    print(f"Current location: {latitude}, {longitude}")
    payload = {
        "device": device_id,
        "user": user_id,
        "latitude": latitude,
        "longitude": longitude,
        "values": {
            "dose_rate": measurement_data.get("dose_rate"),
            "cps": measurement_data.get("cps"),
            "error": measurement_data.get("error"),
            "temperature": measurement_data.get("temperature")
        },
        "dateTime": measurement_data.get("time"),
        "unit": "uSv/h"
    }
    
    headers = {
        "Content-Type": "application/json",
        # Aquí deberías agregar tu token de autenticación
        "Authorization": "Bearer YOUR_TOKEN"
    }
    
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error enviando datos a OpenRed: {e}")
        return False

def obtener_ubicacion():
    """Obtiene la ubicación usando ip-api.com"""
    url = "http://ip-api.com/json"
    try:
        respuesta = requests.get(url, timeout=10)
        if respuesta.status_code == 200:
            datos = respuesta.json()
            if datos.get("status") == "success":
                return datos.get("lat"), datos.get("lon")
        return None
    except Exception as e:
        print(f"Error obteniendo ubicación: {e}")
        return None

def main():
    parser = argparse.ArgumentParser()

    if platform.system() != 'Darwin':
        parser.add_argument(
            '--bluetooth-mac', type=str, required=False, help='bluetooth MAC address of radiascan device (e.g. 00:11:22:33:44:55)'
        )

    parser.add_argument(
        '--serial',
        type=str,
        required=False,
        help='serial number of radiascan device (e.g. "RC-10x-xxxxxx"). Useful in case of multiple devices.',
    )

    args = parser.parse_args()

    if hasattr(args, 'bluetooth_mac') and args.bluetooth_mac:
        print(f'Connecting to Radiacode via Bluetooth (MAC address: {args.bluetooth_mac})')

        try:
            rc = RadiaCode(bluetooth_mac=args.bluetooth_mac)
        except DeviceNotFoundBT as e:
            print(e)
            return
        except ValueError as e:
            print(e)
            return
    else:
        print('Connecting to Radiacode via USB' + (f' (serial number: {args.serial})' if args.serial else ''))

        try:
            rc = RadiaCode(serial_number=args.serial)
        except DeviceNotFoundUSB:
            print('Device not found, check your USB connection')
            return

    serial = rc.serial_number()
    print(f'### Serial number: {serial}')
    print('--------')

    fw_version = rc.fw_version()
    print(f'### Firmware: {fw_version}')
    print('--------')

    spectrum = rc.spectrum()
    print(f'### Spectrum: {spectrum}')
    print('--------')

    # Configuración para OpenRed
    DEVICE_ID = 1  # Reemplaza con tu ID de dispositivo
    USER_ID = 1    # Reemplaza con tu ID de usuario
    
    # Obtener ubicación
    ubicacion = obtener_ubicacion()
    if ubicacion:
        LATITUDE, LONGITUDE = ubicacion
    else:
        LATITUDE, LONGITUDE = 40.0, -3.0  # Valores por defecto
    
    print(f'### Ubicación actual: {LATITUDE}, {LONGITUDE}')

    print('### DataBuf:')
    while True:
        for v in rc.data_buf():
            measurement_data = {
                "time": datetime.now().isoformat(),
                "dose_rate": getDoseRate(v),
                "cps": getCPS(v),
                "error": getDoseRateError(v),
                "temperature": getTemperature(v)
            }
            
            # Imprimir datos localmente
            tiempo = getMeasurementTime(v)
            if tiempo:
                print(f"Hora: {tiempo}")
            if measurement_data["dose_rate"] is not None:
                print(f"Tasa de dosis: {measurement_data['dose_rate']:.6f} uSv/h")
            if measurement_data["cps"] is not None:
                print(f"CPS: {measurement_data['cps']:.2f}")
            if measurement_data["error"] is not None:
                print(f"Error: {measurement_data['error']}%")
            if measurement_data["temperature"] is not None:
                print(f"Temperatura: {measurement_data['temperature']}°C")
            print("--------")
            
            # Enviar datos a OpenRed
            if send_to_openred(measurement_data, DEVICE_ID, USER_ID, LATITUDE, LONGITUDE):
                print("Datos enviados exitosamente a OpenRed")
            else:
                print("Error al enviar datos a OpenRed")
        
        time.sleep(5)


if __name__ == '__main__':
    main()
