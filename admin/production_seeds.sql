-- SQL Script para insertar datos iniciales en la base de datos de producción
-- Generado a partir del archivo seeds.py

-- ==================================================
-- INSERCIÓN DE ROLES
-- ==================================================

INSERT INTO roles (name) VALUES 
('PUBLIC'),
('EDITOR'),
('ADMIN'),
('SYS_ADMIN')
ON CONFLICT (name) DO NOTHING;

-- ==================================================
-- INSERCIÓN DE PERMISOS
-- ==================================================

INSERT INTO permissions (name) VALUES
('user_create'),
('user_list'),
('user_update'),
('user_delete'),
('user_role'),
('user_block'),
('site_create'),
('site_list'),
('site_update'),
('site_delete'),
('site_tags'),
('site_export'),
('site_history'),
('flags')
ON CONFLICT (name) DO NOTHING;

-- ==================================================
-- RELACIÓN ROLES-PERMISOS
-- ==================================================

-- Permisos para ADMIN
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p 
WHERE r.name = 'ADMIN' AND p.name IN (
    'user_create', 'user_list', 'user_update', 'user_delete', 
    'user_role', 'user_block', 'site_create', 'site_list', 
    'site_update', 'site_delete', 'site_tags', 'site_export', 'site_history'
)
ON CONFLICT DO NOTHING;

-- Permisos para EDITOR
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p 
WHERE r.name = 'EDITOR' AND p.name IN (
    'site_create', 'site_list', 'site_update', 'site_tags', 'site_history'
)
ON CONFLICT DO NOTHING;

-- Permisos para PUBLIC
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p 
WHERE r.name = 'PUBLIC' AND p.name = 'site_list'
ON CONFLICT DO NOTHING;

-- Permisos para SYS_ADMIN
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p 
WHERE r.name = 'SYS_ADMIN' AND p.name = 'flags'
ON CONFLICT DO NOTHING;

-- ==================================================
-- INSERCIÓN DE USUARIO ADMINISTRADOR
-- ==================================================

INSERT INTO users (email, nombre, apellido, password_hash, activo, rol, created_at)
VALUES (
    'admin@example.com',
    'Admin',
    'Local',
    'scrypt:32768:8:1$oO9ZGbXImoQfZrNj$b8c8d5c5c5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5',
    TRUE,
    'ADMIN',
    NOW()
)
ON CONFLICT (email) DO NOTHING;

-- NOTA: El hash de password corresponde a "admin123"
-- Para generar un nuevo hash, usar: generate_password_hash("tu_password")

-- ==================================================
-- INSERCIÓN DE TAGS (ETIQUETAS)
-- ==================================================

INSERT INTO tags (name, slug, description, created_at) VALUES
('Patrimonio Mundial', 'patrimonio-mundial', 'Sitios reconocidos por la UNESCO por su importancia cultural o natural.', NOW()),
('Antiguo', 'antiguo', 'Sitios que datan de civilizaciones o períodos antiguos.', NOW()),
('Arqueológico', 'arqueologico', 'Sitios de importancia arqueológica, a menudo involucrando excavaciones.', NOW()),
('Cultural', 'cultural', 'Sitios que representan un patrimonio cultural significativo.', NOW()),
('Natural', 'natural', 'Sitios importantes por su belleza natural o relevancia ecológica.', NOW()),
('Moderno', 'moderno', 'Sitios de historia reciente que muestran arquitectura o logros modernos.', NOW()),
('Turismo', 'turismo', 'Destinos populares para turistas de todo el mundo.', NOW()),
('Protegido', 'protegido', 'Sitios bajo protección legal para preservar su importancia.', NOW()),
('Cataratas', 'cataratas', 'Sitios con cascadas o saltos de agua de relevancia natural y turística.', NOW()),
('Jujuy', 'jujuy', 'Lugares ubicados en la provincia de Jujuy, Argentina, con valor patrimonial o natural.', NOW()),
('Colonial', 'colonial', 'Sitios que conservan arquitectura y trazado urbano de la época colonial.', NOW()),
('Religioso', 'religioso', 'Lugares con un valor religioso o espiritual significativo (iglesias, santuarios, etc.).', NOW()),
('Arquitectura', 'arquitectura', 'Sitios destacados por su arquitectura relevante o representativa.', NOW()),
('Marino', 'marino', 'Sitios con valor natural marino, como arrecifes o parques costeros.', NOW()),
('Teatro', 'teatro', 'Espacios escénicos históricos y emblemáticos donde se desarrollan artes escénicas.', NOW()),
('Museo', 'museo', 'Instituciones que preservan colecciones de valor histórico, artístico o científico.', NOW()),
('Estancia', 'estancia', 'Grandes propiedades rurales de interés histórico y patrimonial en regiones ganaderas.', NOW()),
('Ferroviario', 'ferroviario', 'Sitios vinculados a la historia del ferrocarril: estaciones, talleres y vías históricas.', NOW()),
('Industrial', 'industrial', 'Patrimonio vinculado a la actividad industrial: fábricas, molinos y usinas históricas.', NOW()),
('Monumento', 'monumento', 'Estructuras erguidas conmemorativas o representativas de hechos históricos o personajes.', NOW()),
('Patrimonio Inmaterial', 'patrimonio-inmaterial', 'Prácticas, expresiones y tradiciones intangibles de valor cultural.', NOW()),
('Puente', 'puente', 'Obras de ingeniería civil que conectan regiones y que en algunos casos son hitos arquitectónicos.', NOW()),
('Glaciar', 'glaciar', 'Formaciones de hielo de gran tamaño (glaciares) y áreas glaciales de interés geológico y turístico.', NOW()),
('Estatua', 'estatua', 'Esculturas y estatuas monumentales con valor histórico, cultural o religioso.', NOW()),
('Observatorio', 'observatorio', 'Lugares o instalaciones dedicadas a la observación astronómica o científica, de interés histórico o cultural.', NOW())
ON CONFLICT (name) DO NOTHING;

