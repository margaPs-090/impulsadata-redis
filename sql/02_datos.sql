-- ImpulsaData: datos insertados en la base de datos
SET NAMES utf8mb4;
USE impulsadata;

INSERT INTO municipios (id_municipio, nombre, provincia) VALUES
(1, 'Madrid', 'Madrid'),
(2, 'Alcalá de Henares', 'Madrid'),
(3, 'Sevilla', 'Sevilla'),
(4, 'Valencia', 'Valencia'),
(5, 'Toledo', 'Toledo'),
(6, 'Zaragoza', 'Zaragoza');

INSERT INTO competencias (id_competencia, nombre, categoria) VALUES
(1, 'Python', 'Programación'),
(2, 'SQL', 'Datos'),
(3, 'Excel', 'Ofimática'),
(4, 'Análisis de datos', 'Datos'),
(5, 'Comunicación', 'Habilidades blandas'),
(6, 'Atención al cliente', 'Habilidades blandas'),
(7, 'Spark', 'Big Data'),
(8, 'Inglés', 'Idiomas');

INSERT INTO usuarios (id_usuario, nombre, email, telefono, fecha_registro, id_municipio) VALUES
(1, 'Jorge Guerra',      'jorge.guerra@example.com',    '600000001', '2025-01-10', 1),
(2, 'Lucía Benítez',    'lucia.benitez@example.com',  '600000002', '2025-01-15', 3),
(3, 'Pepe García',      'pepe.garcia@example.com',    '600000003', '2025-01-20', 1),
(4, 'Elena Gómez',      'elena.gomez@example.com',    '600000004', '2025-02-01', 4),
(5, 'Calisto Melibea',  'calisto.melibea@example.com','600000005', '2025-02-05', 5),
(6, 'Marta Ruiz',       'marta.ruiz@example.com',     '600000006', '2025-02-10', 2),
(7, 'Andrés Molina',    'andres.molina@example.com',  '600000007', '2025-02-12', 3),
(8, 'Sara Núñez',       'sara.nunez@example.com',     '600000008', '2025-02-20', 6);

INSERT INTO usuario_competencia (id_usuario, id_competencia, nivel) VALUES
(1, 1, 'Avanzado'), (1, 2, 'Intermedio'),
(2, 3, 'Intermedio'), (2, 5, 'Avanzado'),
(3, 1, 'Básico'), (3, 2, 'Básico'),
(4, 4, 'Avanzado'), (4, 2, 'Avanzado'), (4, 8, 'Intermedio'),
(5, 3, 'Básico'),
(6, 6, 'Avanzado'), (6, 5, 'Intermedio'),
(7, 1, 'Intermedio'),
(8, 8, 'Avanzado'), (8, 6, 'Intermedio');

INSERT INTO empresas (id_empresa, nombre, cif, email, telefono, id_municipio) VALUES
(1, 'DataSur',                      'B11111111', 'rrhh@datasur.example.com',        '910000001', 3),
(2, 'Logística Norte',              'B22222222', 'rrhh@logisticanorte.example.com', '910000002', 6),
(3, 'TecnoVega',                    'B33333333', 'rrhh@tecnovega.example.com',      '910000003', 1),
(4, 'Servicios Integrales Levante', 'B44444444', 'rrhh@sil.example.com',            '910000004', 4);

INSERT INTO ofertas_empleo (id_oferta, titulo, descripcion, salario, fecha_publicacion, estado, id_empresa) VALUES
(1, 'Analista de datos junior',    'Análisis y visualización de datos de negocio', 24000.00, '2025-02-01', 'abierta', 1),
(2, 'Técnico de soporte TI',       'Soporte de primer nivel a usuarios',           20000.00, '2025-01-20', 'cerrada', 3),
(3, 'Desarrollador Python',        'Desarrollo de servicios backend',              30000.00, '2025-02-05', 'abierta', 3),
(4, 'Administrativo/a',            'Gestión documental y facturación',             18500.00, '2025-02-08', 'abierta', 2),
(5, 'Ingeniero/a de datos',        'Pipelines de Big Data con Spark',              36000.00, '2025-02-10', 'abierta', 1),
(6, 'Atención al cliente bilingüe','Atención telefónica en español e inglés',      19000.00, '2025-01-25', 'cerrada', 4);

INSERT INTO oferta_competencia (id_oferta, id_competencia) VALUES
(1, 2), (1, 4), (1, 3),
(2, 2),
(3, 1), (3, 2),
(4, 3), (4, 5),
(5, 1), (5, 7), (5, 2),
(6, 6), (6, 8);

INSERT INTO cursos (id_curso, nombre, descripcion, horas, plazas) VALUES
(1, 'Python desde cero',     'Introducción a la programación con Python',  40, 20),
(2, 'SQL para análisis',     'Consultas SQL y análisis de datos',          60, 15),
(3, 'Excel intermedio',      'Fórmulas, tablas dinámicas y gráficos',      30, 30),
(4, 'Big Data con Spark',    'Procesamiento distribuido con Apache Spark', 80, 10),
(5, 'Comunicación efectiva', 'Habilidades de comunicación en el trabajo',  20, 25),
(6, 'Inglés profesional',    'Inglés orientado al entorno laboral',       100, 20);

INSERT INTO curso_competencia (id_curso, id_competencia) VALUES
(1, 1), (2, 2), (2, 4), (3, 3), (4, 7), (5, 5), (6, 8);

INSERT INTO candidaturas (fecha_candidatura, estado, id_usuario, id_oferta) VALUES
('2025-02-10', 'pendiente',  1, 1),
('2025-02-12', 'entrevista', 4, 5),
('2025-02-15', 'contratado', 1, 3),
('2025-02-16', 'pendiente',  3, 3),
('2025-02-18', 'rechazada',  5, 4),
('2025-02-20', 'entrevista', 2, 4),
('2025-02-22', 'pendiente',  7, 3),
('2025-02-25', 'contratado', 6, 6);
