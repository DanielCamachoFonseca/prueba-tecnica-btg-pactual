-- ============================================================================
-- BTG Pactual - Prueba Técnica - Parte 2: SQL (20%)
-- Autor: Daniel Camacho Fonseca
-- ============================================================================
-- Consulta solicitada:
-- Obtener los nombres de los clientes que tienen inscrito algún producto 
-- disponible SOLO en las sucursales que visitan.
-- ============================================================================

-- ============================================================================
-- PARTE 1: CREACIÓN DE TABLAS
-- ============================================================================

CREATE TABLE Cliente (
    id NUMBER PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    ciudad VARCHAR(100) NOT NULL
);

CREATE TABLE Sucursal (
    id NUMBER PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    ciudad VARCHAR(100) NOT NULL
);

CREATE TABLE Producto (
    id NUMBER PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    tipoProducto VARCHAR(50) NOT NULL
);

CREATE TABLE Inscripcion (
    idProducto NUMBER NOT NULL,
    idCliente NUMBER NOT NULL,
    PRIMARY KEY (idProducto, idCliente),
    FOREIGN KEY (idProducto) REFERENCES Producto(id),
    FOREIGN KEY (idCliente) REFERENCES Cliente(id)
);

CREATE TABLE Disponibilidad (
    idSucursal NUMBER NOT NULL,
    idProducto NUMBER NOT NULL,
    PRIMARY KEY (idSucursal, idProducto),
    FOREIGN KEY (idSucursal) REFERENCES Sucursal(id),
    FOREIGN KEY (idProducto) REFERENCES Producto(id)
);

CREATE TABLE Visitan (
    idSucursal NUMBER NOT NULL,
    idCliente NUMBER NOT NULL,
    fechaVisita DATE NOT NULL,
    PRIMARY KEY (idSucursal, idCliente),
    FOREIGN KEY (idSucursal) REFERENCES Sucursal(id),
    FOREIGN KEY (idCliente) REFERENCES Cliente(id)
);

-- ============================================================================
-- PARTE 2: DATOS DE EJEMPLO
-- ============================================================================

-- Clientes
INSERT INTO Cliente VALUES (1, 'Juan', 'Pérez García', 'Bogotá');
INSERT INTO Cliente VALUES (2, 'María', 'López Rodríguez', 'Medellín');
INSERT INTO Cliente VALUES (3, 'Carlos', 'Gómez Martínez', 'Cali');
INSERT INTO Cliente VALUES (4, 'Ana', 'Ramírez Torres', 'Bogotá');
INSERT INTO Cliente VALUES (5, 'Pedro', 'Sánchez Díaz', 'Barranquilla');

-- Sucursales
INSERT INTO Sucursal VALUES (1, 'Sucursal Centro', 'Bogotá');
INSERT INTO Sucursal VALUES (2, 'Sucursal Norte', 'Bogotá');
INSERT INTO Sucursal VALUES (3, 'Sucursal Poblado', 'Medellín');
INSERT INTO Sucursal VALUES (4, 'Sucursal Sur', 'Cali');
INSERT INTO Sucursal VALUES (5, 'Sucursal Principal', 'Barranquilla');

-- Productos
INSERT INTO Producto VALUES (1, 'FPV_BTG_PACTUAL_RECAUDADORA', 'FPV');
INSERT INTO Producto VALUES (2, 'FPV_BTG_PACTUAL_ECOPETROL', 'FPV');
INSERT INTO Producto VALUES (3, 'DEUDAPRIVADA', 'FIC');
INSERT INTO Producto VALUES (4, 'FDO-ACCIONES', 'FIC');
INSERT INTO Producto VALUES (5, 'FPV_BTG_PACTUAL_DINAMICA', 'FPV');

-- Disponibilidad (qué productos ofrece cada sucursal)
-- Producto 1: Disponible en TODAS las sucursales
INSERT INTO Disponibilidad VALUES (1, 1);
INSERT INTO Disponibilidad VALUES (2, 1);
INSERT INTO Disponibilidad VALUES (3, 1);
INSERT INTO Disponibilidad VALUES (4, 1);
INSERT INTO Disponibilidad VALUES (5, 1);

-- Producto 2: Disponible SOLO en Bogotá (sucursales 1 y 2)
INSERT INTO Disponibilidad VALUES (1, 2);
INSERT INTO Disponibilidad VALUES (2, 2);

