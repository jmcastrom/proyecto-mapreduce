# Proyecto MapReduce 

Este proyecto implementa una arquitectura de procesamiento distribuido utilizando Hadoop MapReduce sobre un clúster EMR (Elastic MapReduce) en AWS. El objetivo es analizar grandes volúmenes de datos de clima y salud (EPS) y exponer los resultados mediante una API desarrollada en Flask.

Una version en video sobre este proyecto puede ser vista en el siguiente enlace: https://www.youtube.com/watch?v=B9WU4dgQ-lY&ab_channel=AlejandroQuintero

## 1. Descripción General

Se desarrollaron dos programas MapReduce independientes utilizando la librería `mrjob`, que procesan distintas fuentes de datos:

- **analyze.py**: analiza registros meteorológicos para obtener la temperatura promedio por día.
- **mapreduce_EPS.py**: analiza indicadores de calidad de EPS para calcular el tiempo de espera promedio y máximo por EPS.

Los resultados de ambos procesos se exponen a través de endpoints REST desarrollados con Flask.


## 2. Objetivos del Proyecto

- Procesar datos masivos en paralelo utilizando Hadoop.
- Automatizar la ejecución de MapReduce y la extracción de resultados desde HDFS.
- Visualizar resultados a través de una API REST sencilla y funcional.
- Aplicar buenas prácticas de programación y despliegue en la nube.

## 3. Fuentes de Datos

### 3.1 Clima (data.csv)

- Datos reales obtenidos de sensores meteorológicos.
- Campos relevantes: `time`, `temperature_2m`.
- Propósito: analizar la evolución diaria de la temperatura promedio durante el año 2025.

### 3.2 Indicadores de EPS (Clicsalud)

- Archivo: `Clicsalud-_Indicadores_de_calidad_EPS_20250522.csv`
- Contiene datos por EPS, incluyendo el tiempo de espera promedio para atención.
- Propósito: evaluar el desempeño de las EPS en Colombia mediante métricas cuantificables.

## 4. Componentes del Proyecto

### 4.1 MapReduce - analyze.py

Procesa las temperaturas por día.

- **Mapper**: extrae la fecha y temperatura por fila.
- **Reducer**: calcula la temperatura promedio por día.


### 4.2 MapReduce - mapreduce_EPS.py

Procesa los tiempos de espera de cada EPS.

- **Mapper**: obtiene EPS y tiempo de espera por fila.
- **Reducer**: calcula tiempo de espera promedio y máximo por EPS.

### 4.3 API REST (app.py)

Expuesta en Flask con dos endpoints:

- `/temperaturas`: devuelve un JSON con temperatura promedio por fecha.
- `/eps`: devuelve un JSON con tiempos de espera promedio y máximo por EPS.

Internamente, ambos leen archivos resultantes de MapReduce (`output.txt`, `eps_output.txt`) procesados desde HDFS.

## 5. Arquitectura y Despliegue

### 5.1 Clúcster EMR y Nodo Master

- Se configuró un clúcster EMR en AWS con un nodo master EC2 (instancia `m5.xlarge`).
- Hadoop se instaló automáticamente y se ejecutaron los scripts directamente desde SSH.

### 5.2 Carga de Datos y Ejecución

- Los archivos `.csv` se subieron a HDFS mediante `hdfs dfs -put`.
- Se ejecutó el programa MapReduce usando `mrjob` con el runner `-r hadoop`.
- Los resultados fueron descargados con `hdfs dfs -getmerge`.


## 6. Resultados

### 6.1 Análisis Climático

Se obtuvo un JSON con temperatura promedio por día para el año 2025, accesible en `/temperaturas`. Ejemplo:

```json
{
  "timestamp": "2025-04-15",
  "temperatura_promedio": 22.3
}
```

### 6.2 Análisis EPS

Se obtuvo un JSON con el tiempo de espera promedio y máximo por EPS, accesible en `/eps`. Ejemplo:

```json
{
  "eps": "SALUDTOTAL",
  "tiempo_espera_promedio": 23.6,
  "tiempo_espera_maximo": 55
}
```


---
# Replicación Proyecto  


## Requisitos previos

* Acceso a una instancia de Amazon EMR con Hadoop configurado.
* Llave privada `.pem` para acceder por SSH al nodo master.
* Acceso a la terminal local con `scp` y `ssh` instalados.
* Proyecto local con la siguiente estructura:

```
proyecto-mapreduce/
├── api/
│   └── app.py
│   └── static/
│       └── index.html
├── data/
│   └── data.csv
│   └── EPS_data.csv
├── mapreduce/
│   └── analyze.py
│   └── mapreduce_EPS.py
├── output/
├── requirements.txt
└── README.md
```

---

## 1. Conexión por SSH al nodo master

```bash
ssh -i "C:\Users\Msi\Downloads\p3-key.pem.pem" hadoop@ec2-100-26-229-126.compute-1.amazonaws.com
```

## 2. Verificación de HDFS

```bash
hdfs dfs -ls /
hdfs dfs -mkdir /user/admin
hdfs dfs -mkdir /user/admin/test

# Archivo de prueba
echo "Archivo de prueba para Lab EMR" > prueba.txt
hdfs dfs -copyFromLocal prueba.txt /user/admin/test/
hdfs dfs -ls /user/admin/test
hdfs dfs -cat /user/admin/test/prueba.txt
```

## 3. Subir el código del proyecto al nodo master

Desde el nodo master:

```bash
# Clonación del repositorio del proyecto
git clone https://github.com/jmcastrom/proyecto-mapreduce
cd proyecto-mapreduce
```

---

## 4. Subir el archivo de datos a HDFS

```bash
hdfs dfs -mkdir -p /user/admin/input
hdfs dfs -put data/data.csv /user/admin/input/
hdfs dfs -put data/EPS_data.csv /user/admin/input/
# Verificar existencia
hdfs dfs -ls /user/admin/input
```

---

## 5. Configurar entorno virtual y dependencias

```bash
cd proyecto-mapreduce
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 6. Ejecutar el procesamiento MapReduce

```bash
# Eliminar salidas previas
hdfs dfs -rm -r /user/admin/output

# Ejecutar MapReduce
python mapreduce/analyze.py hdfs:///user/admin/input/data.csv -r hadoop --output-dir hdfs:///user/admin/output

python mapreduce/mapreduce_EPS.py hdfs:///user/admin/input/EPS_data.csv -r hadoop --output-dir hdfs:///user/admin/eps_output
```

---

## 7. Descargar resultados de HDFS al nodo master

```bash

# Eliminar resultados previos si existen
rm -f output/output.txt

mkdir -p output
hdfs dfs -getmerge /user/admin/output/ output/output.txt
hdfs dfs -getmerge /user/admin/eps_output/ output/eps_output.txt
```

---

## 8. Ejecutar la API Flask

```bash
python api/app.py --host=0.0.0.0 --port=5000
```

Verificar disponibilidad en:

```
http://<PUBLIC-IP>:5000/temperaturas
```

Para identificar y cerrar el proceso anterior (si el puerto ya está en uso):

```bash
lsof -i :5000
kill -9 <PID>
```

---

## Observaciones Finales

* El archivo de salida `output.txt` debe existir antes de que la API pueda mostrar resultados.
* Se debe tener acceso público abierto al puerto 5000 en las reglas del Security Group de EC2.
* En caso de problemas de red, se usa el DNS público o la IP directamente desde el navegador.
