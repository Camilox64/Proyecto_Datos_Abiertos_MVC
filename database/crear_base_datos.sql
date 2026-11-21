/* Base de datos para el proyecto de consulta histórica de casos COVID-19. */
USE master;
GO

IF DB_ID(N'DatosAbiertosDB') IS NULL
BEGIN
    CREATE DATABASE DatosAbiertosDB;
END;
GO

USE DatosAbiertosDB;
GO

IF OBJECT_ID(N'dbo.RegistrosAPI', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.RegistrosAPI (
        id BIGINT IDENTITY(1,1) NOT NULL CONSTRAINT PK_RegistrosAPI PRIMARY KEY,
        id_api NVARCHAR(40) NOT NULL,
        fecha_reporte_web DATETIME2 NULL,
        fecha_notificacion DATETIME2 NULL,
        departamento NVARCHAR(12) NULL,
        departamento_nombre NVARCHAR(120) NULL,
        municipio NVARCHAR(12) NULL,
        municipio_nombre NVARCHAR(160) NULL,
        edad INT NULL,
        unidad_medida NVARCHAR(12) NULL,
        sexo NVARCHAR(12) NULL,
        tipo_contagio NVARCHAR(80) NULL,
        ubicacion NVARCHAR(80) NULL,
        estado NVARCHAR(80) NULL,
        recuperado NVARCHAR(80) NULL,
        json_original NVARCHAR(MAX) NOT NULL,
        fecha_captura DATETIME2 NOT NULL CONSTRAINT DF_RegistrosAPI_fecha_captura DEFAULT SYSDATETIME(),
        CONSTRAINT UQ_RegistrosAPI_id_api UNIQUE (id_api)
    );

    CREATE INDEX IX_RegistrosAPI_fecha ON dbo.RegistrosAPI(fecha_reporte_web DESC);
    CREATE INDEX IX_RegistrosAPI_territorio ON dbo.RegistrosAPI(departamento_nombre, municipio_nombre);
END;
GO
