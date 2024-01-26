""""
Este arquivo tem como finalidade servir de exemplo de algumas queries
SQL para analise ou transformação caso o desenvolvedor não saiba usar a
linguagem python. Para usa-lo nos notebooks do databricks é necessário
fazer as devidas alterações.
"""

from pyspark.sql import SparkSession

# Mude para o path da camada bronze após fazer o mount do blob storage.
silver_location = "/mnt/<mount-name>/<path-to-silver-layer>"

# Mude para o path da camada Silver
gold_location = "/mnt/delta/<path-to-gold-layer>"

spark = SparkSession.builder \
        .appName("Silver Layer data manipulation") \
        .getOrCreate()

df = spark.read.json(silver_location)

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

# Também é possível salvar como streaming como indicado na documentação.
df.write.format("delta").save(gold_location)