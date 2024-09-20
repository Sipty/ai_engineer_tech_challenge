import pika
import logging
from chat import get_chat_response

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    try:
        # Establish connection with heartbeat and timeout
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            'localhost',
            heartbeat=600,
            blocked_connection_timeout=300
        ))
        channel = connection.channel()

        # Declare queues
        channel.queue_declare(queue='chat_requests')
        channel.queue_declare(queue='chat_responses')

        # Set prefetch count
        channel.basic_qos(prefetch_count=1)

        # Set up consumer
        channel.basic_consume(queue='chat_requests', on_message_callback=callback)

        logger.info('Established connection to RabbitMQ. Waiting for messages...')
        channel.start_consuming()
    except pika.exceptions.AMQPConnectionError as error:
        logger.error(f"Unable to connect to RabbitMQ: {error}")
    except KeyboardInterrupt:
        logger.info("Worker stopped by user.")
    except Exception as error:
        logger.error(f"An unexpected error occurred: {error}")

def callback(ch, method, properties, body):
    try:
        message = body.decode()
        logger.info(f"Received message: {message[:50]}...")
        logger.info("The message has correlation_id: %s", properties.correlation_id)  
              
        response = get_chat_response(message)
        
        ch.basic_publish(
            exchange='',
            routing_key='chat_responses',
            properties=pika.BasicProperties(correlation_id=properties.correlation_id),
            body=response
        )
        logger.info(f"Published response: {response[:50]}...")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as error:
        logger.error(f"Error processing message: {error}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

if __name__ == "__main__":
    main()