import boto3
import json

sqs = boto3.client('sqs')

#URL de la cola sqs
SQS_QUEUE_URL = "https://sqs.us-east-2.amazonaws.com/888577034559/parquet-notifications"

def lambda_handler(event, context):
    print("Lambda iniciada...")

    try:
        bucket = event['Records'][0]['s3']['bucket']['name']
        file_key = event['Records'][0]['s3']['object']['key']

        print(f"Nuevo archivo detectado en S3: {file_key}")

        #solo manda el mensaje si esta en 'Published/' y es Parquet
        if file_key.startswith('Published/') and file_key.endswith('.parquet'):
            message = {
                "bucket": bucket,
                "file_path": file_key
            }

            #envia el mensaje a la cola SQS
            response_sqs = sqs.send_message(
                QueueUrl=SQS_QUEUE_URL,
                MessageBody=json.dumps(message)
            )

            print(f"Mensaje enviado a SQS: {response_sqs['MessageId']}")

            return {'statusCode': 200, 'body': f'Mensaje enviado para {file_key}'}

        else:
            print("El archivo no es un .parquet o no está en la carpeta Published/")
            return {'statusCode': 400, 'body': 'Archivo ignorado'}

    except Exception as e:
        print(f"Error: {str(e)}")
        return {'statusCode': 500, 'body': f'Error interno: {str(e)}'}