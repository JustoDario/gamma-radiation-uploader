import os
import sys
import platform
import subprocess
import shutil

def install_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--break-system-packages", package])
        print(f"✓ Instalado {package}")
    except:
        print(f"✗ Error instalando {package}")

def main():
    print("=== Instalando dependencias para RadiaCode ===")
    
    # Detectar sistema operativo
    os_name = platform.system()
    print(f"Sistema operativo detectado: {os_name}")
    
    # Instalar pip si no está instalado
    try:
        import pip
    except ImportError:
        print("Instalando pip...")
        if os_name == "Windows":
            os.system("curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py")
            os.system(f"{sys.executable} get-pip.py")
        else:
            os.system("sudo apt-get install python3-pip -y")
    
    # Dependencias básicas de Python según poetry.lock
    packages = [
        "requests>=2.32.3",
        "setuptools>=75.8.0",
        "jinja2",
        "typeguard>=4.4.1",
        "pyusb",
        "bluepy;platform_system!='Windows'",  # Solo para Linux
        "certifi",
        "charset-normalizer>=2,<4",
        "idna>=3.10",
        "urllib3>=2.3.0",
        "typing-extensions>=4.12.2",
        "importlib-metadata>=8.6.1;python_version<'3.10'",
        "zipp>=3.20",
        "git+https://github.com/cdump/radiacode.git"  # Instalar radiacode directamente desde GitHub
    ]
    
    # Instalar dependencias según el sistema operativo
    if os_name == "Linux":
        print("\n=== Instalando dependencias del sistema (Linux) ===")
        os.system("sudo apt-get update")
        os.system("sudo apt-get install -y libusb-1.0-0-dev bluetooth libbluetooth-dev git python3-dev")
        
        # Crear reglas udev para acceso USB desde radiacode.rules
        udev_rule = '''SUBSYSTEM=="usb", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="f123", MODE="0666", GROUP="plugdev"
KERNEL=="hidraw*", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="f123", MODE="0666", GROUP="plugdev"'''
        try:
            with open("/etc/udev/rules.d/99-radiacode.rules", "w") as f:
                f.write(udev_rule)
            os.system("sudo udevadm control --reload-rules")
            os.system("sudo udevadm trigger")
            print("✓ Reglas udev instaladas")
        except:
            print("✗ Error instalando reglas udev")
            
    elif os_name == "Windows":
        print("\n=== Instalando dependencias del sistema (Windows) ===")
        
        # Verificar si Git está instalado
        try:
            subprocess.check_call(["git", "--version"])
            print("✓ Git ya está instalado")
        except:
            print("Instalando Git...")
            print("Por favor, descarga e instala Git desde: https://git-scm.com/download/win")
            input("Presiona Enter cuando hayas instalado Git...")
        
        # Verificar Visual C++ Redistributable
        print("\nVerificando Visual C++ Redistributable...")
        print("Si el programa falla más tarde, por favor instala:")
        print("Microsoft Visual C++ Redistributable: https://aka.ms/vs/17/release/vc_redist.x64.exe")
        
        # Instalar libusb mediante Zadig
        print("\nPara conectar el dispositivo RadiaCode:")
        print("1. Conecta el dispositivo RadiaCode por USB")
        print("2. Instala Zadig desde: https://zadig.akeo.ie/")
        print("3. En Zadig:")
        print("   - Menú Options > List All Devices")
        print("   - Selecciona 'RadiaCode' en el desplegable")
        print("   - Selecciona el driver 'WinUSB'")
        print("   - Haz clic en 'Install Driver' o 'Replace Driver'")
        input("\nPresiona Enter cuando hayas completado estos pasos...")
        
        # Verificar Python y pip
        try:
            python_version = platform.python_version()
            print(f"\n✓ Python {python_version} instalado")
            
            # Actualizar pip
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--break-system-packages", "--upgrade", "pip"])
            print("✓ pip actualizado")
        except:
            print("✗ Error verificando Python/pip")
            sys.exit(1)
        
        # Instalar wheel para mejor soporte de paquetes binarios
        install_package("wheel")
    
    elif os_name == "Darwin":  # MacOS
        print("\n=== Instalando dependencias del sistema (MacOS) ===")
        os.system("brew install libusb git")
    
    print("\n=== Instalando dependencias de Python ===")
    for package in packages:
        install_package(package)
    
    print("\n=== Instalación completada ===")
    print("Puedes ejecutar el programa con:")
    print("python basic.py")

if __name__ == "__main__":
    main() 