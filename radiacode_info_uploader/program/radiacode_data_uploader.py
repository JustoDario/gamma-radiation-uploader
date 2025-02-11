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
    """Sends data to OpenRed API"""
    api_url = "https://openred.ibercivis.es/api/measurements/"
    
    # Convert dose rate to µSv/h 
    radiation_value = measurement_data.get("dose_rate", 0) * 1000000 if measurement_data.get("dose_rate") is not None else 0
    
    # Use current date in ISO format
    current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    
    payload = {
        "device": device_id,
        "user": user_id,
        "latitude": latitude,
        "longitude": longitude,
        "altitude": 0,
        "values": {
            "radiation": radiation_value
        },
        "dateTime": current_time,
        "accuracy": 0,
        "unit": "string",
        "notes": "string",
        "weather": {}
    }
    
    print("\n=== Sending data to OpenRed ===")
    print(f"URL: {api_url}")
    print("Headers:")
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "X-CSRFTOKEN": "X5OIJURr29SzYxWZgEcPnBhINbkzvMB6EI7Y7IiaGJgrGd6pyYiz07Vq8BvboZyP"
    }
    print(json.dumps(headers, indent=2))
    print("Payload:")
    print(json.dumps(payload, indent=2))
    
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        print("\n=== OpenRed Response ===")
        print(f"Status Code: {response.status_code}")
        print("Response Headers:")
        print(json.dumps(dict(response.headers), indent=2))
        print("Response Body:")
        try:
            print(json.dumps(response.json(), indent=2))
        except:
            print(response.text)
            
        if response.status_code == 201:
            data = response.json()
            print(f"\n✓ Measurement saved with ID: {data.get('measurement_id')}")
            return True
        else:
            print(f"\n✗ Error: {response.status_code} - {response.reason}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\n✗ Connection error: {str(e)}")
        return False
    finally:
        print("=" * 40)

def obtener_ubicacion():
    """Gets location using ip-api.com"""
    url = "http://ip-api.com/json"
    try:
        respuesta = requests.get(url, timeout=10)
        if respuesta.status_code == 200:
            datos = respuesta.json()
            if datos.get("status") == "success":
                return datos.get("lat"), datos.get("lon")
        return None
    except Exception as e:
        print(f"Error getting location: {e}")
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
        print(f'Connecting to RadiaCode via Bluetooth (MAC address: {args.bluetooth_mac})')

        try:
            rc = RadiaCode(bluetooth_mac=args.bluetooth_mac)
        except (DeviceNotFoundBT, ValueError) as e:
            print('No RadiaCode found via Bluetooth. Is it turned on and paired?')
            return
    else:
        print('Connecting to RadiaCode via USB' + (f' (serial number: {args.serial})' if args.serial else ''))

        try:
            rc = RadiaCode(serial_number=args.serial)
        except DeviceNotFoundUSB:
            print('No RadiaCode found via USB. Is it turned on and connected?')
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

    # OpenRed configuration
    DEVICE_ID = 1  # Replace with your device ID
    USER_ID = 1    # Replace with your user ID
    
    # Get location
    ubicacion = obtener_ubicacion()
    if ubicacion:
        LATITUDE, LONGITUDE = ubicacion
    else:
        LATITUDE, LONGITUDE = 40.0, -3.0  # Default values
    
    print(f'### Current location: {LATITUDE}, {LONGITUDE}')

    print('### DataBuf:')
    while True:
        for v in rc.data_buf():
            measurement_data = {
                "radiation": getDoseRate(v),
                "time": datetime.now().isoformat(),
                "dose_rate": getDoseRate(v),
                "cps": getCPS(v),
                "error": getDoseRateError(v),
                "temperature": getTemperature(v)
            }
            
            # Print data locally
            tiempo = getMeasurementTime(v)
            if tiempo:
                print(f"Time: {tiempo}")
            if measurement_data["dose_rate"] is not None:
                print(f"Dose rate: {measurement_data['dose_rate']:.6f} uSv/h")
            if measurement_data["cps"] is not None:
                print(f"CPS: {measurement_data['cps']:.2f}")
            if measurement_data["error"] is not None:
                print(f"Error: {measurement_data['error']}%")
            if measurement_data["temperature"] is not None:
                print(f"Temperature: {measurement_data['temperature']}°C")
            print("--------")
            
            # Send data to OpenRed
            if send_to_openred(measurement_data, DEVICE_ID, USER_ID, LATITUDE, LONGITUDE):
                print("Data successfully sent to OpenRed")
            else:
                print("Error sending data to OpenRed")
        
        time.sleep(5)


if __name__ == '__main__':
    main()