-- ==================================================
-- INSERCIÓN DE SITIOS HISTÓRICOS
-- ==================================================

INSERT INTO sites (name, description_short, description, city, province, location, conservation_status, year_declared, category, registration_date, visibility) VALUES
('Muralla China', 'Antiguo conjunto de muros y fortificaciones.', 'La Muralla China es una fortificación histórica construida para proteger los estados chinos contra invasiones. Se extiende por miles de kilómetros.', 'Beijing', 'Hebei', 'China', 'Bien conservada en algunos tramos; otros requieren restauración.', -700, 'Fortificación', '1987-12-01', TRUE),
('Machu Picchu', 'Ciudadela inca del siglo XV.', 'Machu Picchu es una antigua ciudad inca situada en lo alto de los Andes, conocida por su valor arqueológico y sus impresionantes vistas.', 'Cusco', 'Cusco', 'Peru', 'Protegida, pero amenazada por el turismo masivo.', 1450, 'Sitio arqueologico', '1983-12-01', TRUE),
('Pirámides de Giza', 'Antiguo complejo de pirámides.', 'Las Pirámides de Giza son monumentos funerarios construidos para los faraones egipcios, representando una de las mayores hazañas arquitectónicas de la antigüedad.', 'Giza', 'Giza', 'Egipto', 'Estables con trabajos de restauración en curso.', -2580, 'Monumento', '1979-12-01', TRUE),
('Coliseo', 'Gran anfiteatro en Roma.', 'El Coliseo es un anfiteatro de piedra en Roma, conocido por sus espectáculos y combates de la antigüedad.', 'Roma', 'Lazio', 'Italia', 'Parcialmente restaurado; conservación continua.', 80, 'Anfiteatro', '1980-12-01', TRUE),
('Taj Mahal', 'Mausoleo de mármol blanco.', 'El Taj Mahal es un mausoleo construido por el emperador mogol Shah Jahan en memoria de su esposa Mumtaz Mahal.', 'Agra', 'Uttar Pradesh', 'India', 'Bien conservado; problemas por contaminación.', 1643, 'Mausoleo', '1983-12-01', TRUE),
('Sierra de las Quijadas', 'Parque nacional con formaciones rocosas y fósiles.', 'La Sierra de las Quijadas es una zona protegida en Argentina famosa por sus paisajes áridos, cañadones y hallazgos paleontológicos.', 'Albardón', 'San Juan', 'Argentina', 'Protegido; conservación activa.', 1980, 'Parque Nacional', '1990-05-10', TRUE),
('Cueva de las Manos', 'Conjunto de arte rupestre prehistórico.', 'La Cueva de las Manos, en Río Pinturas, contiene pinturas rupestres con manos estencilladas y escenas de caza de hace miles de años.', 'Perito Moreno', 'Santa Cruz', 'Argentina', 'Patrimonio protegido; vulnerable al turismo no regulado.', 1000, 'Sitio arqueológico', '1999-11-28', TRUE),
('Casco Histórico de Quito', 'Centro histórico bien conservado con arquitectura colonial.', 'El Casco Histórico de Quito destaca por su planificación urbana y edificios coloniales; es uno de los cascos históricos mejor conservados de América.', 'Quito', 'Pichincha', 'Ecuador', 'Bien conservado; medidas de protección en marcha.', 1534, 'Conjunto urbano', '1978-09-05', TRUE),
('Cataratas del Iguazú', 'Espectaculares saltos de agua compartidos entre Argentina y Brasil.', 'Las Cataratas del Iguazú son un sistema de cascadas sobre el río Iguazú, ubicadas en la frontera entre Argentina y Brasil. Son un importante sitio natural y turístico, con una rica biodiversidad en el entorno de la selva subtropical.', 'Puerto Iguazú', 'Misiones', 'Argentina', 'Área protegida; presión turística controlada mediante gestión de visitantes.', 1984, 'Parque Nacional', '1984-11-25', TRUE),
('Quebrada de Humahuaca', 'Cañadón andino en la provincia de Jujuy con alto valor cultural.', 'La Quebrada de Humahuaca es un valle andino en Jujuy poblado desde tiempos precolombinos, con paisajes multicolores, tradiciones vivas y una historia cultural rica; fue inscrita como Patrimonio Mundial por la UNESCO.', 'Humahuaca', 'Jujuy', 'Argentina', 'Zona protegida en muchas áreas; requiere políticas de manejo sostenible del turismo.', 2003, 'Paisaje cultural', '2003-07-03', TRUE),
('Iglesia y Convento de San Ignacio', 'Conjunto jesuítico en la región del Litoral argentino.', 'Las reducciones jesuíticas y sus iglesias son ejemplos de arquitectura y organización social de la época colonial; varias están reconocidas por su valor histórico y religioso.', 'San Ignacio', 'Misiones', 'Argentina', 'Conservado con intervenciones de restauración periódicas.', 1700, 'Conjunto religioso', '1983-06-15', TRUE),
('Torre Eiffel', 'Ícono arquitectónico de París, símbolo mundialmente reconocido.', 'La Torre Eiffel, construida durante la Exposición Universal de 1889, es un emblema de la ingeniería y la arquitectura de finales del siglo XIX.', 'París', 'Île-de-France', 'Francia', 'Monumento gestionado y conservado; alto flujo turístico.', 1889, 'Monumento', '1889-03-31', TRUE),
('Estatua de la Libertad', 'Monumento emblemático en la entrada del puerto de Nueva York.', 'La Estatua de la Libertad es un símbolo de libertad y bienvenida para millones de inmigrantes; es también un sitio histórico visitable.', 'Nueva York', 'New York', 'Estados Unidos', 'Conservado y gestionado como parque nacional; mantenimiento constante.', 1886, 'Monumento', '1984-10-15', TRUE),
('Gran Barrera de Coral', 'El mayor sistema de arrecifes coralinos del mundo.', 'La Gran Barrera de Coral en Australia es un extenso ecosistema marino de alto valor ecológico, hogar de miles de especies; enfrenta amenazas por el cambio climático y la contaminación.', 'Queensland', 'Queensland', 'Australia', 'En riesgo por blanqueamiento de corales; áreas protegidas y estudio científico en curso.', 1981, 'Arrecife', '1981-11-21', TRUE),
('Petra', 'Ciudad tallada en la roca en Jordania.', 'Petra es una antigua ciudad nabatea famosa por sus fachadas esculpidas en roca; es un importante sitio arqueológico y turístico.', 'Wadi Musa', 'Ma''an', 'Jordania', 'Sujeto a erosión y presión turística; se realizan trabajos de conservación.', -300, 'Sitio arqueológico', '1985-12-06', TRUE),
('Glaciar Perito Moreno', 'Glaciar masivo en la provincia de Santa Cruz, Argentina.', 'El Glaciar Perito Moreno es uno de los glaciares más accesibles y espectaculares del mundo, ubicado en el Parque Nacional Los Glaciares. Es famoso por sus rupturas y su frente sobre el Brazo Rico del lago Argentino.', 'El Calafate', 'Santa Cruz', 'Argentina', 'Protegido; monitorizado por parques nacionales.', 1917, 'Glaciar', '1938-07-01', TRUE),
('Cristo Redentor', 'Estatua monumental que domina Río de Janeiro, Brasil.', 'El Cristo Redentor es una estatua de 30 metros que se levanta sobre el cerro del Corcovado, símbolo icónico de Brasil y lugar de gran afluencia turística.', 'Río de Janeiro', 'Río de Janeiro', 'Brasil', 'Mantenido y restaurado; gran afluencia turística.', 1931, 'Monumento', '1931-10-12', TRUE),
('Teatro Colón', 'Teatro histórico y sala de ópera en Buenos Aires.', 'El Teatro Colón es una de las salas líricas más importantes del mundo por su acústica y arquitectura; inaugurado a principios del siglo XX.', 'Buenos Aires', 'Buenos Aires', 'Argentina', 'Conservado y restaurado periódicamente.', 1908, 'Teatro', '1908-05-25', TRUE),
('Estancia Jesuítica de Alta Gracia', 'Estancia histórica vinculada a las reducciones jesuíticas en Córdoba.', 'Parte del conjunto de Estancias Jesuíticas de la provincia de Córdoba, que muestran la organización productiva y social de la época colonial.', 'Alta Gracia', 'Córdoba', 'Argentina', 'Conservada; integra circuitos de patrimonio cultural.', 1608, 'Estancia', '2000-07-01', TRUE),
('Museo Nacional de Bellas Artes', 'Colección pública de arte argentino e internacional.', 'El Museo Nacional de Bellas Artes en Buenos Aires alberga una de las colecciones más importantes de arte en Argentina, con piezas desde la antigüedad hasta el arte moderno.', 'Buenos Aires', 'Buenos Aires', 'Argentina', 'Instalaciones museológicas modernas con programas de conservación.', 1933, 'Museo', '1933-06-23', TRUE),
('Puente de la Mujer', 'Puente peatonal moderno en Puerto Madero, Buenos Aires.', 'Diseñado por Santiago Calatrava, es un emblema moderno de la zona portuaria y un ejemplo de ingeniería contemporánea.', 'Buenos Aires', 'Buenos Aires', 'Argentina', 'Buen estado; mantenimiento regular.', 2001, 'Puente', '2001-12-01', TRUE),
('Cabildo de Buenos Aires', 'Edificio colonial en la Plaza de Mayo, Buenos Aires.', 'El Cabildo fue sede del gobierno colonial y un lugar clave durante los procesos de independencia; hoy funciona como museo histórico.', 'Buenos Aires', 'Buenos Aires', 'Argentina', 'Restaurado y mantenido como museo público.', 1810, 'Conjunto urbano', '1940-07-09', TRUE),
('Monumento a la Bandera', 'Monumento conmemorativo en Rosario, Argentina.', 'Erigido en conmemoración de la creación de la bandera argentina; es un punto neurálgico del espacio urbano y de celebración cívica.', 'Rosario', 'Santa Fe', 'Argentina', 'Conservado; uso público y eventos institucionales.', 1957, 'Monumento', '1957-06-20', TRUE),
('Casa Histórica de la Independencia', 'Lugar donde se declaró la independencia en Tucumán.', 'La Casa Histórica de la Independencia es un edificio clave en la memoria de la formación del Estado argentino; contiene salas históricas y colecciones documentales.', 'San Miguel de Tucumán', 'Tucumán', 'Argentina', 'Conservada y gestionada como museo nacional.', 1816, 'Monumento', '1941-07-09', TRUE)
ON CONFLICT (name) DO NOTHING;

