# Lentigob Splink

En este repositorio se pueden encontrar pruebas de exploración de la biblioteca de _linkeo_ o vinculación de registros 
(_data linkeage_ ó _record linkeage_) [_SPlink_](https://github.com/moj-analytical-services/splink). Esta biblioteca es 
de código abierto y como bien lo indica la propia
documentación de la misma, ésta permite deduplicar y vinculación de registros en conjuntos de datos.

El objetivo de esta exploración es evaluar la infraestructura de la biblioteca para integrar nuevas funcionalidades 
customizadas, como por ejemplo reglas de agrupamiento y comparación, así como entender bajo que metodología la 
biblioteca lleva a cabo la vinculación de registros.

## Uso

### Organización del repositorio

- En el directorio `exploracion` se pueden encontrar los archivos `.ipynb` donde se hizo la exploración de la biblioteca usando conjuntos de datos de salud proporcionados por personal del INER*. 
- En el directorio `splink` se encuentra el fork de la biblioteca original de _SPlink_ donde se agregaron las funcionalidades customizadas.

*Por razones de privacidad y seguridad los conjuntos de datos usados en esta exploración no se agregaron a este 
repositorio. Para poder reproducir los resultados es necesario solicitar los conjuntos de datos al personal del INER.

```bash
lentigob-splink/
├── exploracion/
│   ├── pyproject.toml                               # TOML para instalación idependiente
│   ├── comorbilidad_prueba.ipynb                    # Pruebas sobre un conjunto de datos de comorbilidades de pacientes de COVID-19
│   ├── costos_pacientes_prueba.ipynb                # Pruebas sobre un conjunto de datos de costos de atención de pacientes de COVID-19
│   └── trabajo_social.ipynb                         # Pruebas sobre un conjunto de datos socioeconómicos y demográficos de pacientes de COVID-19
    └── data/                                        # Carpeta donde se depositan los conjuntos de datos (CSV). Se mantiene en la estructura para claridad de la usuaria.
└── splink/                                          # Se muestran aquí solamente los scripts de interés para customizar la biblioteca. Para la arquitectura completa, consultar la documentación de SPlink
│   ├── pyproject.toml                               # TOML original de SPlink
│   ├── README.md                                    # Documentación original de SPlink
    └── splink/
        └── internals/
            ├── blocking_rule_library.py             # Script original de reglas de agrupamiento
            ├── blocking_rule_library_custom.py      # Script customizado de reglas de agrupamiento
            ├── comparison_level_library.py          # Script original de reglas de comparación
            └── comparison_level_library_custom.py   # Script customizado de reglas de comparación
└── README.md                                        # El presente archivo y documentación de este repositorio
```

### Instalación, requerimientos y uso

Se recomienda tratar los dos directorios principales de este repostorio (`exploracion` y `splink`) como dos ambientes de 
Python distintos e instalar de manera independiente dentro de cada directorio. Para esta finalidad se conserva el `pyproject.toml`
original de SPlink en la carpeta `splink` y se incluye otro `pyproject.toml` para la carpeta `exploracion`.

**A. Para `exploracion`**

#### Requerimientos
- [Python >=3.10.0](https://www.python.org/downloads/release/python-3100/)
- [Jupyter >=1.0.0](https://jupyter.org/)
- [SPlink 4.0.16](https://github.com/moj-analytical-services/splink)
- [Pandas >=2.0.0](https://pandas.pydata.org/)
- [DuckDB >=0.10.0](https://duckdb.org/docs/current/)

#### Instalación

Como se mencionó antes, se proporciona el `pyproject.toml` para hacer una instalación de los requerimientos para correr 
los _notebooks_ de exploración de SPlink. Se puede usar la herramienta de manejo de ambientes virtuales que la usuaria
elija. Aquí se dan las instrucciones usando [`uv`](https://docs.astral.sh/uv/) para instalar los requerimientos y 
crear el ambiente virtual.

Ejecutar en una terminal dentro de la carpeta `exploración`:

1. Instalación y creación del ambiente virtual `.venv/`
```bash
uv sync
```

2. Activar el ambiente virtual
```bash
source .venv/bin/activate
```

3. Registro del ambiente virtual en el kernel local de _Jupyter_
```bash
python -m ipykernel install --user --name=splink-project --display-name "Python (splink-exploracion)"
```

4. Levantar localmente `Jupyter notebook`
```bash
jupyter notebook
```

Con este último paso se abre en una ventana del navegador el ambiente de _Jupyter_

Cada vez que se quiera volver a trabajar con los _notebooks_ de exploración es necesario abrir una terminal y ejecutar 
los pasos 2 y 4, es decir, activar el ambiente virtual de Python y levantar localmente el servidor de _Jupyter_.

Dentro de cada _notebook_ se pueden encontrar anotaciones y observaciones sobre cada módulo de SPlink en contexto con 
los conjuntos de datos usados para la exploración.

**B. Para `splink`**

#### Requerimientos

#### Instalación

### Funciones customizadas en _SPlink_

## Breve resumen de _SPlink_

## Conclusiones