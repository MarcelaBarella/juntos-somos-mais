# Data Pipeline Juntos Somos Mais

## Lista de Ferramentas
* [Apache Airflow](https://airflow.apache.org/)
* [Apache Kafka](https://kafka.apache.org/)
* [Apache Spark](https://spark.apache.org/)
* [Azure Blob Storage](https://azure.microsoft.com/en-us/products/storage/blobs)
* [Azure Delta Lake](https://learn.microsoft.com/pt-br/azure/synapse-analytics/spark/apache-spark-what-is-delta-lake)
* [Azurre Delta Live Tables](https://learn.microsoft.com/en-us/azure/databricks/delta-live-tables/)
* [Databricks](https://www.databricks.com/)
* [Power BI](https://learn.microsoft.com/pt-br/power-bi/fundamentals/power-bi-overview)

## Decisões arquiteturais
### Arquiteturas Lakehouse e Medallion
As arquiteturas escolhidas para esta solução são a [Lakehouse](https://www.databricks.com/br/glossary/data-lakehouse) e a [Meddalion](https://www.databricks.com/br/glossary/medallion-architecture) motivado pelo fato de que o time de dados já conta com o uso do Databricks, que consequentemente tem ambas arquiteturas nativas.
A arquitetura Lakehouse é uma combinação das arquiteturas [Data Warehouse](https://azure.microsoft.com/pt-br/resources/cloud-computing-dictionary/what-is-a-data-warehouse) e [Data Lake](https://azure.microsoft.com/pt-br/resources/cloud-computing-dictionary/what-is-a-data-lake) visando oferecer vantagens referentes a ambas arquiteruras, ou seja, capacidade de gerenciamento e desempenho robustas e armazenamento em grande escala consequentemente. 

Neste tipo de arquitetura o armazenamento é unificado, pode se armazenar tanto dados estruturados quanto não estruturados num único repositório em grandes volumes sem perder a escalabilidade e flexibilidade, e as consultas aos mesmos é otimizada de forma a proporcionar respostas rápidas. Também conta com uma camada de segurança e governança de dados que preenche lacunas existentes nas arquiteturas que dão origem quando consideradas individualmente. Com essas caracteristicas as vantagens que essa arquitetura fornece são facilidade de manutenção por conta da infraestrutura reduzida, reduz o numero de silos, permite analises em real time e e pode ser mais econômica que outras opções de armazenamento dependendo do caso.

A arquitetura medallion é uma estratégia de organização de dados frequentemente utilizada com Databricks projetada de forma a o tornar mais eficiente e otimizar os fluxos dos dados. Ela é composta por três diferentes camadas de armazenamento que possuem diferentes níveis de processamento dos dados afim de servir a diferentes propósitos sendo essas camadas Bronze, Prata e Ouro. Dentre as vantagens em usar este tipo de arquitetura estão a flexibilidade de integração com novas fontes de dados e adaptações para atender demandas de negocios, melhoria continua da qualidade de dados devido a estrutura de camadas e facilidade na implementação de padrões de governança de dados.

### Ingestão
A ferramenta escolhida para fazer a ingestão de dados é o Apache Kafka pois é uma ferramenta robusta que oferece várias vantagens técnicas nesta implementação. O Kafka é capaz de processar mensagens em streaming com baixa latência e alto throughput, apresenta um sistema distribuído que facilita seu escalonamento horinzontal adicionando mais clusters em casos de aumento no número de pedidos como por exemplo Black Friday e a replicação de clusters também proporciona tolerancia a falhas.
A integração do Kafka também foi considerada em relação as ferramentas de processamento usadas e possíveis novas ferramentas e linguagens que possam futuramente vir a ser adotadas.
Por fim seu gerenciamento de grandes volumes de dados e integração com padrões de arquitetura event driven e ampla comunidade tornam uma ferramenta de interessante adoção para um ecommerce.

### Processamento
O processamento dos dados pode ser feitos em diferentes camadas conforme a necessidade. Considerando que o time de dados já possuí um Databricks na Azure é pertinente manter o processamento dentro dele já que utilizar outras ferramentas incluiria considerar a possível curva de aprendizado dos membros do time, que demanda tempo, além de possíveis novos custos e afins.
A ferramenta utilizada para processar e transformar os dados será o Apache Spark do Databricks já que esta ferramenta realiza o processamento de dados de forma distribuída e além disso é de fácil integração com o Kafka e com a Azure. Junto ao Apache Spark pode ser utilizado o PySpark do Python para realizar o processamento per se pois possui uma variedade grande de libs de processamento, mas caso a equipe se sinta mais confortavel também é possível usar o Scala no Databricks.

#### Camada Streaming
Esta camada fará o processamento inicial dos dados, ou seja, limpeza, transformações e consolidações.
Para a limpeza dos dados recomenda-se considerar:
* Identificar valores faltantes.
* Remover dados duplicados para garantir unicidade destes (considerando contextos em que não faça sentido haver duplicidade).
* Corrigir typos, valores incorretos e outros possíveis erros.

Para transformação dos dados recomenda-se considerar:
* Normalizar os dados de forma que todos dados de uma determinada coluna possuam a mesma unidade de medida, como por exemplo todos os itens da coluna Price com libras como moeda.
* Converter valores Date Time de forma que todos possuam a mesma formatação.
* Converter os dados categóricos numa mesma formatação, como por exemplo todos ProductNo contendo 5 ou 6 digitos unicos.

Caso futuramente ocorra a necessidade de integrar os dados de pedidos com dados ingeridos de fontes diferentes, realize os processamentos anteriormente citados e/ou que sejam resolvidas quaisquer incossistencias para que durante o "merge" desses dados/data frames as informações se mantenham consistentes entre si em termos de formatos e afins.

### Armazenamento
#### Camada Bronze
Considerando o cenário de um ecommerce onde ocorram váriações de preço segundo certas demandas, analise de vendas, construção de modelos de recomendação, auditorias e afins, uma camada bronze se faz pertinente uma vez que comporta dados de todo tipo de pedido e que essas informações podem ser remodeladas em etapas posteriores para seu melhor uso e como confiavel source of thruth. Além disso a construção dessa camada visa evitar o retrabalho total da etapa de ingestão caso sejam necessárias alterações no processamento.
A ferramenta sugerida para armazenamento dos dados brutos é o Azure Blob Storage devido a eficiência que proporciona a solução. Essa ferramenta se integra fácilmente com o Databricks que fará o processamento dos dados, é otimizado para o armazenamento de um grande volume de dados sendo mais econômico, possui redundância de dados em multiplos locais geograficos oque consequentemente o torna mais resiliente e torna mais robusta a recuperação e escalabilidade do uso dos dados e afins.

#### Camada Silver
Nesta camada serão armazenados os dados limpos, normalizados e consolidados. Considerando o cenário de um ecommerce, onde diferentes tipos de analises e construção, por exemplo, de modelos de precificação e recomendação que podem ser feitos posteriormente, além de questões de complience e regulamentação de dados como a LGPD dentre outros benefícios a criação de uma camada de armazenamento Silver se faz pertinente.
A ferramenta escolhida para o armazenamento dos dados desta camada são as [Delta Live Tables](https://docs.databricks.com/pt/delta-live-tables/index.html) e Delta Lake do Databricks, tornando a curva de aprendizado e integração ferramental menor. Outros motivos para a escolha dessa ferramenta é que a integridade dos dados especialmente sendo real time pode ser garantida pois oferece o uso de transações [ACID](https://www.databricks.com/br/glossary/acid-transactions), ela também oferece leitura e escrita otimizadas e consequentemente desempenho e escalabilidade, controle de versão e snapshots time travel e por consequencia facilidade na auditoria de dados e em analises históricas.

#### Camada Gold
Nesta camada serão armazenados dados limpos e sumarizados otimizados para leitura (menos normalizações e agregações feitas de modo a atender demandas mais específicas) pois é utilizada para obtenção de insights de forma clara e rápida voltadas a questões de negócios. O armazenamento da camada gold será feito da mesma forma ao que foi feito na camada Silver.

### Análise/Visualização de Dados:
A ferramenta escolhida é o Power BI, que é uma ferramenta robusta por que oferece uma variedade grande de opções para criação e visualização de relatórios e de integração nativa com a Azure. Outros motivos para sua escolha incluem a facilidade de uso e consequente autonomia que porprociona devido a sua interface, oque torna acessível para membros não tech da equipe, a governança de dados também é facilitada por ele, ou seja, permissões de acesso de determinados dashboards a determinadas pessoas, que é importante pois o compartilhamento desses dashboards também é facilitado.

### Orquestramento
Mesmo se tratando de uma pipeline em real time, o orquestramento das etapas é importante pois garante a integridade do processo e facilita o monitoramento, já que pode indicar em qual etapa do workflow ocorreu o erro com mais facilidade do que procurar o erro individualmente até achar a parte problematica. Em termos de escalabilidade o orquestrador pode reajustar recursos computacionais conforme necessário e dentre outras vantagens também inclui automatização de rotinas facilita a documentação da pipeline como um todo.
A ferramenta utilizada para o orquestramento é o Apache Airflow que orquestra workflows através de [DAGs](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html) escritas em Python, sendo estas fácilmente escalaveis conforme o aumento no volume de dados, tarefas e workflows. Além disso ele contruibuí com as vantagens de orquestar uma solução mesmo que esta seja real time já que facilita o gerencimento de dependencias, permite configurar politicas de retry e agendamentos complexos, fácil integração com outras ferramentas adotadas como o Databricks e Kafka dentre outros.

## Guia de implementação
### Ingestão
Os campos que dizem respeito as informações do pedido enviados pelos producers serão:
1. TransactionNo (categoria): um campo de valor numérico único para cada transação. A letra "C" no código indica um pedido cancelado.
2. Date (string): a data em que foi gerada cada transação.
3. ProductNo (categoria): um número de cinco ou seis digitos com caracteres únicos utilizado para identificar um produto específico.
4. Product (categoria): nome do item/produto.
5. Price (numerico): preço unitario de cada produto em libras esterlinas (£).
6. Quantity (numerico): a quantidade de cada produto por transação. Valores negativos dizem respeito a transações canceladas.
7. CustomerNo (categoria): um número único de cinco digitos que define cada cliente.
8. Country (categoria): o nome do país onde o cliente reside.

Para fazer a ingestão de dados siga os seguintes passos:
1. Primeiro passo é definir um tópico, no caso o tópico sugerido é o intuitivamente: **Pedidos**. Os tópicos podem ser particionados e replicados para lidar com um maior numero de pedidos em situações de aumento de demanda, diferentes publishers, já que o processo poderia ser paralelizado e também aumentaria a resistencia a possíveis falhas caso uma das replicas falhasse ou algo parecido.

2. Serão então definidos os producers que são os responsáveis por assinar os tópicos e enviar as mensagens (neste caso os detalhes dos pedidos) para eles para que possam ser posteriormente processados. Para o formato de mensagem será usado o JSON pois além de mais comum, é fácil de processar já que pode ser organizado em key-value.
{
  "TransactionNo": "581482",
  "Date": "12/9/2019",
  "ProductNo": "22485",
  "Product": "Bull Dog Bottle Opener",
  "Price": 19.99,
  "Quantity": 2,
  "CustomerNo": "54321",
  "Country": "United Kingdom"
}
Esse modelo é bem básico considerando os campos referentes ao pedido, porém, podem ser futuramente alterados para comportar novos valores e organicações.

3. Durante a configuração dos clusters serão tomadas as decisões inicias sobre particionamento, replicamento e retenção de dados considerando as demandas de pedidos
4. Serão definidos os consumers, que basicamente vão se inscrever nos topicos, e vão "processar" esses dados (por processar entende-se que os JSON serão mandados para as próximas etapas da pipeline).
5. Devem Ser implementados também os logs, estes são parte importante do processo ponta a ponta por que é com eles que serão detectados possíveis erros e em quais tópicos. Brokers, etc etc ocorreram esses erros.
6. Monitoramento será implementado para verificar como anda a saúde da aplicação e se são necessárias mudanças como aumentos de brokers e afins.
7. DLQ Caso houverem erros é importante para que o sistema continue operando e que concomitantemente as mensagens de erros ou outras mensagens sejam processadas.

A documentação de quick start também pode ser usada como referência para detalhes técnicos e entendimento sobre event streaming e o uso do Kafka:

[Kafka Documentation](https://kafka.apache.org/documentation)

#### Error Handling
Alguns dos approachs em relação a possíveis erros no Kafka são a criação de DLQs e a implementação de retrys.
As DLQs (Dead Letter Queues) são filas secundárias para qual vão mensagens que não puderam ser processadas na fila principal por diversos motivos. As mensagens não processadas são enviadas para essas filas para evitar gargalos de processamento e para que possam ser analisadas mais a fundo para que o problema que causou o seu não processamento possa ser detectado e corrigido.
Para implementar DLQs os seguintes passos são necessários:
1. Criação de um tópico DLQ que armazenará as mensagens não processadas.
2. Configurar um consumer com o código necessário para lidar com exceções que são capturadas e as mensagens que as causaram devem ser enviadas para a DLQ. É importante incluir informações adicionais como horário e razão pela qual foi movida para a DLQ, horário inicial de processamento e afins para facilitar a analíse e reprocessamento das DLQs.
3. É pertinente definir políticas de reprocessamento, correção ou descarte das mensagens para que sejam enviadas novamente para a fila principal.

### Armazenamento
Para criar um container no Blob Storage que consequentemente irá ser integrado com o Kafka siga os seguintes passos:
1. Caso ainda não possua, obtenha suas credenciais de acesso ao Blob Storage.
2. Crie uma conta de armazenamento indo até **Storage Accounts** caso ainda não exista.
3. Configure a conta com as informações necessárias.
4. Crie um container em **Blob Service >> Containers** com as configurações de acesso necessárias.
3. Obtenha as **Access Keys** do container criado, é importante copia-la pois será usada para conectar o Blob Storade a outras aplicaçoes como o Kafka por exemplo.
4. Adicione configuraçOes de criptografia e SAS para garantir maior segurança do container.
5. Teste o funcionamento do container.

Você também pode consultar a documentação abaixo para informações mais diversas e aprofundadas:
[Quickstart: Use Azure Storage Explorer to create a blob](https://learn.microsoft.com/en-us/azure/storage/blobs/quickstart-storage-explorer)

Para integrar o Kafka ao Blob Storage siga so seguintes passos:
1. Caso ainda não possua, obtenha suas credenciais de acesso ao Blob Storage.
2. Caso necessário instale um connector Kafka, como por exemplo:
[Azure Blob Storage Source Connector](https://www.confluent.io/hub/confluentinc/kafka-connect-azure-blob-storage-source?utm_medium=sem&utm_source=google&utm_campaign=ch.sem_br.nonbrand_tp.prs_tgt.kafka-connectors_mt.mbm_rgn.latam_lng.eng_dv.all_con.connector-azure-blob&utm_term=+kafka++connect++blob&placement=&device=c&creative=&gclid=Cj0KCQiAh8OtBhCQARIsAIkWb6__0h6jaAZsFysCZ9iIRcJp75VtIiSFMzPhAnM87z4dGRg6TMMB1xEaAoi2EALw_wcB&session_ref=https://www.google.com/)
[Azure Blob Storage Sink Connector](https://www.confluent.io/hub/confluentinc/kafka-connect-azure-blob-storage?utm_medium=sem&utm_source=google&utm_campaign=ch.sem_br.nonbrand_tp.prs_tgt.kafka-connectors_mt.mbm_rgn.latam_lng.eng_dv.all_con.connector-azure-blob&utm_term=+kafka++connect++blob&placement=&device=c&creative=&gclid=Cj0KCQiAh8OtBhCQARIsAIkWb6__0h6jaAZsFysCZ9iIRcJp75VtIiSFMzPhAnM87z4dGRg6TMMB1xEaAoi2EALw_wcB&session_ref=https://www.google.com/)
3. Crie o arquivo de configuração com as credenciais do Azure Blob e outras informações necessárias.
4. Após configurar o conector, é necessário inicia-lo para que o Kafka possa enviar os dados.
5. Teste a conexão enviando alguns dados mock e verificando se estão chegando no Blob Storage.

Para armazenar os dados já processado, é necessário configurar um ambiente no Databricks seguindo os seguintes passos:
1. Caso ainda não exista, crie um workspace Azure Databricks na Azure.
2. Crie um cluster Spark dentro do seu workspace.
3. Verifique se o runtime do Databricks já possui o Delta Lake e caso necessário o instale.
4. Crie um container no Blob Storage e configure seus acessos para armazenar os dados do Delta Lake.
5. Utilize os DBFS para montar seu bucket no Databricks.
6. Crie as tabelas delta com comandos SQL ou PySpark.
7. Faça testes de leitura e escrita para validar a criação das tabelas.

Você também pode consultar a documentação abaixo para informações mais diversas e aprofundadas:
[Tutorial Delta Lake](https://learn.microsoft.com/pt-br/azure/databricks/delta/tutorial)

### Processamento
Os passos para consumir os dados da camada bronze e depois processa-los são:
1. Leia os dados do diretorio da camada bronze utilizando o `readStream`. Segue um exemplo pratico:
```
bronze_df = spark.readStream.format("kafka").load("/path/to/bronze/directory")
```
2. Realize os processamentos necessários como citados anteriormente.
3. Persista os dados na camada silver no Delta Lake utilizando o `writeStream`. Segue um exemplo pratico:
```
query = silver_df.writeStream.format("delta").outputMode("append").option("checkpointLocation", "/path/to/checkpoint").start("/path/to/silver/directory")
```
4. Realize os processamentos e consolidações necessários para persistir os dados na camada silver.
5. Persista os dados na camada silver no Delta Lake utilizando o `writeStream`. Segue um exemplo pratico:
```
query = gold_df.writeStream.format("delta").outputMode("append").option("checkpointLocation", "/path/to/checkpoint").start("/path/to/gold/layer")
```
Obs: Por se tratar de processamento real-time recomenda-se que seja usando o `append` por questões de eficiência, integridade e simplificação do processamento.

### Analíse e Visualização.
Para integrar o Power Bi com o Delta Lake do Databricks siga os seguintes passos:
1. Instale e configure o Power BI em seu computador caso necessário.
2. Configure o Delta Lake caso necessário.
3. Caso ainda não esteja instalado e configurado instale o connector JDBC caso ainda não esteja instalado no Databricks. Use o guia a seguir caso necessário: [Databricks JDBC Driver](https://docs.databricks.com/en/_extras/documents/Databricks-JDBC-Driver-Install-and-Configuration-Guide.pdf)
4. Crie um Token PAT no Databricks.
5. Obtenha a url do servidor JDBC no Databricks pois será necessária para configurar a conexão.
6. No power BI vá até **Get data** e em seguida selecione **Azure Databricks**
7. Insira a url de conexão e seu PAT e clique em OK.
8. Depois disso os bancos do Delta Lake estarão disponíveis para seleção.

Você também pode consultar a documentação abaixo para informações mais diversas e aprofundadas:
[Connect Power BI to Databricks](https://docs.databricks.com/en/partners/bi/power-bi.html#connect-power-bi-to-databricks)

### Orquestramento
Para orquestrar a pipeline com o airflow siga os seguintes passos:
1. Instale e configure o Airflow para se conectar ao Databricks.
2. Para a ingestão podem ser criados [sensores](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/sensors.html) que verificarão se há novas mensagens no tópico do Kafka após integrar o Airflow e o Kafka através de conectores.
3. Para o processamento podem ser usados ou criados [operadores](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/operators.html#operators) para integrar o Airflow e o Databricks e automatizar a manutenção das tabelas do Delta Lake.
4. Para as analises uma vez que o Airflow e o Databricks já estao conectados pode se automatizar a execução de notebooks do Databricks através de operadores. E já considerado na etapa de processamento automatizar os dados que serão carregados no Power Bi.