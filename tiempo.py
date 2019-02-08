import requests
import zipfile
import io
#import estaciones

class Estado_del_tiempo:
    #horrible, usar @dataclass
    def __init__(self, params):
        (self.estacion, self.fecha, self.hora, self.estado, self.visibilidad,
         self.temperatura, self.termica, self.humedad, self.viento_dir,
         self.viento_vel, self.presion) = params
    
#todo: error handling si no hay internet
def tiempo_actual():
    r = requests.get('https://ssl.smn.gob.ar/dpd/zipopendata.php?dato=tiepre')
    z = zipfile.ZipFile(io.BytesIO(r.content))
    nombre = z.namelist()[0]
    data = list(io.TextIOWrapper(z.open(nombre), 'latin-1'))
    data = [renglon.lstrip().rstrip()[:-2].split(';') for renglon in data]
    datos = []
    for linea in data:
        estacion = linea[0]
        fecha = linea[1]
        hora = linea[2]
        estado = linea[3]
        visibilidad = linea[4]
        temperatura = float(linea[5])
        termica = None if linea[6] == 'No se calcula' else float(linea[6])
        humedad = int(linea[7])
        if linea[8] == 'Calma':
            (viento_dir, viento_vel) = ('Calma', 0)
        else:
            (viento_dir, viento_vel) = linea[8].split()
            viento_vel = int(viento_vel)
        presion = float(linea[9])
        datos.append(Estado_del_tiempo([estacion, fecha, hora, estado,
                                        visibilidad, temperatura, termica,
                                        humedad, viento_dir, viento_vel,
                                        presion]))
    return datos

def tiempo_actual_en(ciudad):
    datos = tiempo_actual()
    estaciones = [dato.estacion for dato in datos]
    return datos[estaciones.index(ciudad)]
