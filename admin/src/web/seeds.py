from select import select

# from core.database import db
from src.core.database import db
from src.core import historicalSites
from src.core.historicalSites.site import Site
from src.core.historicalSites.tags.tag import Tag
from datetime import date
from src.core.users.user import User, UserRole
from werkzeug.security import generate_password_hash


def run():
    print("Seeding database with initial data...")

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
            "location": "China",
            "conservation_status": "Bien conservada en algunos tramos; otros requieren restauración.",
            "year_declared": -700,
            "category": "Fortificación",
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
            "location": "Peru",
            "conservation_status": "Protegida, pero amenazada por el turismo masivo.",
            "year_declared": 1450,
            "category": "Sitio arqueologico",
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
            "location": "Egipto",
            "conservation_status": "Estables con trabajos de restauración en curso.",
            "year_declared": -2580,
            "category": "Monumento",
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
            "location": "Italia",
            "conservation_status": "Parcialmente restaurado; conservación continua.",
            "year_declared": 80,
            "category": "Anfiteatro",
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
            "location": "India",
            "conservation_status": "Bien conservado; problemas por contaminación.",
            "year_declared": 1643,
            "category": "Mausoleo",
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
            "location": "Argentina",
            "conservation_status": "Protegido; conservación activa.",
            "year_declared": 1980,
            "category": "Parque Nacional",
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
            "location": "Argentina",
            "conservation_status": "Patrimonio protegido; vulnerable al turismo no regulado.",
            "year_declared": 1000,
            "category": "Sitio arqueológico",
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
            "location": "Ecuador",
            "conservation_status": "Bien conservado; medidas de protección en marcha.",
            "year_declared": 1534,
            "category": "Conjunto urbano",
            "registration_date": date(1978, 9, 5),
            "visibility": True,
            "tags": ["Patrimonio Mundial", "Cultural"],
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
    """Crea un usuario administrador por defecto si no existe."""
    exists = User.query.filter_by(email="admin@example.com").first()
    if not exists:
        admin = User(
            email="admin@example.com",
            nombre="Admin",
            apellido="Local",
            password_hash=generate_password_hash("admin123"),
            activo=True,
            rol=UserRole.ADMIN,
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin creado: admin@example.com / admin123")
    else:
        print("El admin ya existe.")
