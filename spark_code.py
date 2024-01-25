""""
Este arquivo tem como finalidade apresentar exemplos de limpeza, 
transformação e analíses que posem ser feitas nos dados da camada
bronze, sendo possível utilizar os notebooks do databricks para
testar os códigos a seguir após fazer as devidas alteraçoes para a
leitura da camada bronze.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import (isnan, 
                                   when, 
                                   count, 
                                   col,
                                   round)
from pyspark.sql.types import IntegerType


bronze_location = "/path/to/bronze/directory"

spark = SparkSession.builder \
        .appName("Bronze layer data manipulation") \
        .getOrCreate()

df = spark.read.csv(bronze_location, header=True, inferSchema=True)

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

# 
total_sales_per_product = df.groupBy("ProductNo").agg(
    round(sum("TotalSalesAmount"), 2).alias("TotalSales"))

# Também é possível fazer certas analises/transformações usando SQL
# Crie uma view para rodar as queires
df.createOrReplaceTempView("transactions")

# Use o spark sql e a query como parametro
# Query produtos unicos.
unique_products = spark.sql("SELECT COUNT(DISTINCT ProductNo) AS UniqueProducts FROM transactions")

# Query clientes unicos.
unique_customers = spark.sql("SELECT COUNT(DISTINCT CustomerID) AS UniqueCustomers FROM transactions")

# Query cancelamentos.
query = """
SELECT
    ROUND(SUM(ABS(Quantity) * Price), 2) AS TotalCancellationValue,
    SUM(ABS(Quantity)) AS TotalCancellationQuantity
FROM
    transactions
WHERE
    Quantity < 0
"""
cancellation_stats = spark.sql(query)