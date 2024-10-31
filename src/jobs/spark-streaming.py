from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, when, udf
from pyspark.sql.types import StructType, StructField, StringType, FloatType


def streaming(spark):
    df = (spark.readStream.format("socket")
    .option("host", "localhost") 
    .option("port", 9999).load())
    
    schema = StructType([
                StructField("review_id", StringType()),
                StructField("user_id", StringType()),
                StructField("business_id", StringType()),
                StructField("stars", FloatType()),
                StructField("date", StringType()),
                StructField("text", StringType())
            ])
    df = df.select(from_json(col("value"), schema).alias("data")).select("data.*")
    query = df.writeStream.outputMode('append').format("console").start()
    query.awaitTermination()

if __name__ == "__main__":
    spark = SparkSession.builder.appName("SparkStreaming").getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    streaming(spark)
    

    
    
    spark.stop()