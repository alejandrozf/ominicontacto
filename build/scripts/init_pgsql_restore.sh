
#!/bin/bash

if [ ! -f /etc/localtime ]; then
  ln -s /usr/share/zoneinfo/$TZ /etc/localtime
fi

case ${CALLREC_DEVICE} in
  s3-aws)
    aws s3 cp s3://${S3_BUCKET_NAME}/backup/${BACKUP_FILENAME} /tmp/
  ;;
  s3-minio)
  	aws --endpoint ${S3_ENDPOINT_MINIO} s3 cp s3://${S3_BUCKET_NAME}/backup/${BACKUP_FILENAME} /tmp/
  ;;       
  s3-no-check-cert)
    aws --endpoint ${S3_ENDPOINT} --no-verify-ssl s3 cp s3://${S3_BUCKET_NAME}/backup/${BACKUP_FILENAME} /tmp/
  ;;
  *)
  	aws --endpoint ${S3_ENDPOINT} s3 cp s3://${S3_BUCKET_NAME}/backup/${BACKUP_FILENAME} /tmp/
  ;;               
esac

pg_restore -d ${PGDATABASE} /tmp/${BACKUP_FILENAME}