-- Producto 3: Disponible SOLO en sucursal Centro Bogotá (sucursal 1)
INSERT INTO Disponibilidad VALUES (1, 3);

-- Producto 4: Disponible en Medellín y Cali (sucursales 3 y 4)
INSERT INTO Disponibilidad VALUES (3, 4);
INSERT INTO Disponibilidad VALUES (4, 4);

-- Producto 5: Disponible SOLO en Barranquilla (sucursal 5)
INSERT INTO Disponibilidad VALUES (5, 5);

-- Visitas de clientes a sucursales
-- Juan visita sucursales de Bogotá (1 y 2)
INSERT INTO Visitan VALUES (1, 1, DATE '2024-01-15');
INSERT INTO Visitan VALUES (2, 1, DATE '2024-02-20');

-- María visita sucursal de Medellín (3)
INSERT INTO Visitan VALUES (3, 2, DATE '2024-01-10');

-- Carlos visita sucursal de Cali (4)
INSERT INTO Visitan VALUES (4, 3, DATE '2024-03-05');

-- Ana visita SOLO sucursal Centro Bogotá (1)
INSERT INTO Visitan VALUES (1, 4, DATE '2024-02-28');

-- Pedro visita sucursal de Barranquilla (5)
INSERT INTO Visitan VALUES (5, 5, DATE '2024-01-20');

-- Inscripciones de clientes a productos
-- Juan inscrito a productos 1 y 2
INSERT INTO Inscripcion VALUES (1, 1);  
INSERT INTO Inscripcion VALUES (2, 1);  

-- María inscrita a productos 1 y 4
INSERT INTO Inscripcion VALUES (1, 2);  
INSERT INTO Inscripcion VALUES (4, 2);  

-- Carlos inscrito a producto 4
INSERT INTO Inscripcion VALUES (4, 3);  

-- Ana inscrita a productos 2 y 3
INSERT INTO Inscripcion VALUES (2, 4);  
INSERT INTO Inscripcion VALUES (3, 4);

-- Pedro inscrito a producto 5
INSERT INTO Inscripcion VALUES (5, 5); 


-- ============================================================================
-- PARTE 3: CONSULTA SOLICITADA
-- ============================================================================
-- Obtener los nombres de los clientes que tienen inscrito algún producto 
-- disponible SOLO en las sucursales que visitan.
-- ============================================================================


-- ============================================================================
-- OPCIÓN 1: Usando NOT EXISTS (más explícita y legible)
-- ============================================================================
SELECT DISTINCT c.nombre, c.apellidos
FROM Cliente c
INNER JOIN Inscripcion i ON c.id = i.idCliente
WHERE 
    NOT EXISTS (
        SELECT 1
        FROM Disponibilidad d
        WHERE d.idProducto = i.idProducto
        AND d.idSucursal NOT IN (
            SELECT v.idSucursal
            FROM Visitan v
            WHERE v.idCliente = c.id
        )
    )
    AND EXISTS (
        SELECT 1
        FROM Disponibilidad d
        INNER JOIN Visitan v ON d.idSucursal = v.idSucursal
        WHERE d.idProducto = i.idProducto
        AND v.idCliente = c.id
    );


-- ============================================================================
-- OPCIÓN 2: Usando JOINs + GROUP BY + HAVING (optimizada para rendimiento)
-- ============================================================================
SELECT DISTINCT c.nombre, c.apellidos
FROM Cliente c
INNER JOIN Inscripcion i ON c.id = i.idCliente
INNER JOIN Disponibilidad d ON i.idProducto = d.idProducto
LEFT JOIN Visitan v ON d.idSucursal = v.idSucursal AND v.idCliente = c.id
GROUP BY c.id, c.nombre, c.apellidos, i.idProducto
HAVING COUNT(d.idSucursal) = COUNT(v.idSucursal);


-- ============================================================================
-- RESULTADO ESPERADO (ambas consultas devuelven el mismo resultado):
-- ============================================================================
-- | nombre | apellidos        |
-- |--------|------------------|
-- | Juan   | Pérez García     |  -> Producto 2 solo en Bogotá, visita ambas
-- | Ana    | Ramírez Torres   |  -> Producto 3 solo en sucursal 1, la visita
-- | Pedro  | Sánchez Díaz     |  -> Producto 5 solo en sucursal 5, la visita
-- ============================================================================
