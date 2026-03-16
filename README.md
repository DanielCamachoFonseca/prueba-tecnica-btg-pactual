# BTG Pactual Funds API

API REST para gestión de fondos de inversión de BTG Pactual.

## 📋 Descripción

Esta API permite a los clientes de BTG Pactual gestionar sus fondos de inversión de manera autónoma, sin necesidad de contactar a un asesor.

### Funcionalidades

- ✅ Registro y autenticación de usuarios (JWT)
- ✅ Suscripción a fondos de inversión (apertura)
- ✅ Cancelación de suscripciones
- ✅ Consulta de historial de transacciones
- ✅ Notificaciones por email/SMS
- ✅ Roles y permisos (cliente/admin)

### Fondos Disponibles

| ID | Nombre | Monto Mínimo | Categoría |
|----|--------|--------------|-----------|
| 1 | FPV_BTG_PACTUAL_RECAUDADORA | COP $75.000 | FPV |
| 2 | FPV_BTG_PACTUAL_ECOPETROL | COP $125.000 | FPV |
| 3 | DEUDAPRIVADA | COP $50.000 | FIC |
| 4 | FDO-ACCIONES | COP $250.000 | FIC |
| 5 | FPV_BTG_PACTUAL_DINAMICA | COP $100.000 | FPV |

### Reglas de Negocio

- Saldo inicial del cliente: **COP $500.000**
- Cada transacción tiene un identificador único
- Cada fondo tiene un monto mínimo de vinculación
- Al cancelar una suscripción, el valor se retorna al cliente
- Si no hay saldo suficiente: "No tiene saldo disponible para vincularse al fondo {nombre}"

## 🛠️ Tecnologías

- **Python 3.11+**
- **FastAPI** - Framework web
- **MongoDB** - Base de datos NoSQL
- **Motor** - Driver async para MongoDB
- **JWT** - Autenticación
- **Pydantic** - Validación de datos
- **Pytest** - Testing
- **Docker** - Contenedores

## 📁 Estructura del Proyecto

```
btg-funds-api/
├── app/
│   ├── core/           # Configuración, DB, seguridad
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── security.py
│   │   └── exceptions.py
│   ├── models/         # Modelos de MongoDB
│   │   ├── user.py
│   │   ├── fund.py
│   │   └── transaction.py
│   ├── schemas/        # Schemas Pydantic
│   │   ├── user.py
│   │   ├── auth.py
│   │   ├── fund.py
│   │   └── transaction.py
│   ├── services/       # Lógica de negocio
│   │   ├── user_service.py
│   │   ├── fund_service.py
│   │   ├── transaction_service.py
│   │   └── notification_service.py
│   ├── routers/        # Endpoints API
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── funds.py
│   │   └── subscriptions.py
│   └── main.py         # Aplicación FastAPI
├── tests/              # Pruebas unitarias
├── aws/                # CloudFormation templates
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 🚀 Instalación y Ejecución

### Prerrequisitos

- Python 3.11+
- Docker y Docker Compose
- Git

### 1. Clonar el repositorio

```bash
git clone https://github.com/DanielCamachoFonseca/prueba-tecnica-btg-pactual.git
cd btg-funds-api
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tus valores
```

### 3. Iniciar MongoDB con Docker

```bash
docker-compose up -d
```

### 4. Crear entorno virtual e instalar dependencias

```bash
python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### 5. Ejecutar la aplicación

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Acceder a la documentación

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📝 Endpoints de la API

### Autenticación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Registrar nuevo usuario |
| POST | `/api/v1/auth/login` | Iniciar sesión |
| POST | `/api/v1/auth/refresh` | Renovar token |
| GET | `/api/v1/auth/me` | Obtener usuario actual |

### Fondos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/funds` | Listar todos los fondos |
| GET | `/api/v1/funds/{fund_id}` | Obtener fondo por ID |

