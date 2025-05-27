# Proyecto MapReduce 

Este documento describe el procedimiento completo para desplegar y ejecutar un proyecto de procesamiento distribuido con Hadoop MapReduce sobre Amazon EMR. La salida del procesamiento se sirve mediante una API Flask accesible desde el exterior.

---

## Requisitos previos

* Acceso a una instancia de Amazon EMR con Hadoop configurado.
* Llave privada `.pem` para acceder por SSH al nodo master.
* Acceso a la terminal local con `scp` y `ssh` instalados.
* Proyecto local con la siguiente estructura:

```
proyecto-mapreduce/
├── api/
│   └── app.py
├── data/
│   └── data.csv
├── mapreduce/
│   └── analyze.py
├── output/
├── run_pipeline.sh
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
mkdir -p /home/hadoop/proyecto-mapreduce
```

Desde la terminal local:

```bash
scp -i C:\Users\Msi\Downloads\p3-key.pem.pem -r "C:\Users\Msi\Desktop\proyecto-mapreduce - copia\*" hadoop@ec2-100-26-229-126.compute-1.amazonaws.com:/home/hadoop/proyecto-mapreduce
```

---

## 4. Subir el archivo de datos a HDFS

```bash
hdfs dfs -mkdir -p /user/admin/input
hdfs dfs -put data/data.csv /user/admin/input/

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
```

---

## 7. Descargar resultados de HDFS al nodo master

```bash

# Eliminar resultados previos si existen
rm -f output/output.txt

mkdir -p output
hdfs dfs -getmerge /user/admin/output/ output/output.txt
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

## 9. Automatizar ejecución con `run_pipeline.sh`

El script `run_pipeline.sh` realiza el flujo completo desde la eliminación de la salida en HDFS hasta la generación de `output.txt`.

### Contenido del script:

```bash
#!/bin/bash

source venv/bin/activate

echo "Eliminando salida anterior en HDFS..."
hdfs dfs -rm -r -f /user/admin/output

echo "Ejecutando MapReduce con analyze.py..."
python3 mapreduce/analyze.py hdfs:///user/admin/input/data.csv -r hadoop --output-dir hdfs:///user/admin/output

echo "Limpiando carpeta local de salida..."
rm -rf output
mkdir -p output

echo "Descargando resultados de HDFS..."
hdfs dfs -getmerge /user/admin/output/ output/output.txt

echo "Proceso completado. Ahora puedes ejecutar tu API si lo deseas:"
echo "   python3 api/app.py --host=0.0.0.0 --port=5000"
```

### Ejecutar:

```bash
chmod +x run_pipeline.sh
./run_pipeline.sh
```

---

## Observaciones Finales

* El archivo de salida `output.txt` debe existir antes de que la API pueda mostrar resultados.
* Se debe tener acceso público abierto al puerto 5000 en las reglas del Security Group de EC2.
* En caso de problemas de red, usa el DNS público o la IP directamente desde el navegador.
