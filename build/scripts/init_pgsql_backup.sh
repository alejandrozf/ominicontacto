
#!/bin/bash

if [ ! -f /etc/localtime ]; then
  ln -s /usr/share/zoneinfo/$TZ /etc/localtime
fi

pg_dump -h ${PGHOST} -p ${PGPORT} -U ${PGUSER} -Fc -b -v -f /tmp/${BACKUP_FILENAME} -d ${PGDATABASE}

case ${CALLREC_DEVICE} in
  s3-aws)
    aws s3 mv /tmp/${BACKUP_FILENAME} s3://${S3_BUCKET_NAME}/backup/        
  ;;
  s3-minio)
  	aws --endpoint-url ${S3_ENDPOINT_MINIO} s3 mv /tmp/${BACKUP_FILENAME} s3://${S3_BUCKET_NAME}/backup/        
  ;;       
  s3-no-check-cert)
    aws --endpoint ${S3_ENDPOINT} s3 --no-verify-ssl mv /tmp/${BACKUP_FILENAME} s3://${S3_BUCKET_NAME}/backup/
  ;;
  *)
  	aws --endpoint ${S3_ENDPOINT} s3 mv /tmp/${BACKUP_FILENAME} s3://${S3_BUCKET_NAME}/backup/
  ;;               
esac