### Suscripciones

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/subscriptions` | Suscribirse a un fondo |
| DELETE | `/api/v1/subscriptions/{id}` | Cancelar suscripción |
| GET | `/api/v1/subscriptions` | Ver suscripciones activas |
| GET | `/api/v1/subscriptions/history` | Ver historial de transacciones |

### Usuarios

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/users/me` | Obtener perfil |
| PUT | `/api/v1/users/me` | Actualizar perfil |
| GET | `/api/v1/users/me/balance` | Consultar saldo |

## 🔐 Autenticación

La API usa JWT (JSON Web Tokens) para autenticación.

### Obtener token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "usuario@email.com", "password": "Password123"}'
```

### Usar token en requests

```bash
curl -X GET "http://localhost:8000/api/v1/funds" \
  -H "Authorization: Bearer <access_token>"
```

## 🧪 Ejecutar Pruebas

```bash
# Ejecutar todas las pruebas
pytest

# Con cobertura
pytest --cov=app --cov-report=html

# Pruebas específicas
pytest tests/test_transaction_service.py -v
```

## 🐳 Docker

### Construir imagen

```bash
docker build -t btg-funds-api .
```

### Ejecutar con Docker Compose

```bash
# Desarrollo
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down
```

## ☁️ Despliegue en AWS

Ver documentación detallada en [`aws/README.md`](aws/README.md)

### Recursos AWS utilizados

- **Amazon ECS** - Orquestación de contenedores
- **Amazon DocumentDB** - Base de datos compatible con MongoDB
- **Application Load Balancer** - Balanceo de carga
- **Amazon ECR** - Registro de contenedores
- **AWS Secrets Manager** - Gestión de secretos
- **Amazon SES** - Envío de emails
- **Amazon SNS** - Envío de SMS

### Despliegue con CloudFormation

```bash
aws cloudformation create-stack \
  --stack-name btg-funds-api \
  --template-body file://aws/cloudformation.yaml \
  --parameters file://aws/parameters.json \
  --capabilities CAPABILITY_IAM
```

## 📊 Modelo de Datos

### Usuario
```json
{
  "_id": "ObjectId",
  "email": "string",
  "hashed_password": "string",
  "full_name": "string",
  "phone": "string",
  "balance": "number",
  "notification_preference": "email|sms|both|none",
  "role": "client|admin",
  "is_active": "boolean",
  "subscriptions": ["subscription_ids"],
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Fondo
```json
{
  "_id": "ObjectId",
  "fund_id": "number",
  "name": "string",
  "minimum_amount": "number",
  "category": "FPV|FIC",
  "description": "string",
  "is_active": "boolean",
  "created_at": "datetime"
}
```

### Transacción
```json
{
  "_id": "ObjectId",
  "transaction_id": "string",
  "user_id": "string",
  "fund_id": "number",
  "fund_name": "string",
  "transaction_type": "apertura|cancelacion",
  "amount": "number",
  "status": "completada|pendiente|fallida",
  "previous_balance": "number",
  "new_balance": "number",
  "notification_sent": "boolean",
  "notification_type": "string",
  "created_at": "datetime"
}
```

## 🔒 Seguridad

- Contraseñas hasheadas con bcrypt
- Tokens JWT con expiración configurable
- Validación de datos con Pydantic
- CORS configurado
- Manejo de excepciones centralizado
- Roles y permisos (RBAC)

## � Parte 2 - SQL (20%)

La solución al punto 2 de la prueba técnica (consultas SQL) se encuentra en:

📁 [`sql/consulta_btg.sql`](sql/consulta_btg.sql)

Este archivo contiene:
- Creación de tablas (Cliente, Sucursal, Producto, Inscripcion, Disponibilidad, Visitan)
- Datos de ejemplo para pruebas
- Consulta solicitada: *"Obtener los nombres de los clientes que tienen inscrito algún producto disponible solo en las sucursales que visitan"*
- Explicación detallada de la lógica utilizada

## �👥 Autor

**Daniel Camacho Fonseca**

## 📄 Licencia

MIT License
