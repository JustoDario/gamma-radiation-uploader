# gamma-radiation-uploader:


![Static Badge](https://img.shields.io/badge/Python%20--green?logo=python&logoColor=green&labelColor=black&color=black)
![Static Badge](https://img.shields.io/badge/Flutter--black?logo=flutter&logoColor=blue&labelColor=white&color=white)
![Static Badge](https://img.shields.io/badge/Flet--red?logo=vercel&logoColor=red&labelColor=white&color=white)


This repo uses [cdump/radiacode](https://github.com/cdump/radiacode) to connect your computer to a radiacode-102 device and catch its lectures in order to send them to an existing database.Additionally in order to make it more pleasing to the user,in [App](https://github.com/JustoDario/gamma-radiation-uploader/tree/main/App)  we have the necesary files in order to create a simple linux desktop app. **Work in progress - For now its Linux compatible but Im working in an easier way to pack all the program dependencies**


## Radiacode_info_uploader:
In this directory you will find :
* [Dependecies Instalation](https://github.com/JustoDario/gamma-radiation-uploader/tree/main/radiacode_info_uploader/install): You will find a python3 script that installs the dependencies necesaries to run /Program.In this directory there is also a .bat for windows but **its not finished**.
* [Program](https://github.com/JustoDario/gamma-radiation-uploader/tree/main/radiacode_info_uploader/program):Here is /radiacode_data_uploader.py.Once every dependency is installed **this program contains all the logic behind this project**
  it connects to the radiacode device pluged via USB (**BLUETOOTH conection isnt supported yet**)and using json format it uses OpenRed API to send the data allong with the **user location** wich is obtained scanning every wifi available,usig their IPs for more precision we use an open library to triangulate the user location as almost every PC doesnt have GPS incorporated and we avoided using APIs wich require token ID == Payment.


## App:
![Screenshot from 2025-02-12 11-44-36](https://github.com/user-attachments/assets/789fa6ec-dad8-4225-b5a1-26dfbdd3dbe9)

**I recommend running it in a virtual envoiroment**

Since it was our first time using flet or building an executable app this version has a lot of work to be done.I encourage people to upgrade it,but it basically uses [Program](https://github.com/JustoDario/gamma-radiation-uploader/tree/main/radiacode_info_uploader/program) logic and combine it with some visual elements.

In [Flet App](https://github.com/JustoDario/gamma-radiation-uploader/tree/main/App/first-flet-app/src) you will find every python script needed to run :
```bash
flet build linux 
```
wich will create a /build/linux with your app wich will be runable with ./src or double click .
This directory also has install_dependecies.py but we are sorry to inform that it isnt 100% working.

### Dependencies:
As this repository was created in 2 days during a hackaton altought I intended to ,we didnt have enough time to make sure everything works for every machine.I apologize if using this repo you have to go throght the same suffering I went to satisfy the missing dependencies error.There is a lot of work to be done.
