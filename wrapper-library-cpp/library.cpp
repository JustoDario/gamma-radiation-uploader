#define PY_SSIZE_T_CLEAN
#include <python3.10/Python.h>
#include <python3.10/datetime.h>
#include <string>
#include <vector>
#include <memory>
#include <stdexcept>

class RadiaCodeWrapper {
private:
    PyObject* pModule;
    PyObject* pRadiaCodeClass;
    PyObject* pRadiaCodeInstance;
    
    // Inicializa el intérprete de Python y carga el módulo
    bool initializePython() {
        Py_Initialize();
        if (PyDateTimeAPI == NULL) {
            PyDateTime_IMPORT;
        }
        
        // Reemplazar con:
        PyObject* datetime_module = PyImport_ImportModule("datetime");
        if (datetime_module == NULL) {
            return false;
        }
        Py_DECREF(datetime_module);
        
        // Importa el módulo radiacode
        pModule = PyImport_ImportModule("radiacode");
        if (!pModule) {
            PyErr_Print();
            return false;
        }
        
        // Obtiene la clase RadiaCode
        pRadiaCodeClass = PyObject_GetAttrString(pModule, "RadiaCode");
        if (!pRadiaCodeClass) {
            PyErr_Print();
            return false;
        }
        
        return true;
    }

public:
    struct RadiationData {
        double uSvh;              // Tasa de dosis en μSv/h
        double cps;               // Cuentas por segundo
        double doseRateError;     // Error % de la tasa de dosis
        std::string timestamp;    // Hora de la medición
        std::string serialNumber; // Número de serie
        std::vector<int> spectrum;// Espectro de radiación
        double temperature;       // Temperatura
    };

    // Constructor - Conecta con el dispositivo por USB o Bluetooth
    RadiaCodeWrapper(const std::string& bluetoothMac = "", const std::string& serialNumber = "") {
        if (!initializePython()) {
            throw std::runtime_error("Failed to initialize Python interpreter");
        }

        // Crea los argumentos para el constructor de RadiaCode
        PyObject* pArgs = PyTuple_New(2);
        if (!bluetoothMac.empty()) {
            PyTuple_SetItem(pArgs, 0, PyUnicode_FromString(bluetoothMac.c_str()));
            PyTuple_SetItem(pArgs, 1, Py_None);
        } else {
            PyTuple_SetItem(pArgs, 0, Py_None);
            PyTuple_SetItem(pArgs, 1, PyUnicode_FromString(serialNumber.c_str()));
        }

        // Crea una instancia de RadiaCode
        pRadiaCodeInstance = PyObject_CallObject(pRadiaCodeClass, pArgs);
        Py_DECREF(pArgs);

        if (!pRadiaCodeInstance) {
            PyErr_Print();
            throw std::runtime_error("Failed to create RadiaCode instance");
        }
    }

    // Obtiene todos los datos de radiación
    RadiationData getData() {
        RadiationData data;
        
        // Obtiene los datos del buffer
        PyObject* pDataBuf = PyObject_CallMethod(pRadiaCodeInstance, "data_buf", NULL);
        if (pDataBuf && PyList_Check(pDataBuf)) {
            // Procesa el último elemento de la lista
            PyObject* pLastData = PyList_GetItem(pDataBuf, PyList_Size(pDataBuf) - 1);
            if (pLastData) {
                // Obtiene la tasa de dosis (convertida a μSv/h)
                PyObject* pDoseRate = PyObject_GetAttrString(pLastData, "dose_rate");
                data.uSvh = PyFloat_AsDouble(pDoseRate) * 10000; // Convierte a μSv/h
                Py_XDECREF(pDoseRate);

                // Obtiene CPS
                PyObject* pCountRate = PyObject_GetAttrString(pLastData, "count_rate");
                data.cps = PyFloat_AsDouble(pCountRate);
                Py_XDECREF(pCountRate);

                // Obtiene el error de la tasa de dosis
                PyObject* pDoseRateErr = PyObject_GetAttrString(pLastData, "dose_rate_err");
                data.doseRateError = PyFloat_AsDouble(pDoseRateErr);
                Py_XDECREF(pDoseRateErr);

                // Obtiene el timestamp
                PyObject* pDateTime = PyObject_GetAttrString(pLastData, "dt");
                PyObject* pTimeStr = PyObject_CallMethod(pDateTime, "strftime", "s", "%H:%M");
                data.timestamp = PyUnicode_AsUTF8(pTimeStr);
                Py_XDECREF(pTimeStr);
                Py_XDECREF(pDateTime);
            }
        }
        Py_XDECREF(pDataBuf);

        // Obtiene el número de serie
        PyObject* pConfig = PyObject_CallMethod(pRadiaCodeInstance, "configuration", NULL);
        if (pConfig) {
            PyObject* pLines = PyObject_CallMethod(pConfig, "split", "s", "\n");
            if (pLines && PyList_Check(pLines)) {
                for (Py_ssize_t i = 0; i < PyList_Size(pLines); i++) {
                    PyObject* pLine = PyList_GetItem(pLines, i);
                    std::string line = PyUnicode_AsUTF8(pLine);
                    if (line.find("SerialNumber=") == 0) {
                        data.serialNumber = line.substr(12);
                        break;
                    }
                }
            }
            Py_XDECREF(pLines);
            Py_XDECREF(pConfig);
        }

        // Obtiene el espectro
        PyObject* pSpectrum = PyObject_CallMethod(pRadiaCodeInstance, "spectrum", NULL);
        if (pSpectrum) {
            PyObject* pCounts = PyObject_GetAttrString(pSpectrum, "counts");
            if (pCounts && PyList_Check(pCounts)) {
                for (Py_ssize_t i = 0; i < PyList_Size(pCounts); i++) {
                    PyObject* pCount = PyList_GetItem(pCounts, i);
                    data.spectrum.push_back(PyLong_AsLong(pCount));
                }
            }
            Py_XDECREF(pCounts);
            Py_XDECREF(pSpectrum);
        }

        // Obtiene la temperatura del último RareData
        PyObject* pDataBufTemp = PyObject_CallMethod(pRadiaCodeInstance, "data_buf", NULL);
        if (pDataBufTemp && PyList_Check(pDataBufTemp)) {
            for (Py_ssize_t i = PyList_Size(pDataBufTemp) - 1; i >= 0; i--) {
                PyObject* pData = PyList_GetItem(pDataBufTemp, i);
                if (PyObject_HasAttrString(pData, "temperature")) {
                    PyObject* pTemp = PyObject_GetAttrString(pData, "temperature");
                    data.temperature = PyFloat_AsDouble(pTemp);
                    Py_XDECREF(pTemp);
                    break;
                }
            }
        }
        Py_XDECREF(pDataBufTemp);

        return data;
    }

    // Destructor
    ~RadiaCodeWrapper() {
        Py_XDECREF(pRadiaCodeInstance);
        Py_XDECREF(pRadiaCodeClass);
        Py_XDECREF(pModule);
        Py_Finalize();
    }
};
