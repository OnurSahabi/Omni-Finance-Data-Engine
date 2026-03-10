from pyspark.sql import SparkSession


def get_spark_session(
    app_name: str = "fintek_analytics",
    executor_memory: str = "2g",
    driver_memory: str = "1g",
    executor_cores: int = 2,
    shuffle_partitions: int = 10
) -> SparkSession:

    spark = (
        SparkSession.builder
        .appName(app_name)
        .master("spark://spark-master:7077")

        .config("spark.executor.memory", executor_memory)
        .config("spark.driver.memory", driver_memory)
        .config("spark.executor.cores", executor_cores)
        .config("spark.sql.shuffle.partitions", shuffle_partitions)

        .config("spark.driver.host", "fintek-jupyter")
        .config("spark.driver.bindAddress", "0.0.0.0")

        .config("spark.jars.packages", "org.postgresql:postgresql:42.7.3")

        .getOrCreate()
    )

    return spark
