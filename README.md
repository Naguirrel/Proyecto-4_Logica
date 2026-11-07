# Opción 2: control difuso de un ventilador

Aplicación educativa en Python con scikit-fuzzy. Las reglas y rangos son
supuestos para una demostración académica, no un controlador calibrado.

## Instalación

Usa Python 3.11 o 3.12. Abre una terminal en esta carpeta.

Windows:
```
py -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python ventilador.py --demo
```

Linux/macOS:
```
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python ventilador.py --demo
```

En Ubuntu/Debian, si falta el módulo venv, instala python3-venv mediante
el administrador de paquetes de tu sistema. No necesitas activar el entorno
si utilizas las rutas anteriores. VS Code es opcional.

Quita --demo para ingresar tus propios datos. Escribe salir o presiona Ctrl+C
para finalizar. Puedes usar decimales con punto o coma. Agrega --sin-graficas
si solo quieres la consola y el CSV.

## Modelo y explicación para la exposición

Entradas: temperatura de 0 a 40 °C y humedad relativa de 0 a 100 %.
Salida: velocidad del ventilador expresada como porcentaje, de 0 a 100.
Cada variable tiene tres conjuntos difusos superpuestos.

| Temperatura / Humedad | Baja | Media | Alta |
|---|---|---|---|
| Baja | Lenta | Lenta | Media |
| Media | Media | Media | Rápida |
| Alta | Rápida | Rápida | Rápida |

1. Fuzzificación: calcula pertenencias de las entradas a cada conjunto.
2. Inferencia Mamdani: AND usa el mínimo; cada regla recorta su conjunto de
   salida según su activación y las salidas se agregan usando el máximo.
3. Defuzzificación: el centroide de la salida agregada produce un porcentaje.

Los parámetros exactos de las funciones triangulares y trapezoidales están
en crear_sistema(). Los rangos superpuestos garantizan cobertura del dominio.
El resultado puede combinar varias reglas. Una salida «rápida» no equivale
necesariamente a 100 %, pues se obtiene el centroide del conjunto agregado.

## Evidencia para el PDF

Al terminar una sesión con al menos un caso se crea resultados/:
- casos.csv: entradas y salidas de esa sesión.
- pertenencias.png: gráficas de los conjuntos difusos.
- ultima_inferencia.png: resultado difuso del último caso.

Las gráficas se guardan como imágenes, no se abren en ventanas.
Una nueva ejecución reemplaza estos archivos. Copia los resultados que quieras
conservar antes de volver a ejecutar.

Incluye en el PDF: problema y objetivo, variables y rangos, gráficas de
pertenencia, nueve reglas, explicación del proceso, tabla de pruebas,
interpretación, conclusiones y recomendaciones. Adjunta el código como anexo
si necesitas que el PDF sea autosuficiente. No se genera el PDF automáticamente.
No se requiere Arduino, sensores, base de datos ni API keys.

Documentación: https://scikit-fuzzy.github.io/scikit-fuzzy/
