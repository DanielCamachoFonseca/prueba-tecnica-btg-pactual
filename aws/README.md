# AWS CloudFormation y Documentación de Despliegue

Este directorio contiene los templates de CloudFormation y la documentación para desplegar la API en AWS.

## Arquitectura

```
                    ┌─────────────────┐
                    │   Route 53      │
                    │   (DNS)         │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  CloudFront     │
                    │  (CDN/WAF)      │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   Application   │
                    │  Load Balancer  │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
     ┌────────▼───────┐     ...     ┌──────▼────────┐
     │   ECS Task 1   │             │  ECS Task N   │
     │  (FastAPI)     │             │  (FastAPI)    │
     └────────┬───────┘             └───────┬───────┘
              │                             │
              └──────────────┬──────────────┘
                             │
                    ┌────────▼────────┐
                    │   DocumentDB    │
                    │   (MongoDB)     │
                    └─────────────────┘
```

## Recursos Desplegados

### Networking
- VPC con subnets públicas y privadas
- Internet Gateway
- NAT Gateway
- Security Groups

### Compute
- ECS Cluster (Fargate)
- Application Load Balancer
- Auto Scaling

### Database
- Amazon DocumentDB (compatible con MongoDB)

### Storage
- Amazon ECR (Container Registry)

### Security
- AWS Secrets Manager
- IAM Roles y Policies
- Security Groups

### Notifications
- Amazon SES (Email)
- Amazon SNS (SMS)

## Prerequisitos

1. AWS CLI configurado
2. Cuenta AWS con permisos necesarios
3. Docker instalado localmente

## Pasos de Despliegue

### 1. Construir y subir imagen Docker

```bash
# Login a ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Construir imagen
docker build -t btg-funds-api .

# Tag
docker tag btg-funds-api:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/btg-funds-api:latest

# Push
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/btg-funds-api:latest
```

### 2. Crear stack de CloudFormation

```bash
aws cloudformation create-stack \
  --stack-name btg-funds-api-stack \
  --template-body file://cloudformation.yaml \
  --parameters \
    ParameterKey=Environment,ParameterValue=production \
    ParameterKey=DBUsername,ParameterValue=btg_admin \
    ParameterKey=DBPassword,ParameterValue=<secure-password> \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM
```

### 3. Verificar despliegue

```bash
aws cloudformation describe-stacks --stack-name btg-funds-api-stack
```

## Variables de Entorno para Producción

```
MONGODB_URL=mongodb://<user>:<password>@<docdb-endpoint>:27017/?tls=true&tlsCAFile=/app/rds-combined-ca-bundle.pem&retryWrites=false
SECRET_KEY=<secure-random-key>
DEBUG=false
```

## Monitoreo

- CloudWatch Logs para logs de aplicación
- CloudWatch Metrics para métricas de ECS
- X-Ray para tracing (opcional)

## Costos Estimados

| Recurso | Costo Mensual Estimado |
|---------|------------------------|
| ECS Fargate (2 tasks) | ~$30-50 |
| DocumentDB (1 instance) | ~$200-300 |
| ALB | ~$20 |
| NAT Gateway | ~$45 |
| Data Transfer | Variable |

**Total estimado**: $300-500/mes (depende del uso)

## Rollback

```bash
aws cloudformation rollback-stack --stack-name btg-funds-api-stack
```

## Eliminar Stack

```bash
aws cloudformation delete-stack --stack-name btg-funds-api-stack
```
