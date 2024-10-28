from pyspark.sql import SparkSession

def streaming(spark):
    df = (spark.readStream.format("socket")
    .option("host", "localhost") 
    .option("port", 9999).load())
    
    query = df.writeStream.outputMode('append').format("console").start()
    query.awaitTermination()

if __name__ == "__main__":
    spark = SparkSession.builder.appName("SparkStreaming").getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    streaming(spark)
    

    
    
    spark.stop()