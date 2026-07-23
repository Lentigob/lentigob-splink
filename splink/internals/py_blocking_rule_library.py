"""
py_blocking_rule_library.py

Módulo complementario a splink.blocking_rule_library, para reglas de
bloqueo definidas por la usuaria con lógica escrita en Python.

NOTA: Splink siempre ejecuta las reglas de bloqueo como SQL contra DuckDB
(u otro backend elegido por la usuaria). Este módulo no sustituye lo anterior, sólo
ofrece dos formas de conectar la lógica de Python con ese requisito.

Modo "pandas" (recomendada):
    Se aplica la función de Python una vez sobre todo el DataFrame y
    se crea una columna nueva ya normalizada, y la regla de bloqueo
    resultante es una simple igualdad SQL sobre esa columna. Esta opción es más rápida y
    es mejor usarla en conjuntos de datos medianos/grandes.

Modo "FDU (Función Definida por la Usuaria)":
    La función de Python se registra como User Defined Function (Función Definida por la Usuaria)
    dentro de la conexión de DuckDB, y la regla de bloqueo la
    llama directamente en SQL. Es más flexible, pues no requiere modificar el DataFrame de antemano, pero
    es más lenta porque DuckDB llama a Python fila por fila. Es mejor para conjuntos de datos pequeños.

Uso:
    # Modo pandas
    from blocking_rule_library_py import block_on_sin_acentos

    df, regla = block_on_sin_acentos(df, "nombre")
    settings = SettingsCreator(
        blocking_rules_to_generate_predictions=[regla],
        ...
    )
    linker = Linker(df, settings, db_api=DuckDBAPI())

    # Modalidad FDU
    from blocking_rule_library_py import registrar_fdu_sin_acentos
    import duckdb

    con = duckdb.connect("mi_bd.duckdb")
    regla = registrar_fdu_sin_acentos(con, "nombre")
    settings = SettingsCreator(
        blocking_rules_to_generate_predictions=[regla],
        ...
    )
    linker = Linker("personas", settings, db_api=DuckDBAPI(connection=con))
"""

import unicodedata
import pandas as pd


# ---------------------------------------------------------------------
# Lógica base compartida por ambas modalidades
# ---------------------------------------------------------------------

def quitar_acentos(texto):
    """
    Quita acentos y diacríticos de un string.
    Compatible tanto con pandas (.apply) como con DuckDB (create_function),
    ya que solo recibe y regresa un valor escalar.
    """
    if texto is None or (isinstance(texto, float) and pd.isna(texto)):
        return texto
    texto = str(texto)
    texto_normalizado = unicodedata.normalize('NFKD', texto)
    return ''.join(c for c in texto_normalizado if not unicodedata.combining(c))


def _normalizar_serie(serie):
    """Aplica quitar_acentos + mayúsculas + strip a una columna de pandas."""
    return (
        serie.apply(quitar_acentos)
        .str.upper()
        .str.strip()
    )


# ---------------------------------------------------------------------
# MODALIDAD 1: pandas (precálculo)
# ---------------------------------------------------------------------

def block_on_sin_acentos(df, columna):
    """
    Crea una columna '{columna}_sin_acentos' en el DataFrame (normalizada:
    sin acentos, en mayúsculas, sin espacios extra) y regresa la regla de
    bloqueo SQL correspondiente.

    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame con la columna a normalizar.
    columna : str
        Nombre de la columna original (ej. 'nombre').

    Regresa
    -------
    (df_transformado, regla_sql) : tuple[pd.DataFrame, str]
    """
    df = df.copy()
    col_nueva = f"{columna}_sin_acentos"
    df[col_nueva] = _normalizar_serie(df[columna])

    regla_sql = f"l.{col_nueva} = r.{col_nueva}"
    return df, regla_sql


# ---------------------------------------------------------------------
# Modo 2: FDU en DuckDB
# ---------------------------------------------------------------------

