import os
import sys
import platform
import subprocess
import shutil
import glob

def install_package(package):
    try:
        if platform.system() == "Windows":
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        else:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--break-system-packages", package])
        print(f"✓ Instalado {package}")
    except Exception as e:
        print(f"✗ Error instalando {package}: {str(e)}")

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
        "flet>=0.21.0",  # Volvemos a la versión actual
    ]
    
    # Instalar dependencias según el sistema operativo
    if os_name == "Linux":
        print("\n=== Instalando dependencias del sistema (Linux) ===")
        subprocess.run(["sudo", "apt-get", "update"])
        subprocess.run([
            "sudo", 
            "apt-get", 
            "install", 
            "-y", 
            "libusb-1.0-0-dev",
            "bluetooth",
            "libbluetooth-dev",
            "git",
            "python3-dev",
            "mpv",
            "libmpv-dev",
            # Dependencias para construir la aplicación
            "build-essential",  # Incluye compiladores C/C++
            "ninja-build",
            "libgtk-3-dev",
            "cmake",
            "pkg-config",
            "clang"  # clang++ viene incluido en este paquete
        ])
        
        # Crear enlace simbólico para libmpv.so.1
        print("\n=== Configurando libmpv para Flet ===")
        try:
            subprocess.run([
                "sudo",
                "ln",
                "-sf",  # -f para forzar si ya existe
                "/usr/lib/x86_64-linux-gnu/libmpv.so",
                "/usr/lib/x86_64-linux-gnu/libmpv.so.1"
            ])
            print("✓ Enlace simbólico de libmpv creado correctamente")
            print("  Esto es necesario para que Flet funcione correctamente en Linux")
        except Exception as e:
            print(f"✗ Error creando enlace simbólico: {str(e)}")
            print("  Por favor, verifica que mpv y libmpv-dev están instalados correctamente")
        
        # Crear reglas udev para acceso USB desde radiacode.rules
        udev_rule = '''SUBSYSTEM=="usb", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="f123", MODE="0666", GROUP="plugdev"
KERNEL=="hidraw*", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="f123", MODE="0666", GROUP="plugdev"'''
        try:
            with open("/etc/udev/rules.d/99-radiacode.rules", "w") as f:
                f.write(udev_rule)
            subprocess.run(["sudo", "udevadm", "control", "--reload-rules"])
            subprocess.run(["sudo", "udevadm", "trigger"])
            print("✓ Reglas udev instaladas")
        except Exception as e:
            print(f"✗ Error instalando reglas udev: {str(e)}")
            
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
        
        # Instalar mpv para Windows
        print("\n=== Instalando MPV para Windows ===")
        print("1. Descarga MPV desde: https://sourceforge.net/projects/mpv-player-windows/files/latest/download")
        print("2. Extrae el archivo zip")
        print("3. Copia el archivo 'mpv-2.dll' a C:\\Windows\\System32")
        print("4. Renombra 'mpv-2.dll' a 'mpv-1.dll'")
        input("\nPresiona Enter cuando hayas completado estos pasos...")
        
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
            
            # Actualizar pip sin --break-system-packages en Windows
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
            print("✓ pip actualizado")
        except Exception as e:
            print(f"✗ Error verificando Python/pip: {str(e)}")
            sys.exit(1)
        
        # Instalar wheel para mejor soporte de paquetes binarios
        install_package("wheel")
    
    elif os_name == "Darwin":  # MacOS
        print("\n=== Instalando dependencias del sistema (MacOS) ===")
        subprocess.run(["brew", "install", "libusb", "git"])
    
    print("\n=== Instalando dependencias de Python ===")
    for package in packages:
        install_package(package)
    
    # Instalar radiacode por separado
    print("\n=== Instalando RadiaCode desde GitHub ===")
    try:
        cmd = [
            sys.executable, 
            "-m", 
            "pip", 
            "install",
            "--force-reinstall",
            "--verbose",
        ]
        if platform.system() != "Windows":
            cmd.append("--break-system-packages")
        cmd.append("git+https://github.com/cdump/radiacode.git")
        
        subprocess.check_call(cmd)
        print("✓ RadiaCode instalado correctamente")
        
        # Verificar la instalación
        print("\n=== Verificando instalación de RadiaCode ===")
        try:
            import radiacode
            print(f"✓ Módulo RadiaCode encontrado en: {radiacode.__file__}")
            print(f"✓ Versión instalada: {radiacode.__version__}")
        except ImportError as e:
            print(f"✗ Error importando RadiaCode después de la instalación: {str(e)}")
            print("\nVerificando rutas de Python:")
            print("Rutas de búsqueda de Python:")
            for path in sys.path:
                print(f"  - {path}")
            
            # Intentar encontrar el paquete manualmente
            site_packages = [p for p in sys.path if 'site-packages' in p]
            for sp in site_packages:
                print(f"\nBuscando en {sp}:")
                for file in glob.glob(os.path.join(sp, "radiacode*")):
                    print(f"  Encontrado: {file}")
            
            raise Exception("No se pudo verificar la instalación de RadiaCode")
    except Exception as e:
        print(f"✗ Error instalando RadiaCode: {str(e)}")

    print("\n=== Instalación completada ===")
    print("IMPORTANTE: Si estás usando un entorno virtual, asegúrate de activarlo antes de ejecutar el programa:")
    print("source .venv/bin/activate  # Para Linux/Mac")
    print(".venv\\Scripts\\activate    # Para Windows")
    print("\nLuego puedes ejecutar el programa con:")
    print("python radiacode_gui.py")

if __name__ == "__main__":
    main() 