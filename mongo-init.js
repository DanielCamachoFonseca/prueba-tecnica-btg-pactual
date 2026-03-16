/**
 * Script de inicialización de MongoDB para BTG Pactual Funds API
 * Este script se ejecuta automáticamente al iniciar el contenedor de MongoDB
 */

// Cambiar a la base de datos de la aplicación
db = db.getSiblingDB('btg_funds');

// Crear usuario específico para la aplicación (opcional, usa el admin por defecto)
// db.createUser({
//     user: 'btg_app_user',
//     pwd: 'btg_app_password',
//     roles: [{ role: 'readWrite', db: 'btg_funds' }]
// });

// Crear colecciones con validación de esquema

// Colección de usuarios
db.createCollection('users', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['email', 'hashed_password', 'full_name', 'balance', 'role'],
            properties: {
                email: {
                    bsonType: 'string',
                    description: 'Email del usuario - requerido'
                },
                hashed_password: {
                    bsonType: 'string',
                    description: 'Contraseña hasheada - requerido'
                },
                full_name: {
                    bsonType: 'string',
                    description: 'Nombre completo del usuario'
                },
                phone: {
                    bsonType: ['string', 'null'],
                    description: 'Número de teléfono'
                },
                balance: {
                    bsonType: 'double',
                    minimum: 0,
                    description: 'Saldo disponible en COP'
                },
                notification_preference: {
                    enum: ['email', 'sms', 'both', 'none'],
                    description: 'Preferencia de notificación'
                },
                role: {
                    enum: ['client', 'admin'],
                    description: 'Rol del usuario'
                },
                is_active: {
                    bsonType: 'bool',
                    description: 'Estado del usuario'
                }
            }
        }
    }
});

// Crear índice único para email
db.users.createIndex({ email: 1 }, { unique: true });
db.users.createIndex({ role: 1 });
db.users.createIndex({ created_at: -1 });

// Colección de fondos
db.createCollection('funds', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['fund_id', 'name', 'minimum_amount', 'category'],
            properties: {
                fund_id: {
                    bsonType: 'int',
                    minimum: 1,
                    description: 'ID único del fondo'
                },
                name: {
                    bsonType: 'string',
                    description: 'Nombre del fondo'
                },
                minimum_amount: {
                    bsonType: 'double',
                    minimum: 0,
                    description: 'Monto mínimo de vinculación'
                },
                category: {
                    enum: ['FPV', 'FIC'],
                    description: 'Categoría del fondo'
                },
                is_active: {
                    bsonType: 'bool',
                    description: 'Estado del fondo'
                }
            }
        }
    }
});

// Crear índices para fondos
db.funds.createIndex({ fund_id: 1 }, { unique: true });
db.funds.createIndex({ category: 1 });
db.funds.createIndex({ is_active: 1 });

// Colección de suscripciones
db.createCollection('subscriptions');
db.subscriptions.createIndex({ user_id: 1 });
db.subscriptions.createIndex({ fund_id: 1 });
db.subscriptions.createIndex({ user_id: 1, fund_id: 1, is_active: 1 });
db.subscriptions.createIndex({ is_active: 1 });
db.subscriptions.createIndex({ subscription_date: -1 });

// Colección de transacciones
db.createCollection('transactions');
db.transactions.createIndex({ transaction_id: 1 }, { unique: true });
db.transactions.createIndex({ user_id: 1 });
db.transactions.createIndex({ fund_id: 1 });
db.transactions.createIndex({ transaction_type: 1 });
db.transactions.createIndex({ created_at: -1 });
db.transactions.createIndex({ user_id: 1, created_at: -1 });

// Insertar fondos iniciales según requerimientos
db.funds.insertMany([
    {
        fund_id: 1,
        name: 'FPV_BTG_PACTUAL_RECAUDADORA',
        minimum_amount: 75000.0,
        category: 'FPV',
        description: 'Fondo de Pensiones Voluntarias BTG Pactual Recaudadora',
        is_active: true,
        created_at: new Date()
    },
    {
        fund_id: 2,
        name: 'FPV_BTG_PACTUAL_ECOPETROL',
        minimum_amount: 125000.0,
        category: 'FPV',
        description: 'Fondo de Pensiones Voluntarias BTG Pactual Ecopetrol',
        is_active: true,
        created_at: new Date()
    },
    {
        fund_id: 3,
        name: 'DEUDAPRIVADA',
        minimum_amount: 50000.0,
        category: 'FIC',
        description: 'Fondo de Inversión Colectiva Deuda Privada',
        is_active: true,
        created_at: new Date()
    },
    {
        fund_id: 4,
        name: 'FDO-ACCIONES',
        minimum_amount: 250000.0,
        category: 'FIC',
        description: 'Fondo de Inversión Colectiva Acciones',
        is_active: true,
        created_at: new Date()
    },
    {
        fund_id: 5,
        name: 'FPV_BTG_PACTUAL_DINAMICA',
        minimum_amount: 100000.0,
        category: 'FPV',
        description: 'Fondo de Pensiones Voluntarias BTG Pactual Dinámica',
        is_active: true,
        created_at: new Date()
    }
]);

// Crear usuario administrador por defecto
// Password: Admin123! (hasheado con bcrypt)
db.users.insertOne({
    email: 'admin@btgpactual.com',
    hashed_password: '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.S9m0c8cVLw4qDi',
    full_name: 'Administrador BTG',
    phone: null,
    balance: 0,
    notification_preference: 'email',
    role: 'admin',
    is_active: true,
    subscriptions: [],
    created_at: new Date(),
    updated_at: new Date()
});

print('Base de datos BTG Funds inicializada correctamente');
print('Fondos creados: 5');
print('Usuario admin creado: admin@btgpactual.com');
