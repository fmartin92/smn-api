import requests
import zipfile
import io
import datetime
import json
from dataclasses import dataclass

CALMA_STR = 'Calma'
URL_DESCARGA = 'https://ssl.smn.gob.ar/dpd/zipopendata.php?dato='
PARAM_TIEMPO = 'tiepre'
PARAM_PRONOSTICO = 'pron5d'
TEXT_ENCODING = 'latin-1'

@dataclass
class Tiempo:
    fecha_hora: datetime.datetime
    estado: str
    visibilidad: str
    temperatura: float
    termica: float
    humedad: int
    viento_dir: str
    viento_vel: int
    presion: float

@dataclass
class Pronostico:
    fecha_hora: datetime.datetime
    temperatura: float
    viento_dir: int
    viento_vel: int
    precipitacion: float

meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio',
        'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
meses_pronostico = [mes[:3].upper() for mes in meses]

def descargar_datos(param):
    r = requests.get(URL_DESCARGA + param)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    nombre = z.namelist()[0]
    return list(io.TextIOWrapper(z.open(nombre), TEXT_ENCODING))

def jsonificar(objeto):
    return json.JSONEncoder().encode({
        k : v.isoformat() if type(v) == datetime.datetime else v
        for (k, v) in objeto.__dict__.items()
    })

def dict_a_json(dic):
    if dic:
        resultado = '{'
        for (k, v) in dic.items():
            resultado += '"' + k + '": ' + v + ', '
        return resultado[:-2] + '}'
    return '{}'

def tiempo_actual():
    data = [renglon.lstrip().rstrip()[:-2].split(';') for renglon
                in descargar_datos(PARAM_TIEMPO)]
    tiempo = {}
    for linea in data:
        estacion = linea[0]
        (dia, mes, anno) = linea[1].split('-')
        (hora, minuto) = [int(n) for n in linea[2].split(':')]
        fecha_hora = datetime.datetime(int(anno), meses.index(mes) + 1,
                                        int(dia), hora, minuto)
        estado = linea[3]
        visibilidad = linea[4]
        temperatura = float(linea[5])
        try:
            termica = float(linea[6])
        except:
            termica = None
        humedad = int(linea[7])
        if linea[8] == CALMA_STR:
            (viento_dir, viento_vel) = (CALMA_STR, 0)
        else:
            viento_vel = linea[8].split()[-1]
            viento_dir = linea[8][:-len(viento_vel)].rstrip()
            viento_vel = int(viento_vel)
        presion = float(linea[9])
        tiempo[estacion] = Tiempo(fecha_hora, estado, visibilidad,
                            temperatura, termica, humedad, viento_dir,
                            viento_vel, presion)
    return tiempo

def pronostico():
    data = descargar_datos(PARAM_PRONOSTICO)[5:]
    linea = 0
    pronosticos = {}
    while linea < len(data)-1:
        estacion = data[linea].lstrip().rstrip()
        linea += 5
        pronostico_estacion = []
        for i in range(40):
            datos = data[linea].split()
            (dia, mes, anno) = datos[0].split('/')
            fecha_hora = datetime.datetime(int(anno),
                                        meses_pronostico.index(mes),
                                        int(dia), int(datos[1][:2]))
            temperatura = float(datos[2])
            viento_dir = int(datos[3])
            viento_vel = int(datos[5])
            precipitacion = float(datos[6])
            pronostico_estacion.append(Pronostico(fecha_hora, temperatura,
                                                    viento_dir, viento_vel,
                                                    precipitacion))
            linea += 1
        pronosticos[estacion] = pronostico_estacion
        linea += 1
    return pronosticos

def tiempo_actual_json():
    tiempo = tiempo_actual()
    return dict_a_json({k : jsonificar(v) for (k, v) in tiempo.items()})

def pronostico_json():
    datos_pronostico = pronostico()
    return dict_a_json({k : '['+', '.join([jsonificar(i) for i in v])+']'
                                for (k, v) in datos_pronostico.items()})
