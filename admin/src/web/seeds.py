from select import select

# from core.database import db
from src.core.database import db
from src.core.featureFlags.flag import FeatureFlag
from src.core import historicalSites
from src.core.historicalSites.site import Site
from src.core.historicalSites.tags.tag import Tag
from datetime import date
from src.core.users.user import User, UserRole
from src.core.permissions.permission import Permission, UserPermission, Role
from werkzeug.security import generate_password_hash


def run():
    print("Seeding database with initial data...")

    feature_flags_seed()
    print("Feature flags creados o actualizados.")
    tags_data = [
        {
            "name": "Patrimonio Mundial",
            "slug": "patrimonio-mundial",
            "description": "Sitios reconocidos por la UNESCO por su importancia cultural o natural.",
        },
        {
            "name": "Antiguo",
            "slug": "antiguo",
            "description": "Sitios que datan de civilizaciones o períodos antiguos.",
        },
        {
            "name": "Arqueológico",
            "slug": "arqueologico",
            "description": "Sitios de importancia arqueológica, a menudo involucrando excavaciones.",
        },
        {
            "name": "Cultural",
            "slug": "cultural",
            "description": "Sitios que representan un patrimonio cultural significativo.",
        },
        {
            "name": "Natural",
            "slug": "natural",
            "description": "Sitios importantes por su belleza natural o relevancia ecológica.",
        },
        {
            "name": "Moderno",
            "slug": "moderno",
            "description": "Sitios de historia reciente que muestran arquitectura o logros modernos.",
        },
        {
            "name": "Turismo",
            "slug": "turismo",
            "description": "Destinos populares para turistas de todo el mundo.",
        },
        {
            "name": "Protegido",
            "slug": "protegido",
            "description": "Sitios bajo protección legal para preservar su importancia.",
        },
        {
            "name": "Cataratas",
            "slug": "cataratas",
            "description": "Sitios con cascadas o saltos de agua de relevancia natural y turística.",
        },
        {
            "name": "Jujuy",
            "slug": "jujuy",
            "description": "Lugares ubicados en la provincia de Jujuy, Argentina, con valor patrimonial o natural.",
        },
        {
            "name": "Colonial",
            "slug": "colonial",
            "description": "Sitios que conservan arquitectura y trazado urbano de la época colonial.",
        },
        {
            "name": "Religioso",
            "slug": "religioso",
            "description": "Lugares con un valor religioso o espiritual significativo (iglesias, santuarios, etc.).",
        },
        {
            "name": "Arquitectura",
            "slug": "arquitectura",
            "description": "Sitios destacados por su arquitectura relevante o representativa.",
        },
        {
            "name": "Marino",
            "slug": "marino",
            "description": "Sitios con valor natural marino, como arrecifes o parques costeros.",
        },
        {
            "name": "Teatro",
            "slug": "teatro",
            "description": "Espacios escénicos históricos y emblemáticos donde se desarrollan artes escénicas.",
        },
        {
            "name": "Museo",
            "slug": "museo",
            "description": "Instituciones que preservan colecciones de valor histórico, artístico o científico.",
        },
        {
            "name": "Estancia",
            "slug": "estancia",
            "description": "Grandes propiedades rurales de interés histórico y patrimonial en regiones ganaderas.",
        },
        {
            "name": "Ferroviario",
            "slug": "ferroviario",
            "description": "Sitios vinculados a la historia del ferrocarril: estaciones, talleres y vías históricas.",
        },
        {
            "name": "Industrial",
            "slug": "industrial",
            "description": "Patrimonio vinculado a la actividad industrial: fábricas, molinos y usinas históricas.",
        },
        {
            "name": "Monumento",
            "slug": "monumento",
            "description": "Estructuras erguidas conmemorativas o representativas de hechos históricos o personajes.",
        },
        {
            "name": "Patrimonio Inmaterial",
            "slug": "patrimonio-inmaterial",
            "description": "Prácticas, expresiones y tradiciones intangibles de valor cultural.",
        },
        {
            "name": "Puente",
            "slug": "puente",
            "description": "Obras de ingeniería civil que conectan regiones y que en algunos casos son hitos arquitectónicos.",
        },
        {
            "name": "Glaciar",
            "slug": "glaciar",
            "description": "Formaciones de hielo de gran tamaño (glaciares) y áreas glaciales de interés geológico y turístico.",
        },
        {
            "name": "Estatua",
            "slug": "estatua",
            "description": "Esculturas y estatuas monumentales con valor histórico, cultural o religioso.",
        },
        {
            "name": "Observatorio",
            "slug": "observatorio",
            "description": "Lugares o instalaciones dedicadas a la observación astronómica o científica, de interés histórico o cultural.",
        },
    ]

    for tag_data in tags_data:
        existing_tag = historicalSites.tags.get_tag_by_name(tag_data["name"])
        if not existing_tag:
            historicalSites.tags.create_tag(**tag_data)
            print(f"Tag agregado: {tag_data['name']}")
        else:
            print(f"El tag ya existe: {tag_data['name']}")

    sites_data = [
        {
            "name": "Muralla China",
            "description_short": "Antiguo conjunto de muros y fortificaciones.",
            "description": "La Muralla China es una fortificación histórica construida para proteger los estados chinos contra invasiones. Se extiende por miles de kilómetros.",
            "city": "Beijing",
            "province": "Hebei",
            "location": "116.4074 39.9042",
            "conservation_status": "regular",
            "year_declared": -700,
            "category": "patrimonio_mundial",
            "registration_date": date(1987, 12, 1),
            "visibility": True,
            "tags": ["Patrimonio Mundial", "Antiguo"],
        },
        {
            "name": "Machu Picchu",
            "description_short": "Ciudadela inca del siglo XV.",
            "description": "Machu Picchu es una antigua ciudad inca situada en lo alto de los Andes, conocida por su valor arqueológico y sus impresionantes vistas.",
            "city": "Cusco",
            "province": "Cusco",
            "location": "-72.5450 -13.1631",
            "conservation_status": "bueno",
            "year_declared": 1450,
            "category": "sitio_historico",
            "registration_date": date(1983, 12, 1),
            "visibility": True,
            "tags": ["Patrimonio Mundial", "Arqueológico"],
        },
        {
            "name": "Pirámides de Giza",
            "description_short": "Antiguo complejo de pirámides.",
            "description": "Las Pirámides de Giza son monumentos funerarios construidos para los faraones egipcios, representando una de las mayores hazañas arquitectónicas de la antigüedad.",
            "city": "Giza",
            "province": "Giza",
            "location": "31.1342 29.9792",
            "conservation_status": "bueno",
            "year_declared": -2580,
            "category": "monumento_nacional",
            "registration_date": date(1979, 12, 1),
            "visibility": True,
            "tags": ["Antiguo", "Arqueológico"],
        },
        {
            "name": "Coliseo",
            "description_short": "Gran anfiteatro en Roma.",
            "description": "El Coliseo es un anfiteatro de piedra en Roma, conocido por sus espectáculos y combates de la antigüedad.",
            "city": "Roma",
            "province": "Lazio",
            "location": "12.4924 41.8902",
            "conservation_status": "en_restauracion",
            "year_declared": 80,
            "category": "monumento_nacional",
            "registration_date": date(1980, 12, 1),
            "visibility": True,
            "tags": ["Antiguo", "Cultural"],
        },
        {
            "name": "Taj Mahal",
            "description_short": "Mausoleo de mármol blanco.",
            "description": "El Taj Mahal es un mausoleo construido por el emperador mogol Shah Jahan en memoria de su esposa Mumtaz Mahal.",
            "city": "Agra",
            "province": "Uttar Pradesh",
            "location": "78.0421 27.1751",
            "conservation_status": "bueno",
            "year_declared": 1643,
            "category": "patrimonio_mundial",
            "registration_date": date(1983, 12, 1),
            "visibility": True,
            "tags": ["Patrimonio Mundial", "Cultural"],
        },
        {
            "name": "Sierra de las Quijadas",
            "description_short": "Parque nacional con formaciones rocosas y fósiles.",
            "description": "La Sierra de las Quijadas es una zona protegida en Argentina famosa por sus paisajes áridos, cañadones y hallazgos paleontológicos.",
            "city": "Albardón",
            "province": "San Juan",
            "location": "-67.1333 -32.5333",
            "conservation_status": "excelente",
            "year_declared": 1980,
            "category": "sitio_historico",
            "registration_date": date(1990, 5, 10),
            "visibility": True,
            "tags": ["Natural", "Protegido"],
        },
        {
            "name": "Cueva de las Manos",
            "description_short": "Conjunto de arte rupestre prehistórico.",
            "description": "La Cueva de las Manos, en Río Pinturas, contiene pinturas rupestres con manos estencilladas y escenas de caza de hace miles de años.",
            "city": "Perito Moreno",
            "province": "Santa Cruz",
            "location": "-71.1544 -47.1547",
            "conservation_status": "regular",
            "year_declared": 1000,
            "category": "sitio_historico",
            "registration_date": date(1999, 11, 28),
            "visibility": True,
            "tags": ["Patrimonio Mundial", "Arqueológico"],
        },
        {
            "name": "Casco Histórico de Quito",
            "description_short": "Centro histórico bien conservado con arquitectura colonial.",
            "description": "El Casco Histórico de Quito destaca por su planificación urbana y edificios coloniales; es uno de los cascos históricos mejor conservados de América.",
            "city": "Quito",
            "province": "Pichincha",
            "location": "-78.5125 -0.2201",
            "conservation_status": "bueno",
            "year_declared": 1534,
            "category": "patrimonio_mundial",
            "registration_date": date(1978, 9, 5),
            "visibility": True,
            "tags": ["Patrimonio Mundial", "Cultural"],
        },
        {
            "name": "Cataratas del Iguazú",
            "description_short": "Espectaculares saltos de agua compartidos entre Argentina y Brasil.",
            "description": "Las Cataratas del Iguazú son un sistema de cascadas sobre el río Iguazú, ubicadas en la frontera entre Argentina y Brasil. Son un importante sitio natural y turístico, con una rica biodiversidad en el entorno de la selva subtropical.",
            "city": "Puerto Iguazú",
            "province": "Misiones",
            "location": "-54.4367 -25.6953",
            "conservation_status": "excelente",
            "year_declared": 1984,
            "category": "patrimonio_mundial",
            "registration_date": date(1984, 11, 25),
            "visibility": True,
            "tags": ["Patrimonio Mundial", "Cataratas", "Natural", "Turismo"],
        },
        {
            "name": "Quebrada de Humahuaca",
            "description_short": "Cañadón andino en la provincia de Jujuy con alto valor cultural.",
            "description": "La Quebrada de Humahuaca es un valle andino en Jujuy poblado desde tiempos precolombinos, con paisajes multicolores, tradiciones vivas y una historia cultural rica; fue inscrita como Patrimonio Mundial por la UNESCO.",
            "city": "Humahuaca",
            "province": "Jujuy",
            "location": "-65.3486 -23.2053",
            "conservation_status": "bueno",
            "year_declared": 2003,
            "category": "patrimonio_mundial",
            "registration_date": date(2003, 7, 3),
            "visibility": True,
            "tags": ["Patrimonio Mundial", "Jujuy", "Cultural"],
        },
        {
            "name": "Iglesia y Convento de San Ignacio",
            "description_short": "Conjunto jesuítico en la región del Litoral argentino.",
            "description": "Las reducciones jesuíticas y sus iglesias son ejemplos de arquitectura y organización social de la época colonial; varias están reconocidas por su valor histórico y religioso.",
            "city": "San Ignacio",
            "province": "Misiones",
            "location": "-55.5331 -27.2583",
            "conservation_status": "bueno",
            "year_declared": 1700,
            "category": "monumento_historico_nacional",
            "registration_date": date(1983, 6, 15),
            "visibility": True,
            "tags": ["Colonial", "Religioso", "Cultural"],
        },
        {
            "name": "Torre Eiffel",
            "description_short": "Ícono arquitectónico de París, símbolo mundialmente reconocido.",
            "description": "La Torre Eiffel, construida durante la Exposición Universal de 1889, es un emblema de la ingeniería y la arquitectura de finales del siglo XIX.",
            "city": "París",
            "province": "Île-de-France",
            "location": "2.2945 48.8584",
            "conservation_status": "excelente",
            "year_declared": 1889,
            "category": "monumento_nacional",
            "registration_date": date(1889, 3, 31),
            "visibility": True,
            "tags": ["Arquitectura", "Turismo"],
        },
        {
            "name": "Estatua de la Libertad",
            "description_short": "Monumento emblemático en la entrada del puerto de Nueva York.",
            "description": "La Estatua de la Libertad es un símbolo de libertad y bienvenida para millones de inmigrantes; es también un sitio histórico visitable.",
            "city": "Nueva York",
            "province": "New York",
            "location": "-74.0445 40.6892",
            "conservation_status": "excelente",
            "year_declared": 1886,
            "category": "monumento_nacional",
            "registration_date": date(1984, 10, 15),
            "visibility": True,
            "tags": ["Monumento", "Turismo", "Arquitectura"],
        },
        {
            "name": "Gran Barrera de Coral",
            "description_short": "El mayor sistema de arrecifes coralinos del mundo.",
            "description": "La Gran Barrera de Coral en Australia es un extenso ecosistema marino de alto valor ecológico, hogar de miles de especies; enfrenta amenazas por el cambio climático y la contaminación.",
            "city": "Queensland",
            "province": "Queensland",
            "location": "145.7781 -16.2393",
            "conservation_status": "critico",
            "year_declared": 1981,
            "category": "patrimonio_mundial",
            "registration_date": date(1981, 11, 21),
            "visibility": True,
            "tags": ["Marino", "Patrimonio Mundial", "Natural"],
        },
        {
            "name": "Petra",
            "description_short": "Ciudad tallada en la roca en Jordania.",
            "description": "Petra es una antigua ciudad nabatea famosa por sus fachadas esculpidas en roca; es un importante sitio arqueológico y turístico.",
            "city": "Wadi Musa",
            "province": "Ma'an",
            "location": "35.4444 30.3285",
            "conservation_status": "regular",
            "year_declared": -300,
            "category": "sitio_historico",
            "registration_date": date(1985, 12, 6),
            "visibility": True,
            "tags": ["Arqueológico", "Patrimonio Mundial", "Turismo"],
        },
        {
            "name": "Glaciar Perito Moreno",
            "description_short": "Glaciar masivo en la provincia de Santa Cruz, Argentina.",
            "description": "El Glaciar Perito Moreno es uno de los glaciares más accesibles y espectaculares del mundo, ubicado en el Parque Nacional Los Glaciares. Es famoso por sus rupturas y su frente sobre el Brazo Rico del lago Argentino.",
            "city": "El Calafate",
            "province": "Santa Cruz",
            "location": "-73.0328 -50.4688",
            "conservation_status": "bueno",
            "year_declared": 1917,
            "category": "sitio_historico",
            "registration_date": date(1938, 7, 1),
            "visibility": True,
            "tags": ["Glaciar", "Natural", "Turismo"],
        },
        {
            "name": "Cristo Redentor",
            "description_short": "Estatua monumental que domina Río de Janeiro, Brasil.",
            "description": "El Cristo Redentor es una estatua de 30 metros que se levanta sobre el cerro del Corcovado, símbolo icónico de Brasil y lugar de gran afluencia turística.",
            "city": "Río de Janeiro",
            "province": "Río de Janeiro",
            "location": "-43.2105 -22.9519",
            "conservation_status": "bueno",
            "year_declared": 1931,
            "category": "monumento_nacional",
            "registration_date": date(1931, 10, 12),
            "visibility": True,
            "tags": ["Estatua", "Turismo", "Monumento"],
        },
        {
            "name": "Teatro Colón",
            "description_short": "Teatro histórico y sala de ópera en Buenos Aires.",
            "description": "El Teatro Colón es una de las salas líricas más importantes del mundo por su acústica y arquitectura; inaugurado a principios del siglo XX.",
            "city": "Buenos Aires",
            "province": "Buenos Aires",
            "location": "-58.3831 -34.6010",
            "conservation_status": "excelente",
            "year_declared": 1908,
            "category": "bien_cultural",
            "registration_date": date(1908, 5, 25),
            "visibility": True,
            "tags": ["Teatro", "Arquitectura", "Cultural"],
        },
        {
            "name": "Estancia Jesuítica de Alta Gracia",
            "description_short": "Estancia histórica vinculada a las reducciones jesuíticas en Córdoba.",
            "description": "Parte del conjunto de Estancias Jesuíticas de la provincia de Córdoba, que muestran la organización productiva y social de la época colonial.",
            "city": "Alta Gracia",
            "province": "Córdoba",
            "location": "-64.4297 -31.6531",
            "conservation_status": "bueno",
            "year_declared": 1608,
            "category": "monumento_historico_nacional",
            "registration_date": date(2000, 7, 1),
            "visibility": True,
            "tags": ["Estancia", "Colonial", "Patrimonio Mundial"],
        },
        {
            "name": "Museo Nacional de Bellas Artes",
            "description_short": "Colección pública de arte argentino e internacional.",
            "description": "El Museo Nacional de Bellas Artes en Buenos Aires alberga una de las colecciones más importantes de arte en Argentina, con piezas desde la antigüedad hasta el arte moderno.",
            "city": "Buenos Aires",
            "province": "Buenos Aires",
            "location": "-58.3930 -34.5842",
            "conservation_status": "excelente",
            "year_declared": 1933,
            "category": "bien_cultural",
            "registration_date": date(1933, 6, 23),
            "visibility": True,
            "tags": ["Museo", "Cultural", "Arquitectura"],
        },
        {
            "name": "Puente de la Mujer",
            "description_short": "Puente peatonal moderno en Puerto Madero, Buenos Aires.",
            "description": "Diseñado por Santiago Calatrava, es un emblema moderno de la zona portuaria y un ejemplo de ingeniería contemporánea.",
            "city": "Buenos Aires",
            "province": "Buenos Aires",
            "location": "-58.3626 -34.6118",
            "conservation_status": "excelente",
            "year_declared": 2001,
            "category": "bien_cultural",
            "registration_date": date(2001, 12, 1),
            "visibility": True,
            "tags": ["Puente", "Moderno", "Turismo"],
        },
        {
            "name": "Cabildo de Buenos Aires",
            "description_short": "Edificio colonial en la Plaza de Mayo, Buenos Aires.",
            "description": "El Cabildo fue sede del gobierno colonial y un lugar clave durante los procesos de independencia; hoy funciona como museo histórico.",
            "city": "Buenos Aires",
            "province": "Buenos Aires",
            "location": "-58.3721 -34.6076",
            "conservation_status": "excelente",
            "year_declared": 1810,
            "category": "monumento_historico_nacional",
            "registration_date": date(1940, 7, 9),
            "visibility": True,
            "tags": ["Colonial", "Cultural", "Monumento"],
        },
        {
            "name": "Monumento a la Bandera",
            "description_short": "Monumento conmemorativo en Rosario, Argentina.",
            "description": "Erigido en conmemoración de la creación de la bandera argentina; es un punto neurálgico del espacio urbano y de celebración cívica.",
            "city": "Rosario",
            "province": "Santa Fe",
            "location": "-60.6393 -32.9442",
            "conservation_status": "bueno",
            "year_declared": 1957,
            "category": "monumento_nacional",
            "registration_date": date(1957, 6, 20),
            "visibility": True,
            "tags": ["Monumento", "Arquitectura", "Turismo"],
        },
        {
            "name": "Casa Histórica de la Independencia",
            "description_short": "Lugar donde se declaró la independencia en Tucumán.",
            "description": "La Casa Histórica de la Independencia es un edificio clave en la memoria de la formación del Estado argentino; contiene salas históricas y colecciones documentales.",
            "city": "San Miguel de Tucumán",
            "province": "Tucumán",
            "location": "-65.2226 -26.8241",
            "conservation_status": "bueno",
            "year_declared": 1816,
            "category": "monumento_historico_nacional",
            "registration_date": date(1941, 7, 9),
            "visibility": True,
            "tags": ["Colonial", "Cultural", "Monumento"],
        },
    ]

    for site_data in sites_data:
        existing_site = historicalSites.get_site_by_name(site_data["name"])
        if not existing_site:
            # Extraer lista de nombres de tags antes de crear el site
            tag_names = site_data.pop("tags", [])
            site = historicalSites.create_site(**site_data)
            # Si llegaron nombres de tags, buscar los objetos Tag y asignarlos
            if tag_names:
                tag_objs = []
                for tn in tag_names:
                    t = Tag.query.filter(Tag.name == tn).first()
                    if t:
                        tag_objs.append(t)
                if tag_objs:
                    historicalSites.asignar_tags_a_sitio(site, tag_objs)
            print(f"Added site: {site.name}")
        else:
            # Si el site ya existe y vienen tags, actualizar asignación
            tag_names = site_data.get("tags", [])
            if tag_names:
                tag_objs = []
                for tn in tag_names:
                    t = Tag.query.filter(Tag.name == tn).first()
                    if t:
                        tag_objs.append(t)
                if tag_objs:
                    historicalSites.asignar_tags_a_sitio(existing_site, tag_objs)
            print(f"Site already exists: {site_data['name']}")

    print("Database seeding complete.")