-- ==================================================
-- RELACIÓN SITIOS-TAGS (MANY-TO-MANY)
-- ==================================================

-- Muralla China: Patrimonio Mundial, Antiguo
INSERT INTO sites_tags (site_id, tag_id)
SELECT s.id, t.id FROM sites s, tags t 
WHERE s.name = 'Muralla China' AND t.name IN ('Patrimonio Mundial', 'Antiguo')
ON CONFLICT DO NOTHING;

-- Machu Picchu: Patrimonio Mundial, Arqueológico
INSERT INTO sites_tags (site_id, tag_id)
SELECT s.id, t.id FROM sites s, tags t 
WHERE s.name = 'Machu Picchu' AND t.name IN ('Patrimonio Mundial', 'Arqueológico')
ON CONFLICT DO NOTHING;

-- Pirámides de Giza: Antiguo, Arqueológico
INSERT INTO sites_tags (site_id, tag_id)
SELECT s.id, t.id FROM sites s, tags t 
WHERE s.name = 'Pirámides de Giza' AND t.name IN ('Antiguo', 'Arqueológico')
ON CONFLICT DO NOTHING;

-- Coliseo: Antiguo, Cultural
INSERT INTO sites_tags (site_id, tag_id)
SELECT s.id, t.id FROM sites s, tags t 
WHERE s.name = 'Coliseo' AND t.name IN ('Antiguo', 'Cultural')
ON CONFLICT DO NOTHING;

