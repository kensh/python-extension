
export REGION=$(aws configure get region)

aws lambda publish-layer-version \
 --layer-name "python-example-extension" \
 --region ${REGION} \
 --zip-file  "fileb://extension.zip"
