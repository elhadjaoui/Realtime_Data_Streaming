import sys
import os
import time 
from confluent_kafka import Producer, Consumer
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config.config import config


def delivery_report(err, msg):
  """Called once for each message produced to indicate delivery result.
  Triggered by poll() or flush()."""
  if err is not None:
    print(f"Message delivery failed: {err}")
  else:
    print(f"Message delivered to {msg.topic()} [{msg.partition()}]")


def produce(topic, config):
  # creates a new producer instance
  producer = Producer(config)
  file_path = "../datasets/yelp_academic_dataset_review.json"

  try:
    with open(file_path, 'r') as file:
        for line in file:
            producer.produce(
                topic=topic,            # Kafka topic
                key=None,               # Optional: partition key
                value=line.strip(),     # File line as the message value
                callback=delivery_report
            )
            producer.flush()           # Ensure message is sent before proceeding
            time.sleep(0.1)            # Simulate streaming (adjust as needed)

  except FileNotFoundError:
      print(f"Error: File {file_path} not found.")
  except Exception as e:
      print(f"An error occurred: {e}")
  finally:
      producer.flush()                   # Ensure all messages are delivered
      print("File ingestion completed.")

    # send any outstanding or buffered messages to the Kafka broker
  producer.flush()

# def consume(topic, config):
#   # sets the consumer group ID and offset  
#   config["group.id"] = "python-group-1"
#   config["auto.offset.reset"] = "earliest"

#   # creates a new consumer instance
#   consumer = Consumer(config)

#   # subscribes to the specified topic
#   consumer.subscribe([topic])

#   try:
#     while True:
#       # consumer polls the topic and prints any incoming messages
#       msg = consumer.poll(1.0)
#       if msg is not None and msg.error() is None:
#         key = msg.key().decode("utf-8")
#         value = msg.value().decode("utf-8")
#         print(f"Consumed message from topic {topic}: key = {key:12} value = {value:12}")
#   except KeyboardInterrupt:
#     pass
#   finally:
#     # closes the consumer connection
#     consumer.close()

def main():
  topic = "ingest-file"

  produce(topic, config['kafka'])
  # consume(topic, config)


main()
