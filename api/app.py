from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/temperaturas', methods=['GET'])
def obtener_temperaturas():
    resultados = []

    with open("../output/output.txt", "r", encoding="utf-16") as archivo:
        for linea in archivo:
            try:
                if not linea.strip():
                    continue  # omitir líneas vacías

                clave, valor = linea.strip().split('\t')
                clave = clave.strip('"')
                datos = eval(valor)

                if not clave.startswith("2025"):
                    continue

                resultados.append({
                    "timestamp": clave,
                    "temperatura_promedio": datos["avg_temp"]
                })
            except Exception as e:
                print("Error al procesar línea:", linea)
                print(e)
                continue

    return jsonify(resultados)



if __name__ == '__main__':
    app.run(debug=True)
