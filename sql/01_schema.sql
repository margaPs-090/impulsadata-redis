-- Creación de tablas de Base de Datos impulsadata
SET NAMES utf8mb4;
CREATE DATABASE IF NOT EXISTS impulsadata CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE impulsadata;

CREATE TABLE IF NOT EXISTS municipios (
    id_municipio INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    provincia VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE,
    telefono VARCHAR(20),
    fecha_registro DATE,
    id_municipio INT,
    FOREIGN KEY (id_municipio) REFERENCES municipios(id_municipio)
);

CREATE TABLE IF NOT EXISTS competencias (
    id_competencia INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    categoria VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS usuario_competencia (
    id_usuario_competencia INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_competencia INT NOT NULL,
    nivel VARCHAR(50),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_competencia) REFERENCES competencias(id_competencia)
);

CREATE TABLE IF NOT EXISTS empresas (
    id_empresa INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    cif VARCHAR(20) UNIQUE,
    email VARCHAR(150),
    telefono VARCHAR(20),
    id_municipio INT,
    FOREIGN KEY (id_municipio) REFERENCES municipios(id_municipio)
);

CREATE TABLE IF NOT EXISTS ofertas_empleo (
    id_oferta INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(150) NOT NULL,
    descripcion TEXT,
    salario DECIMAL(10,2),
    fecha_publicacion DATE,
    estado VARCHAR(50),
    id_empresa INT NOT NULL,
    FOREIGN KEY (id_empresa) REFERENCES empresas(id_empresa)
);

CREATE TABLE IF NOT EXISTS oferta_competencia (
    id_oferta_competencia INT AUTO_INCREMENT PRIMARY KEY,
    id_oferta INT NOT NULL,
    id_competencia INT NOT NULL,
    FOREIGN KEY (id_oferta) REFERENCES ofertas_empleo(id_oferta),
    FOREIGN KEY (id_competencia) REFERENCES competencias(id_competencia)
);

CREATE TABLE IF NOT EXISTS cursos (
    id_curso INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    horas INT,
    plazas INT
);

CREATE TABLE IF NOT EXISTS curso_competencia (
    id_curso_competencia INT AUTO_INCREMENT PRIMARY KEY,
    id_curso INT NOT NULL,
    id_competencia INT NOT NULL,
    FOREIGN KEY (id_curso) REFERENCES cursos(id_curso),
    FOREIGN KEY (id_competencia) REFERENCES competencias(id_competencia)
);

CREATE TABLE IF NOT EXISTS candidaturas (
    id_candidatura INT AUTO_INCREMENT PRIMARY KEY,
    fecha_candidatura DATE,
    estado VARCHAR(50),
    id_usuario INT NOT NULL,
    id_oferta INT NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_oferta) REFERENCES ofertas_empleo(id_oferta)
);
