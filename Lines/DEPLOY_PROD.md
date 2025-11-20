# Production Deployment Guide

## Prerequisites

1. **AWS CLI configured** with appropriate credentials
2. **SAM CLI installed** ([Installation Guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html))
3. **Docker running** (for building with `--use-container`)

## Deployment Steps

### 1. Build the application

```bash
cd /Users/sidekick/ALL_CODE/AWS/Tazent/Lines
sam build --template-file template.prod.yaml --use-container
```

### 2. Deploy to Production

Deploy with the Stage parameter set to "prod":

```bash
sam deploy \
  --template-file template.prod.yaml \
  --stack-name TanzentLines-prod \
  --parameter-overrides Stage=prod \
  --capabilities CAPABILITY_IAM \
  --region us-east-1 \
  --confirm-changeset \
  --resolve-s3
```

### 3. Alternative: Deploy with guided mode (first time)

For the first deployment, you can use guided mode:

```bash
sam deploy \
  --template-file template.prod.yaml \
  --guided \
  --parameter-overrides Stage=prod
```

This will prompt you for:
- Stack name: `TanzentLines-prod`
- AWS Region: `us-east-1`
- Confirm changes before deploy: `Y`
- Allow SAM CLI IAM role creation: `Y`
- Disable rollback: `N` (recommended to keep rollback enabled)
- Save arguments to configuration file: `Y`

### 4. Verify Deployment

After deployment, check the outputs:

```bash
aws cloudformation describe-stacks \
  --stack-name TanzentLines-prod \
  --region us-east-1 \
  --query 'Stacks[0].Outputs'
```

This will show:
- `HttpApiUrl`: Your API Gateway endpoint
- `LinesTableName`: DynamoDB table name
- `LinePropertyTableName`: LineProperty table name
- `CirclesTableName`: Circles table name
- `HomeWidgetsTableName`: HomeWidgets table name

### 5. Update Existing Stack

For subsequent deployments:

```bash
sam build --template-file template.prod.yaml --use-container
sam deploy \
  --template-file template.prod.yaml \
  --stack-name TanzentLines-prod \
  --parameter-overrides Stage=prod \
  --capabilities CAPABILITY_IAM \
  --region us-east-1 \
  --confirm-changeset \
  --resolve-s3
```

## Important Notes

1. **Table Names**: Tables will be created with stage suffix:
   - `LinesDB-prod`
   - `LineProperty-prod`
   - `Circles-prod`
   - `HomeWidgets-prod`

2. **Cost**: Tables use fixed provisioned capacity (1 read/write unit each) to stay within AWS Free Tier

3. **IAM Role**: The template uses an existing IAM role: `arn:aws:iam::107207560024:role/TanzentLambdaRole`
   - Ensure this role exists and has necessary permissions

4. **S3 Bucket**: SAM will create/use an S3 bucket for deployment artifacts
   - Default prefix: `TanzentLines` (from samconfig.toml)

## Troubleshooting

### Check deployment status:
```bash
aws cloudformation describe-stacks \
  --stack-name TanzentLines-prod \
  --region us-east-1
```

### View stack events:
```bash
aws cloudformation describe-stack-events \
  --stack-name TanzentLines-prod \
  --region us-east-1 \
  --max-items 20
```

### Delete stack (if needed):
```bash
sam delete --stack-name TanzentLines-prod --region us-east-1
```

## Environment Variables

The Lambda functions will automatically receive the correct table names via environment variables:
- `LINES_TABLE_NAME`: Points to `LinesDB-prod`
- `LINES_PROPERTY_TABLE_NAME`: Points to `LineProperty-prod`
- `CIRCLES_TABLE_NAME`: Points to `Circles-prod`
- `HOME_WIDGETS_TABLE_NAME`: Points to `HomeWidgets-prod`

These are set automatically by CloudFormation based on the Stage parameter.

