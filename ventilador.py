"""Control difuso educativo: temperatura y humedad -> velocidad del ventilador.

Ejecutar: python ventilador.py
Demo reproducible: python ventilador.py --demo
Solo consola: python ventilador.py --demo --sin-graficas
"""
import argparse
import csv
import math
from pathlib import Path

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


def crear_sistema():
    # Universos de discurso. Los extremos se incluyen en los arreglos.
    temperatura = ctrl.Antecedent(np.arange(0, 41, 1), 'temperatura')
    humedad = ctrl.Antecedent(np.arange(0, 101, 1), 'humedad')
    velocidad = ctrl.Consequent(np.arange(0, 101, 1), 'velocidad')

    # Conjuntos superpuestos: un valor puede pertenecer a dos categorías.
    temperatura['baja'] = fuzz.trapmf(temperatura.universe, [0, 0, 15, 25])
    temperatura['media'] = fuzz.trimf(temperatura.universe, [15, 25, 35])
    temperatura['alta'] = fuzz.trapmf(temperatura.universe, [25, 35, 40, 40])
    humedad['baja'] = fuzz.trapmf(humedad.universe, [0, 0, 30, 50])
    humedad['media'] = fuzz.trimf(humedad.universe, [30, 50, 70])
    humedad['alta'] = fuzz.trapmf(humedad.universe, [50, 70, 100, 100])
    velocidad['lenta'] = fuzz.trapmf(velocidad.universe, [0, 0, 20, 40])
    velocidad['media'] = fuzz.trimf(velocidad.universe, [20, 50, 80])
    velocidad['rapida'] = fuzz.trapmf(velocidad.universe, [60, 80, 100, 100])
    velocidad.defuzzify_method = 'centroid'

    # Nueve reglas cubren todas las combinaciones de categorías.
    tabla = [
        ('baja', 'baja', 'lenta'),
        ('baja', 'media', 'lenta'),
        ('baja', 'alta', 'media'),
        ('media', 'baja', 'media'),
        ('media', 'media', 'media'),
        ('media', 'alta', 'rapida'),
        ('alta', 'baja', 'rapida'),
        ('alta', 'media', 'rapida'),
        ('alta', 'alta', 'rapida'),
    ]
    reglas = [ctrl.Rule(temperatura[t] & humedad[h], velocidad[v],
                       label=f'R{i}')
              for i, (t, h, v) in enumerate(tabla, start=1)]
    return ctrl.ControlSystem(reglas), temperatura, humedad, velocidad, tabla


def evaluar(sistema, temperatura, humedad):
    for nombre, valor, limite in [('Temperatura', temperatura, 40),
                                  ('Humedad', humedad, 100)]:
        if not math.isfinite(valor) or not 0 <= valor <= limite:
            raise ValueError(f'{nombre}: ingresa un número entre 0 y {limite}.')
    simulacion = ctrl.ControlSystemSimulation(sistema, clip_to_bounds=False)
    simulacion.input['temperatura'] = temperatura
    simulacion.input['humedad'] = humedad
    simulacion.compute()
    return float(simulacion.output['velocidad']), simulacion


def leer_numero(mensaje, limite):
    while True:
        texto = input(mensaje).strip().replace(',', '.')
        if texto.lower() in ('salir', 'q'):
            raise EOFError
        try:
            numero = float(texto)
            if math.isfinite(numero) and 0 <= numero <= limite:
                return numero
        except ValueError:
            pass
        print(f'Entrada inválida. Usa un número entre 0 y {limite}.')


def explicar_reglas(temperatura, humedad, tabla, t, h):
    print('Reglas activadas (AND = mínimo de las pertenencias):')
    for i, (ct, ch, salida) in enumerate(tabla, start=1):
        mt = fuzz.interp_membership(temperatura.universe, temperatura[ct].mf, t)
        mh = fuzz.interp_membership(humedad.universe, humedad[ch].mf, h)
        activacion = min(mt, mh)
        if activacion > 0:
            print(f'  R{i}: temperatura {ct} Y humedad {ch} -> '
                  f'velocidad {salida}; activación = {activacion:.3f}')


def guardar_graficas(variables, simulacion, carpeta):
    import matplotlib
    matplotlib.use('Agg')  # También funciona sin interfaz gráfica.
    import matplotlib.pyplot as plt

    fig, ejes = plt.subplots(3, 1, figsize=(9, 10))
    unidades = ['Temperatura (°C)', 'Humedad relativa (%)', 'Velocidad (%)']
    for variable, eje, unidad in zip(variables, ejes, unidades):
        for etiqueta, termino in variable.terms.items():
            eje.plot(variable.universe, termino.mf, label=etiqueta, linewidth=2)
        eje.set(xlabel=unidad, ylabel='Pertenencia', ylim=(-0.05, 1.05))
        eje.legend()
        eje.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(carpeta / 'pertenencias.png', dpi=160)
    plt.close(fig)
    variables[2].view(sim=simulacion)
    plt.gcf().savefig(carpeta / 'ultima_inferencia.png', dpi=160,
                      bbox_inches='tight')
    plt.close('all')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--demo', action='store_true', help='Ejecutar cinco casos.')
    parser.add_argument('--sin-graficas', action='store_true')
    args = parser.parse_args()
    sistema, temperatura, humedad, velocidad, tabla = crear_sistema()
    carpeta = Path(__file__).resolve().parent / 'resultados'
    carpeta.mkdir(exist_ok=True)
    resultados = []
    ultima_simulacion = None
    print('CONTROL DIFUSO DEL VENTILADOR — Modelo educativo Mamdani')
    print('Entradas: 0–40 °C y 0–100 % de humedad. Salida: velocidad 0–100 %.')
    print('Escribe salir para terminar. No controla un dispositivo físico.\n')
    casos = iter([(10, 20), (20, 40), (25, 50), (30, 65), (38, 90)])
    try:
        while True:
            if args.demo:
                caso = next(casos, None)
                if caso is None:
                    break
                t, h = caso
            else:
                t = leer_numero('Temperatura (°C): ', 40)
                h = leer_numero('Humedad (%): ', 100)
            resultado, ultima_simulacion = evaluar(sistema, t, h)
            print(f'\n{t:g} °C | {h:g} % humedad -> velocidad {resultado:.2f} %')
            explicar_reglas(temperatura, humedad, tabla, t, h)
            resultados.append([t, h, round(resultado, 4)])
            print()
    except (EOFError, KeyboardInterrupt):
        print('\nFin de la sesión.')
    if resultados:
        with (carpeta / 'casos.csv').open('w', newline='', encoding='utf-8') as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(['temperatura_c', 'humedad_pct', 'velocidad_pct'])
            escritor.writerows(resultados)
        if not args.sin_graficas:
            guardar_graficas((temperatura, humedad, velocidad), ultima_simulacion, carpeta)
        print(f'Resultados guardados en: {carpeta}')
        print('Los archivos se reemplazan al ejecutar una nueva sesión.')


if __name__ == '__main__':
    main()
