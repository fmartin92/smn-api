import unidecode
import copy

class Estacion:
    def __init__(self, params):
        (self.nombre, self.provincia, self.oaci, self.latitud_gr,
         self.latitud_min, self.longitud_gr, self.longitud_min,
         self.altura, self.numero) = params

with open('estaciones_smn.txt') as f:
    datos_estaciones = f.read().split('\n')[:-1]

estaciones = []

for estacion in datos_estaciones:
    nombre = estacion[:31].rstrip()
    provincia = estacion[31:68].rstrip()
    resto_de_datos = estacion[67:].split()
    oaci = resto_de_datos.pop()
    datos_numericos = [int(dato) for dato in resto_de_datos]
    estaciones.append(Estacion([nombre, provincia, oaci] + datos_numericos))

nombres_de_estaciones = [estacion.nombre for estacion in estaciones]

def estacion_por_nombre(nombre):
    nombre = unidecode.unidecode(nombre).upper()
    if nombre in nombres_de_estaciones:
        return copy.deepcopy(estaciones[nombres_de_estaciones.index(nombre)])
    nombre += ' AERO'
    if nombre in nombres_de_estaciones:
        return copy.deepcopy(estaciones[nombres_de_estaciones.index(nombre)])
    else:
        raise ValueError