def users():
    """Crea un usuario administrador por defecto si no existe y usuarios de prueba."""
    # Crear admin si no existe
    exists = User.query.filter_by(email="admin@example.com").first()
    if not exists:
        admin = User(
            email="admin@example.com",
            nombre="Admin",
            apellido="Local",
            password_hash=generate_password_hash("admin123"),
            activo=True,
            rol=UserRole.SYS_ADMIN,
        )
        db.session.add(admin)
        print("Admin creado: admin@example.com / admin123")
    else:
        print("El admin ya existe.")

    # Crear 30 usuarios de prueba
    test_users = []

    # 10 administradores (algunos inactivos)
    for i in range(1, 11):
        email = f"admin{i}@example.com"
        if not User.query.filter_by(email=email).first():
            test_users.append(
                User(
                    email=email,
                    nombre=f"Admin{i}",
                    apellido=f"Apellido{i}",
                    password_hash=generate_password_hash("password123"),
                    activo=i % 3 != 0,  # Cada tercer usuario inactivo
                    rol=UserRole.ADMIN,
                )
            )

    # 10 editores (algunos inactivos)
    for i in range(1, 11):
        email = f"editor{i}@example.com"
        if not User.query.filter_by(email=email).first():
            test_users.append(
                User(
                    email=email,
                    nombre=f"Editor{i}",
                    apellido=f"Apellido{i}",
                    password_hash=generate_password_hash("password123"),
                    activo=i % 4 != 0,  # Cada cuarto usuario inactivo
                    rol=UserRole.EDITOR,
                )
            )

    # 10 usuarios públicos (algunos inactivos)
    for i in range(1, 11):
        email = f"user{i}@example.com"
        if not User.query.filter_by(email=email).first():
            test_users.append(
                User(
                    email=email,
                    nombre=f"Usuario{i}",
                    apellido=f"Apellido{i}",
                    password_hash=generate_password_hash("password123"),
                    activo=i % 5 != 0,  # Cada quinto usuario inactivo
                    rol=UserRole.PUBLIC,
                )
            )

    if test_users:
        db.session.add_all(test_users)
        db.session.commit()
        print(f"Se crearon {len(test_users)} usuarios de prueba")
    else:
        print("Todos los usuarios de prueba ya existen")


def roles():
    for name in UserRole.__members__.keys():
        db.session.add(Role(name=name))

    for name, roles in UserPermission.__members__.values():
        perm = Permission(name=name)
        for r in roles:
            r = Role.query.filter_by(name=r).first()
            if r:
                perm.roles.append(r)
        db.session.add(perm)
    db.session.commit()


def feature_flags_seed():
    """Crea los feature flags predeterminados si no existen."""
    defaults = [
        ("admin_maintenance_mode", False, ""),
        ("portal_maintenance_mode", False, ""),
        ("reviews_enabled", True, ""),
    ]
    changed = False
    for k, v, m in defaults:
        existing = FeatureFlag.query.get(k)
        if not existing:
            db.session.add(FeatureFlag(key=k, value_bool=v, message=m))
            changed = True
    if changed:
        db.session.commit()
    print("Feature flags creados o actualizados.")
