import flet as ft
import sys
import subprocess
from pathlib import Path
import asyncio

def verify_radiacode_dependencies():
    """Verifica todas las dependencias necesarias para radiacode_data_uploader.py"""
    missing_deps = []
    
    # Verificar dependencias de Python
    python_deps = {
        'requests': 'requests',
        'radiacode': 'radiacode',
        'ctypes': '_ctypes',
        'usb.core': 'pyusb',
        'json': 'json',
        'argparse': 'argparse',
    }
    
    for module, package in python_deps.items():
        try:
            __import__(module)
        except ImportError:
            missing_deps.append(package)
    
    # Verificar dependencias del sistema
    system_deps = {
        'libusb-1.0-0-dev': '/usr/lib/x86_64-linux-gnu/libusb-1.0.so',
        'python3-dev': '/usr/include/python3.10/Python.h',
        'libffi-dev': '/usr/lib/x86_64-linux-gnu/libffi.so'
    }
    
    for package, path in system_deps.items():
        if not Path(path).exists():
            missing_deps.append(package)
    
    return missing_deps

class RadiaCodeMonitor:
    def __init__(self):
        self.rc = None
        self.is_monitoring = False
        
    async def start(self):
        try:
            from radiacode import RadiaCode
            from radiacode.transports.usb import DeviceNotFound
            try:
                self.rc = RadiaCode()
                serial = self.rc.serial_number()
                self.is_monitoring = True
                return True, serial
            except DeviceNotFound:
                return False, "No se encontró el dispositivo RadiaCode. ¿Está conectado?"
            except Exception as e:
                return False, f"Error al conectar: {str(e)}"
        except Exception as e:
            return False, f"Error al inicializar RadiaCode: {str(e)}"
    
    def stop(self):
        self.is_monitoring = False
        self.rc = None
    
    async def get_dose_rate(self):
        if not self.rc or not self.is_monitoring:
            return None
            
        try:
            for data in self.rc.data_buf():
                if hasattr(data, 'dose_rate'):
                    return data.dose_rate
            return None
        except Exception as e:
            print(f"Error leyendo dose rate: {e}")
            return None

async def main(page: ft.Page):
    page.title = "RadiaCode App"
    page.padding = 20
    
    # Crear instancia del monitor
    monitor = RadiaCodeMonitor()
    
    async def update_dose_rate():
        try:
            while monitor.is_monitoring:
                dose_rate = await monitor.get_dose_rate()
                if dose_rate is not None:
                    dose_rate_text.value = f"Dose Rate: {dose_rate:.6f} µSv/h"
                    await page.update_async()
                await asyncio.sleep(1)
        except Exception as e:
            print(f"Error en update_dose_rate: {e}")
    
    async def toggle_monitoring(e):
        if not monitor.is_monitoring:
            # Primero verificar dependencias
            missing = verify_radiacode_dependencies()
            if missing:
                status.value = f"❌ Faltan las siguientes dependencias:\n" + "\n".join(f"- {dep}" for dep in missing)
                status.color = "red"
                device_info.visible = False
                dose_rate_text.visible = False
                await page.update_async()
                return
                
            # Intentar conectar con el RadiaCode
            success, result = await monitor.start()
            if success:
                status.value = "✅ Conectado al dispositivo"
                status.color = "green"
                device_info.value = f"📟 RadiaCode detectado\nNúmero de Serie: {result}"
                device_info.color = "green"
                device_info.visible = True
                dose_rate_text.visible = True
                monitor_btn.text = "Detener Monitoreo"
                asyncio.create_task(update_dose_rate())
            else:
                status.value = f"❌ {result}"
                status.color = "red"
                device_info.visible = False
                dose_rate_text.visible = False
        else:
            monitor.stop()
            monitor_btn.text = "Iniciar Monitoreo"
            dose_rate_text.visible = False
            device_info.visible = False
            status.value = "Monitoreo detenido"
            
        await page.update_async()
    
    title = ft.Text("RadiaCode App", size=30, weight=ft.FontWeight.BOLD)
    description = ft.Text("Aplicación base para RadiaCode")
    monitor_btn = ft.ElevatedButton(
        text="Iniciar Monitoreo",
        on_click=lambda e: asyncio.create_task(toggle_monitoring(e))
    )
    status = ft.Text("", size=16)
    device_info = ft.Text("", size=16, visible=False)
    dose_rate_text = ft.Text("", size=20, visible=False)
    
    page.add(
        ft.Column([
            title,
            description,
            monitor_btn,
            status,
            device_info,
            dose_rate_text
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
    )

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP) 