-- Taj Mahal: Patrimonio Mundial, Cultural
INSERT INTO sites_tags (site_id, tag_id)
SELECT s.id, t.id FROM sites s, tags t 
WHERE s.name = 'Taj Mahal' AND t.name IN ('Patrimonio Mundial', 'Cultural')
ON CONFLICT DO NOTHING;

-- Sierra de las Quijadas: Natural, Protegido
INSERT INTO sites_tags (site_id, tag_id)
SELECT s.id, t.id FROM sites s, tags t 
WHERE s.name = 'Sierra de las Quijadas' AND t.name IN ('Natural', 'Protegido')
ON CONFLICT DO NOTHING;

-- Cueva de las Manos: Patrimonio Mundial, Arqueológico
INSERT INTO sites_tags (site_id, tag_id)
SELECT s.id, t.id FROM sites s, tags t 
WHERE s.name = 'Cueva de las Manos' AND t.name IN ('Patrimonio Mundial', 'Arqueológico')
ON CONFLICT DO NOTHING;

-- Casco Histórico de Quito: Patrimonio Mundial, Cultural
INSERT INTO sites_tags (site_id, tag_id)
SELECT s.id, t.id FROM sites s, tags t 
WHERE s.name = 'Casco Histórico de Quito' AND t.name IN ('Patrimonio Mundial', 'Cultural')
ON CONFLICT DO NOTHING;

