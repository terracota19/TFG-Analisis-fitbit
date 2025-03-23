```
 _   _                 _   ____               _ _ ___ _   
| | | | ___  __ _ _ __| |_|  _ \ _ __ ___  __| ( )_ _| |_ 
| |_| |/ _ \/ _` | '__| __| |_) | '__/ _ \/ _` |/ | || __|
|  _  |  __/ (_| | |  | |_|  __/| | |  __/ (_| |  | || |_ 
|_| |_|\___|\__,_|_|   \__|_|   |_|  \___|\__,_| |___|\__|

```

# **Guía de Instalación de la Aplicación HeartPred'it**

Bienvenido a la guía de instalación de la aplicación **HeartPred'it**. A continuación, te proporcionamos los pasos necesarios para configurar tu entorno y ejecutar la aplicación correctamente.

---

## **Requisitos Previos**

Antes de ejecutar la aplicación, asegúrate de tener instalados los siguientes componentes:

### 1. **MongoDB**
   - **Versión recomendada**: v7.0.x.
   - **Descarga MongoDB** desde [aquí](https://www.mongodb.com/try/download/community) (archivo `.msi`).
   
   **Pasos de instalación**:
   1. Durante la instalación, selecciona la opción **Complete** en la ventana de **Choose setup type**.
   2. En la ventana **Server configuration**, desactiva la opción **Install MongoD as a Service**. Esto te permitirá iniciar el servidor manualmente cuando lo necesites.

### 2. **Configuración del Sistema**
   Para asegurar que MongoDB y otros componentes funcionen correctamente, realiza las siguientes configuraciones:
   
   - **Variables de entorno**:
     - Añade la carpeta `bin` de MongoDB a las variables de entorno **Path** del usuario y del sistema.
     - Esto te permitirá ejecutar los comandos `mongod` y `mongo` desde cualquier terminal.
   
   - **Crear carpeta de datos**:
     - Crea la carpeta `C:/hlocal/datos` en tu disco C para almacenar los datos de MongoDB.

### 3. **Python**
   - **Descargar e instalar Python** desde [aquí](https://www.python.org/downloads/).
   - Asegúrate de seleccionar la opción **Agregar Python al PATH** durante la instalación para poder ejecutar los comandos `python` y `pip` desde cualquier terminal.

### 4. **Cuenta de Fitbit**
   - **Regístrate en Fitbit** para obtener una cuenta en [este enlace](https://www.fitbit.com/global/es/home).
   
### 5. **Dispositivo Fitbit**
   - **Adquiere un dispositivo Fitbit** (pulsera) desde [este enlace](https://www.fitbit.com/global/es/home).

---

## **Métodos de Ejecución**

Existen dos formas de ejecutar la aplicación: automática y manual. A continuación, te explicamos ambas opciones.

### **Ejecutar la Aplicación Automáticamente**
   Si prefieres automatizar el proceso de instalación y ejecución, sigue estos pasos:
   1. Ejecuta el archivo **`HeartPred'it.bat`**.
   2. Este script instalará automáticamente las dependencias necesarias e iniciará la aplicación.

### **Ejecutar la Aplicación Manualmente**
   Si prefieres controlar cada paso de la ejecución, sigue estos pasos:

#### 1. **Iniciar MongoDB**
   - Abre una terminal (por ejemplo, **Terminal 1**).
   - Ejecuta el siguiente comando para iniciar el servidor MongoDB:
     ```bash
     mongod --dbpath C:\hlocal\datos
     ```
     Este comando iniciará el servidor de MongoDB utilizando la carpeta que has creado anteriormente para almacenar los datos.

#### 2. **Iniciar la Aplicación**
   - Abre una nueva terminal (por ejemplo, **Terminal 2**).
   - Dirígete a la carpeta donde se encuentra el archivo `main.py`.
   - Ejecuta el siguiente comando para iniciar la aplicación:
     ```bash
     python ruta:/main.py
     ```
     Asegúrate de reemplazar `ruta:/main.py` por la ruta exacta del archivo `main.py` en tu sistema.

---

