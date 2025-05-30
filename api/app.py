from flask import Flask, jsonify, send_from_directory
import os

app = Flask(__name__, static_folder='static')


@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/temperaturas', methods=['GET'])
def obtener_temperaturas():
    resultados = []

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(BASE_DIR, "output", "output.txt")

    try:
        with open(output_path, "r", encoding="utf-8") as archivo:
            for linea in archivo:
                try:
                    if not linea.strip():
                        continue

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
    except FileNotFoundError:
        return jsonify({"error": "El archivo output.txt no fue encontrado."}), 404
    except UnicodeDecodeError as e:
        return jsonify({"error": f"Error de codificación: {str(e)}"}), 500

    return jsonify(resultados)

@app.route('/eps', methods=['GET'])
def obtener_eps():
    resultados = []

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(BASE_DIR, "output", "eps_output.txt")

    try:
        with open(output_path, "r", encoding="utf-8") as archivo:
            for linea in archivo:
                try:
                    if not linea.strip():
                        continue

                    clave, valor = linea.strip().split('\t')
                    clave = clave.strip('"')
                    datos = eval(valor)

                    resultados.append({
                        "eps": clave,
                        "tiempo_espera_promedio": datos["avg_wait_time"],
                        "tiempo_espera_maximo": datos["max_wait_time"]
                    })
                except Exception as e:
                    print("Error al procesar línea:", linea)
                    print(e)
                    continue
    except FileNotFoundError:
        return jsonify({"error": "El archivo eps_output.txt no fue encontrado."}), 404
    except UnicodeDecodeError as e:
        return jsonify({"error": f"Error de codificación: {str(e)}"}), 500

    return jsonify(resultados)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