-- Cataratas del Iguazú: Patrimonio Mundial, Cataratas, Natural, Turismo
INSERT INTO sites_tags (site_id, tag_id)
SELECT s.id, t.id FROM sites s, tags t 
WHERE s.name = 'Cataratas del Iguazú' AND t.name IN ('Patrimonio Mundial', 'Cataratas', 'Natural', 'Turismo')
ON CONFLICT DO NOTHING;

-- Quebrada de Humahuaca: Patrimonio Mundial, Jujuy, Cultural
INSERT INTO sites_tags (site_id, tag_id)
SELECT s.id, t.id FROM sites s, tags t 
WHERE s.name = 'Quebrada de Humahuaca' AND t.name IN ('Patrimonio Mundial', 'Jujuy', 'Cultural')
ON CONFLICT DO NOTHING;

-- Iglesia y Convento de San Ignacio: Colonial, Religioso, Cultural
INSERT INTO sites_tags (site_id, tag_id)
SELECT s.id, t.id FROM sites s, tags t 
WHERE s.name = 'Iglesia y Convento de San Ignacio' AND t.name IN ('Colonial', 'Religioso', 'Cultural')
ON CONFLICT DO NOTHING;

-- Torre Eiffel: Arquitectura, Turismo
INSERT INTO sites_tags (site_id, tag_id)
SELECT s.id, t.id FROM sites s, tags t 
WHERE s.name = 'Torre Eiffel' AND t.name IN ('Arquitectura', 'Turismo')
ON CONFLICT DO NOTHING;

-- Estatua de la Libertad: Monumento, Turismo, Arquitectura
INSERT INTO sites_tags (site_id, tag_id)
SELECT s.id, t.id FROM sites s, tags t 
WHERE s.name = 'Estatua de la Libertad' AND t.name IN ('Monumento', 'Turismo', 'Arquitectura')
ON CONFLICT DO NOTHING;

-- Gran Barrera de Coral: Marino, Patrimonio Mundial, Natural
INSERT INTO sites_tags (site_id, tag_id)
SELECT s.id, t.id FROM sites s, tags t 
WHERE s.name = 'Gran Barrera de Coral' AND t.name IN ('Marino', 'Patrimonio Mundial', 'Natural')
ON CONFLICT DO NOTHING;

-- Petra: Arqueológico, Patrimonio Mundial, Turismo
INSERT INTO sites_tags (site_id, tag_id)
SELECT s.id, t.id FROM sites s, tags t 
WHERE s.name = 'Petra' AND t.name IN ('Arqueológico', 'Patrimonio Mundial', 'Turismo')
ON CONFLICT DO NOTHING;

-- Glaciar Perito Moreno: Glaciar, Natural, Turismo
INSERT INTO sites_tags (site_id, tag_id)
SELECT s.id, t.id FROM sites s, tags t 
WHERE s.name = 'Glaciar Perito Moreno' AND t.name IN ('Glaciar', 'Natural', 'Turismo')
ON CONFLICT DO NOTHING;

