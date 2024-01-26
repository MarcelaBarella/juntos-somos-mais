""""
Este arquivo tem como finalidade servir de exemplo de algumas
transformações que podem ser feitas nos dados da camada bronze
para que sejam persistidos na camada Silver, para efetivamente
utilizar esse código é necessário fazer as alterações de leitura
e escrita para os notebooks no databricks.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import (isnan, 
                                   when, 
                                   count, 
                                   col,
                                   round)
from pyspark.sql.types import IntegerType

# Mude para o path da camada bronze após fazer o mount do blob storage.
bronze_location = "/mnt/<mount-name>/<path-to-bronze-layer>"

# Mude para o path da camada Silver
silver_location = "/mnt/delta/<path-to-silver-layer>"

spark = SparkSession.builder \
        .appName("Bronze layer data manipulation") \
        .getOrCreate()

df = spark.read.json(bronze_location)

# Verifica e mostra se existem transações duplicadas.
df \
    .groupby(df.columns) \
    .count() \
    .where("count > 1") \
    .sort("count", ascending=False) \
    .show()

# Foram encontradas 5200 duplicações no momento de criação do código.

# Para remover as duplicações.
df = df.dropDuplicates()

# Normalizando colunas que estejam vazias.
df = df.na.fill({"Price": 0, "Quantity": 0})
df = df.na.fill({"Location": "Unknown"})

# Verifica e mostra se existem valores faltantes no df.
df.select([count(when(isnan(c), c)).alias(c) for c in df.columns]).show()
# Não foram encontrados valores faltantes.

# Fazendo casting de Quantity de string para integer.
df_with_int_quantity = df.withColumn("Quantity", col("Quantity").cast(IntegerType()))

# Filtrando transações não canceladas por valores negativos.
df = df.filter(col("Quantity") > 0)

# Após filtrar é possível por exemplo quantificar o total de vendas.
df = df.withColumn("TotalSalesAmount", round(col("Quantity") * col("Price"), 2))
df = df.na.fill({"TotalSalesAmount": 0})

df = df.join(df, "ProductID")

# Também é possível salvar como streaming como indicado na documentação.
df.write.format("delta").save(silver_location)