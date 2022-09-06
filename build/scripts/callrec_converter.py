import boto3
import os
import sys
import logging
from datetime import datetime, timedelta
from pydub import AudioSegment

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s]: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Configuraciones
LOCAL_DIR = '/tmp'
DATE_FORMAT = "%Y-%m-%d"

# Fecha de ayer
yesterday = datetime.now() - timedelta(days=1)
ano, mes, dia = yesterday.strftime(DATE_FORMAT).split('-')

# Obtener las variables de entorno
callrec_format = os.environ.get('MONITORFORMAT', 'mp3')
callrec_device = os.getenv("CALLREC_DEVICE")
s3_bucket_name = os.getenv("S3_BUCKET_NAME")
s3_endpoint = os.getenv("S3_ENDPOINT")
storage_type = os.getenv('CALLREC_DEVICE')
aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID") or None
aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY") or None
endpoint_url = os.environ.get("S3_ENDPOINT") or None
region_name = os.environ.get("S3_REGION_NAME") or 'us-east-1'

# Crear cliente S3
try:
    if storage_type == 's3-aws':
        s3 = boto3.client('s3', region_name)
    elif storage_type == 's3-no-check-cert':
        s3 = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            endpoint_url=endpoint_url,
            verify=False)
    else:
        s3 = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            endpoint_url=endpoint_url)
except Exception as e:
    print(f"Error al crear el cliente S3: {str(e)}")
    exit(1)


# Verificación del formato de grabación
if callrec_format != 'mp3':
    logging.info("No es necesario convertir archivos, MONITORFORMAT no es mp3.")
else:
    local_path = os.path.join(LOCAL_DIR, f"{ano}-{mes}-{dia}")
    os.makedirs(local_path, exist_ok=True)
    os.chdir(local_path)

# Sincronizar los archivos .wav desde S3 al directorio local
try:
    s3_objects = s3.list_objects(Bucket=s3_bucket_name, Prefix=f"{ano}-{mes}-{dia}")['Contents']
except Exception as e:
    logging.error(f"Error al listar objetos desde S3 con el prefijo {ano}-{mes}-{dia}: {str(e)}")
    # Puedes decidir si deseas salir del script aquí o simplemente continuar.
    # exit(1)

for obj in s3_objects:
    filename = os.path.basename(obj['Key'])
    if filename.endswith('.wav'):
        try:
            # Descargar el archivo .wav desde S3
            s3.download_file(s3_bucket_name, obj['Key'], filename)
            logging.info(f"Archivo descargado con éxito: {filename}")
        except Exception as e:
            logging.error(f"Error al descargar el archivo {filename} desde S3: {str(e)}")
            # Si no puedes descargar el archivo, probablemente quieras saltarte la conversión y la
            # eliminación de este archivo.
            raise
        try:
            # Convertir el archivo .wav a .mp3
            sound = AudioSegment.from_wav(filename)
            sound.export(filename.replace('.wav', '.mp3'), format="mp3")
            logging.info(
                f"Archivo convertido con éxito: {filename} a {filename.replace('.wav', '.mp3')}")
        except Exception as e:
            logging.error(f"Error al convertir el archivo {filename} a MP3: {str(e)}")
            # Si la conversión falla, puedes decidir si aún deseas eliminar el archivo .wav
            # original.
            # Si decides continuar aquí, el bucle pasará al siguiente archivo en s3_objects.
            raise
        try:
            # Eliminar el archivo .wav original
            os.remove(filename)
            logging.info(f"Archivo eliminado con éxito: {filename}")
        except Exception as e:
            logging.error(f"Error al eliminar el archivo {filename}: {str(e)}")
            raise
            # Si la eliminación falla, probablemente quieras saberlo, pero es posible que no
            # necesites hacer nada adicional aquí.

    # # Sincronizar el directorio local con S3 y eliminar lo que no está en local
    # for root, dirs, files in os.walk(local_path):
    #     for file in files:
    #         local_file_path = os.path.join(root, file)
    #         s3_file_path = os.path.join(f"{ano}-{mes}-{dia}", file)
    #         s3.upload_file(local_file_path, S3_BUCKET_NAME, s3_file_path)

    # # Eliminación de Archivos Locales
    # for root, dirs, files in os.walk(local_path):
    #     for file in files:
    #         file_path = os.path.join(root, file)
    #         try:
    #             os.remove(file_path)
    #             logging.info(f"Archivo local eliminado: {file_path}")
    #         except Exception as e:
    #             logging.error(f"Error al eliminar el archivo local: {file_path}, Error: {str(e)}")

    logging.info("Procedimiento realizado con éxito")
