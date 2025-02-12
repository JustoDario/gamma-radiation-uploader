import flet as ft
from radiacode import RadiaCode
from radiacode.transports.usb import DeviceNotFound as DeviceNotFoundUSB
import requests

def obtener_ubicacion():
    """Gets location using ip-api.com"""
    url = "http://ip-api.com/json"
    try:
        respuesta = requests.get(url, timeout=10)
        if respuesta.status_code == 200:
            datos = respuesta.json()
            if datos.get("status") == "success":
                return f"{datos.get('lat')}, {datos.get('lon')}"
        return "--"
    except Exception as e:
        print(f"Error getting location: {e}")
        return "--"

def get_radiacode_data():
    """Obtiene una única lectura de todos los datos del RadiaCode"""
    try:
        rc = RadiaCode()
        serial = rc.serial_number()
        
        # Obtener una única lectura
        for data in rc.data_buf():
            return {
                "cps": data.count_rate if hasattr(data, 'count_rate') else 0,
                "dose_rate": data.dose_rate if hasattr(data, 'dose_rate') else 0,
                "temperature": data.temperature if hasattr(data, 'temperature') else 0,
                "coords": obtener_ubicacion()
            }
        return None
    except DeviceNotFoundUSB:
        return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.DARK
    page.title = "Radiocode"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Contenedor CPS
    containerCps = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("CPS", size=30, color=ft.colors.BLACK, font_family="Arial"),
                ft.Text("--", size=30, color=ft.colors.BLACK, font_family="Arial", key="cps_value")
            ],
            spacing=2,
        ),
        margin=10,
        padding=10,
        alignment=ft.alignment.center,
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_center,
            end=ft.alignment.bottom_center,
            colors=[ft.colors.GREY, ft.colors.WHITE]
        ),
        width=300,
        height=150,
        border_radius=10
    )

    # Contenedor Temperatura
    containerTemp = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("TEMP", size=25, color=ft.colors.BLACK, font_family="Arial"),
                ft.Text("--", size=30, color=ft.colors.BLACK, font_family="Arial", key="temp_value")
            ],
            spacing=2,
        ),
        margin=10,
        padding=10,
        alignment=ft.alignment.center,
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_center,
            end=ft.alignment.bottom_center,
            colors=[ft.colors.GREY, ft.colors.WHITE]
        ),
        width=300,
        height=150,
        border_radius=10
    )

    # Contenedor Dose
    containerDose = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("DOSE", size=30, color=ft.colors.BLACK, font_family="Arial"),
                ft.Text("--", size=30, color=ft.colors.BLACK, font_family="Arial", key="dose_value")
            ],
            spacing=2,
        ),
        margin=10,
        padding=10,
        alignment=ft.alignment.center,
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_center,
            end=ft.alignment.bottom_center,
            colors=[ft.colors.GREY, ft.colors.WHITE]
        ),
        width=300,
        height=150,
        border_radius=10
    )

    # Contenedor Coordenadas
    containerCoord = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("GPS", size=25, color=ft.colors.BLACK, font_family="Arial"),
                ft.Text("--", size=25, color=ft.colors.BLACK, font_family="Arial", key="coord_value")
            ],
            spacing=2,
        ),
        margin=10,
        padding=10,
        alignment=ft.alignment.center,
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_center,
            end=ft.alignment.bottom_center,
            colors=[ft.colors.GREY, ft.colors.WHITE]
        ),
        width=300,
        height=150,
        border_radius=10
    )

    def update_values(e):
        data = get_radiacode_data()
        if data:
            # Actualizar valores en los contenedores
            for control in containerCps.content.controls:
                if hasattr(control, 'key') and control.key == "cps_value":
                    control.value = f"{data['cps']:.2f}"
            
            for control in containerTemp.content.controls:
                if hasattr(control, 'key') and control.key == "temp_value":
                    control.value = f"{data['temperature']}°C"
            
            for control in containerDose.content.controls:
                if hasattr(control, 'key') and control.key == "dose_value":
                    control.value = f"{data['dose_rate']:.6f}"
            
            for control in containerCoord.content.controls:
                if hasattr(control, 'key') and control.key == "coord_value":
                    control.value = data['coords']
            
            page.update()

    # Botón para actualizar valores
    update_btn = ft.ElevatedButton("Obtener Lectura", on_click=update_values)

    # Contenedor principal
    main_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("RadiaCode OpenRed", size=40, color=ft.colors.WHITE, weight=ft.FontWeight.BOLD),
                ft.Row(
                    controls=[containerCps, containerTemp],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=30,
                ),
                ft.Row(
                    controls=[containerDose, containerCoord],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=30,
                ),
                update_btn
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=30,
        ),
    )

    page.add(main_container)

if __name__ == "__main__":
    ft.app(target=main)