from time import sleep
from openai import OpenAI
import sys
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, when, udf, decode
from pyspark.sql.types import StructType, StructField, StringType, FloatType
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config.config import config

def sentiment_analysis(comment) -> str:
    if comment:
        client = OpenAI(api_key= config['openai']['api_key'])
        completion = client.chat.completions.create(
            model='gpt-4o',
            messages = [
                {
                    "role": "system",
                    "content": """
                        You're a machine learning model with a task of classifying comments into POSITIVE, NEGATIVE, NEUTRAL.
                        You are to respond with one word from the option specified above, do not add anything else.
                        Here is the comment:
                        
                        {comment}
                    """.format(comment=comment)
                }
            ]
        )
        return completion.choices[0].message.content
    return "Empty"

def start_streaming(spark):
    topic1 = 'ingest-file'
    topic2 = 'ingested-file'
    while True:
        try:
            stream_df = (spark.readStream
                .format("kafka")
                .option("kafka.bootstrap.servers", config['kafka']['bootstrap.servers'])
                .option("kafka.security.protocol", config['kafka']['security.protocol'])
                .option('kafka.sasl.mechanism', config['kafka']['sasl.mechanisms'])\
                .option('kafka.sasl.jaas.config',
                           'org.apache.kafka.common.security.plain.PlainLoginModule required username="{username}" '
                           'password="{password}";'.format(
                               username=config['kafka']['sasl.username'],
                               password=config['kafka']['sasl.password']
                           ))
                .option('checkpointLocation', '/tmp/checkpoint')
                .option("subscribe", topic1) 
                .load())
            print("*************************** = ",stream_df)
            print("***************************")

            schema = StructType([
                StructField("review_id", StringType()),
                StructField("user_id", StringType()),
                StructField("business_id", StringType()),
                StructField("stars", FloatType()),
                StructField("date", StringType()),
                StructField("text", StringType())
            ])
            
            stream_df = stream_df.select(decode(col('value'), 'UTF-8').alias('value_string'))
            stream_df = stream_df.select(from_json(col('value_string'), schema).alias("data")).select(("data.*"))


            sentiment_analysis_udf = udf(sentiment_analysis, StringType())

            stream_df = stream_df.withColumn('feedback', when(col('text').isNotNull(), sentiment_analysis_udf(col('text'))) .otherwise(None))

            kafka_df = stream_df.selectExpr("CAST(review_id AS STRING) AS key", "to_json(struct(*)) AS value")

            query = (kafka_df.writeStream
                   .format("kafka")
                   .option("kafka.bootstrap.servers", config['kafka']['bootstrap.servers'])
                   .option("kafka.security.protocol", config['kafka']['security.protocol'])
                   .option('kafka.sasl.mechanism', config['kafka']['sasl.mechanisms'])
                   .option('kafka.sasl.jaas.config',
                           'org.apache.kafka.common.security.plain.PlainLoginModule required username="{username}" '
                           'password="{password}";'.format(
                               username=config['kafka']['sasl.username'],
                               password=config['kafka']['sasl.password']
                           ))
                   .option('checkpointLocation', '/tmp/checkpoint')
                   .option('topic', topic2)
                   .start()
                   .awaitTermination()
                )

        except Exception as e:
            print(f'Exception encountered: {e}. Retrying in 10 seconds')
            sleep(10)

if __name__ == "__main__":
    spark_conn = SparkSession.builder.appName("SocketStreamConsumer").getOrCreate()

    start_streaming(spark_conn)