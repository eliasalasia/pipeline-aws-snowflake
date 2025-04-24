import boto3
import zipfile
import io

s3 = boto3.client('s3')

def lambda_handler(event, context):
    print("Lambda iniciado..")

    try:
        bucket = event['Records'][0]['s3']['bucket']['name']
        zip_key = event['Records'][0]['s3']['object']['key']

        print(f" Bucket: {bucket}, Key: {zip_key}")

        if not zip_key.endswith('.zip'):
            print("No es un archivo ZIP.")
            return {'statusCode': 400, 'body': 'No es un archivo ZIP.'}

        #descargar el ZIP desde s3
        zip_obj = s3.get_object(Bucket=bucket, Key=zip_key)
        buffer = io.BytesIO(zip_obj['Body'].read())

        #extraer los archivos y guardarlos en /curated/
        with zipfile.ZipFile(buffer, 'r') as zip_ref:
            file_list = zip_ref.namelist()

            if not file_list:
                print(f"El ZIP {zip_key} esta vacio. No hay archivos para procesar.")
                return {'statusCode': 204, 'body': 'ZIP vacio'}

            for file_name in file_list:
                with zip_ref.open(file_name) as file:
                    s3.put_object(Bucket=bucket, Key=f'curated/{file_name}', Body=file.read())
                    print(f" Archivo extraido y guardado en curated/{file_name}")

        print("Funcion completada..")
        return {'statusCode': 200, 'body': f'Archivos extraidos: {file_list}'}

    except Exception as e:
        print(f"Error: {str(e)}")
        return {'statusCode': 500, 'body': f'Error interno: {str(e)}'}