def registrar_fdu_sin_acentos(con, columna, nombre_fdu="quitar_acentos_fdu"):
    """
    Registra quitar_acentos como FDU en la conexión de DuckDB dada,
    y regresa la regla de bloqueo SQL que la usa.

    Parámetros
    ----------
    con : duckdb.DuckDBPyConnection
        Conexión activa de DuckDB (la misma que usarás en DuckDBAPI(connection=con)).
    columna : str
        Nombre de la columna sobre la que se aplicará la fdu (ej. 'nombre').
    nombre_fdu : str
        Nombre que tendrá la función dentro de DuckDB. Cambialo si ya
        existe una función con ese nombre en tu conexión.

    Regresa
    -------
    regla_sql : str
    """
    # evitar registrar dos veces la misma FDU si ya existe
    funciones_existentes = con.execute(
        "SELECT function_name FROM duckdb_functions() WHERE function_name = ?",
        [nombre_fdu],
    ).fetchall()

    if not funciones_existentes:
        con.create_function(nombre_fdu, quitar_acentos, [str], str)

    regla_sql = f"UPPER({nombre_fdu}(l.{columna})) = UPPER({nombre_fdu}(r.{columna}))"
    return regla_sql


# ---------------------------------------------------------------------
# Selector único: el usuario elige la modalidad
# ---------------------------------------------------------------------

def get_regla_bloqueo_sin_acentos(columna, modo="pandas", df=None, con=None):
    """
    Punto de entrada único: según 'modo', arma la regla de bloqueo
    usando la modalidad pandas o fdu.

    Parámetros
    ----------
    columna : str
        Columna a normalizar (ej. 'nombre').
    modo : str
        'pandas' o 'fdu'.
    df : pd.DataFrame, requerido si modo='pandas'.
    con : duckdb.DuckDBPyConnection, requerido si modo='fdu'.

    Regresa
    -------
    Si modo='pandas': (df_transformado, regla_sql)
    Si modo='fdu': regla_sql
    """
    if modo == "pandas":
        if df is None:
            raise ValueError("modo='pandas' requiere pasar el DataFrame en 'df'.")
        return block_on_sin_acentos(df, columna)

    elif modo == "fdu":
        if con is None:
            raise ValueError("modo='fdu' requiere pasar la conexión de DuckDB en 'con'.")
        return registrar_fdu_sin_acentos(con, columna)

    else:
        raise ValueError(f"modo debe ser 'pandas' o 'fdu', recibido: '{modo}'")


# ---------------------------------------------------------------------
# Ejemplo de uso
# ---------------------------------------------------------------------

if __name__ == "__main__":
    import duckdb
    from splink import Linker, SettingsCreator, DuckDBAPI
    import splink.comparison_library as cl

    data = {
        "unique_id": [1, 2, 3, 4],
        "nombre": ["José Pérez", "jose perez", "María López", "Ana Ruiz"],
    }
    df = pd.DataFrame(data)

    # --- Modalidad pandas ---
    df_norm, regla_pandas = get_regla_bloqueo_sin_acentos(
        "nombre", modo="pandas", df=df
    )
    print("Regla (pandas):", regla_pandas)
    print(df_norm)

    settings_pandas = SettingsCreator(
        link_type="dedupe_only",
        blocking_rules_to_generate_predictions=[regla_pandas],
        comparisons=[cl.ExactMatch("nombre")],
    )
    linker_pandas = Linker(df_norm, settings_pandas, db_api=DuckDBAPI())
    print(linker_pandas.inference.predict().as_pandas_dataframe())

    # --- Modalidad FDU ---
    con = duckdb.connect(":memory:")
    con.execute("CREATE TABLE personas AS SELECT * FROM df")

    regla_fdu = get_regla_bloqueo_sin_acentos("nombre", modo="fdu", con=con)
    print("Regla (fdu):", regla_fdu)

    settings_fdu = SettingsCreator(
        link_type="dedupe_only",
        blocking_rules_to_generate_predictions=[regla_fdu],
        comparisons=[cl.ExactMatch("nombre")],
    )
    linker_fdu = Linker("personas", settings_fdu, db_api=DuckDBAPI(connection=con))
    print(linker_fdu.inference.predict().as_pandas_dataframe())