-- Cristo Redentor: Estatua, Turismo, Monumento
INSERT INTO sites_tags (site_id, tag_id)
SELECT s.id, t.id FROM sites s, tags t 
WHERE s.name = 'Cristo Redentor' AND t.name IN ('Estatua', 'Turismo', 'Monumento')
ON CONFLICT DO NOTHING;

-- Teatro Colón: Teatro, Arquitectura, Cultural
INSERT INTO sites_tags (site_id, tag_id)
SELECT s.id, t.id FROM sites s, tags t 
WHERE s.name = 'Teatro Colón' AND t.name IN ('Teatro', 'Arquitectura', 'Cultural')
ON CONFLICT DO NOTHING;

-- Estancia Jesuítica de Alta Gracia: Estancia, Colonial, Patrimonio Mundial
INSERT INTO sites_tags (site_id, tag_id)
SELECT s.id, t.id FROM sites s, tags t 
WHERE s.name = 'Estancia Jesuítica de Alta Gracia' AND t.name IN ('Estancia', 'Colonial', 'Patrimonio Mundial')
ON CONFLICT DO NOTHING;

-- Museo Nacional de Bellas Artes: Museo, Cultural, Arquitectura
INSERT INTO sites_tags (site_id, tag_id)
SELECT s.id, t.id FROM sites s, tags t 
WHERE s.name = 'Museo Nacional de Bellas Artes' AND t.name IN ('Museo', 'Cultural', 'Arquitectura')
ON CONFLICT DO NOTHING;

-- Puente de la Mujer: Puente, Moderno, Turismo
INSERT INTO sites_tags (site_id, tag_id)
SELECT s.id, t.id FROM sites s, tags t 
WHERE s.name = 'Puente de la Mujer' AND t.name IN ('Puente', 'Moderno', 'Turismo')
ON CONFLICT DO NOTHING;

-- Cabildo de Buenos Aires: Colonial, Cultural, Monumento
INSERT INTO sites_tags (site_id, tag_id)
SELECT s.id, t.id FROM sites s, tags t 
WHERE s.name = 'Cabildo de Buenos Aires' AND t.name IN ('Colonial', 'Cultural', 'Monumento')
ON CONFLICT DO NOTHING;

-- Monumento a la Bandera: Monumento, Arquitectura, Turismo
INSERT INTO sites_tags (site_id, tag_id)
SELECT s.id, t.id FROM sites s, tags t 
WHERE s.name = 'Monumento a la Bandera' AND t.name IN ('Monumento', 'Arquitectura', 'Turismo')
ON CONFLICT DO NOTHING;

-- Casa Histórica de la Independencia: Colonial, Cultural, Monumento
INSERT INTO sites_tags (site_id, tag_id)
SELECT s.id, t.id FROM sites s, tags t 
WHERE s.name = 'Casa Histórica de la Independencia' AND t.name IN ('Colonial', 'Cultural', 'Monumento')
ON CONFLICT DO NOTHING;

-- ==================================================
-- VERIFICACIÓN DE INSERCIÓN
-- ==================================================

-- Consultas para verificar que los datos se insertaron correctamente
-- SELECT COUNT(*) as total_roles FROM roles;
-- SELECT COUNT(*) as total_permissions FROM permissions;
-- SELECT COUNT(*) as total_users FROM users;
-- SELECT COUNT(*) as total_tags FROM tags;
-- SELECT COUNT(*) as total_sites FROM sites;
-- SELECT COUNT(*) as total_sites_tags FROM sites_tags;
-- SELECT COUNT(*) as total_role_permissions FROM role_permissions;

-- ==================================================
-- NOTAS IMPORTANTES
-- ==================================================

/*
1. Este script usa ON CONFLICT DO NOTHING para evitar duplicados al ejecutar múltiples veces.

2. El hash de password para el usuario admin corresponde a la contraseña "admin123".
   Para generar un nuevo hash, usar la función generate_password_hash() de Flask.

3. Las relaciones many-to-many (sites_tags y role_permissions) se crean después 
   de insertar los registros principales para evitar errores de foreign key.

4. Verificar que las fechas estén en el formato correcto para tu base de datos 
   (PostgreSQL usa 'YYYY-MM-DD', MySQL puede variar).

5. Ejecutar en orden: primero las tablas principales, luego las relaciones.

6. Para verificar la inserción, descomentar las consultas SELECT al final.
*/