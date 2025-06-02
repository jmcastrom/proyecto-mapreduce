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
* En caso de problemas de red, usa el DNS público o la IP directamente desde el navegador.
