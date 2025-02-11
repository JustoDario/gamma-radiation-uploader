#include <iostream>
#include "library.cpp"  // O mejor crear un library.h

int main() {
    try {
        // Conecta con el dispositivo (por Bluetooth o USB)
        RadiaCodeWrapper rc("52:43:06:60:0d:0d");  // Reemplaza con tu MAC address
        
        // Obtiene los datos
        auto data = rc.getData();
        
        // Muestra los datos
        std::cout << "Tasa de dosis: " << data.uSvh << " μSv/h\n";
        std::cout << "CPS: " << data.cps << "\n";
        std::cout << "Error: " << data.doseRateError << "%\n";
        std::cout << "Hora: " << data.timestamp << "\n";
        std::cout << "S/N: " << data.serialNumber << "\n";
        std::cout << "Temperatura: " << data.temperature << "°C\n";
        
        // Muestra el espectro
        std::cout << "Espectro (primeros 10 valores): ";
        for (int i = 0; i < 10 && i < data.spectrum.size(); ++i) {
            std::cout << data.spectrum[i] << " ";
        }
        std::cout << "\n";
        
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
    
    return 0;
}
