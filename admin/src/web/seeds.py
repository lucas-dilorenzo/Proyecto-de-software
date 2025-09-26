from select import select
from src.core.database import db
from src.core import historicalSites
from src.core.historicalSites.site import Site  # Esta es la correcta
from datetime import date
from src.core.users.user import User, UserRole
from werkzeug.security import generate_password_hash


def run():
    print("Seeding database with initial data...")

    sites_data = [
        {
            "name": "Great Wall of China",
            "description_short": "Ancient series of walls and fortifications.",
            "description": "The Great Wall of China is a historic fortification built to protect Chinese states against invasions. It stretches over 13,000 miles.",
            "city": "Beijing",
            "province": "Hebei",
            "location": "China",
            "conservation_status": "Well-preserved in some sections, others are deteriorating.",
            "year_declared": -700,
            "category": "Fortification",
            "registration_date": date(1987, 12, 1),
            "visibility": True,
        },
        {
            "name": "Machu Picchu",
            "description_short": "15th-century Inca citadel.",
            "description": "Machu Picchu is an ancient Inca city set high in the Andes Mountains, renowned for its archaeological significance and breathtaking views.",
            "city": "Cusco",
            "province": "Cusco",
            "location": "Peru",
            "conservation_status": "Protected, but threatened by tourism.",
            "year_declared": 1450,
            "category": "Archaeological Site",
            "registration_date": date(1983, 12, 1),
            "visibility": True,
        },
        {
            "name": "Pyramids of Giza",
            "description_short": "Ancient pyramid complex.",
            "description": "The Pyramids of Giza are monumental tombs built for Egyptian pharaohs, representing one of the greatest architectural feats of ancient times.",
            "city": "Giza",
            "province": "Giza",
            "location": "Egypt",
            "conservation_status": "Stable, ongoing restoration.",
            "year_declared": -2580,
            "category": "Monument",
            "registration_date": date(1979, 12, 1),
            "visibility": True,
        },
        {
            "name": "Colosseum",
            "description_short": "Large amphitheater in Rome.",
            "description": "The Colosseum is a massive stone amphitheater in Rome, Italy, known for gladiatorial contests and public spectacles.",
            "city": "Rome",
            "province": "Lazio",
            "location": "Italy",
            "conservation_status": "Partially restored, ongoing conservation.",
            "year_declared": 80,
            "category": "Amphitheater",
            "registration_date": date(1980, 12, 1),
            "visibility": True,
        },
        {
            "name": "Taj Mahal",
            "description_short": "Ivory-white marble mausoleum.",
            "description": "The Taj Mahal is a world-famous mausoleum built by Mughal emperor Shah Jahan in memory of his wife Mumtaz Mahal.",
            "city": "Agra",
            "province": "Uttar Pradesh",
            "location": "India",
            "conservation_status": "Well-preserved, pollution concerns.",
            "year_declared": 1643,
            "category": "Mausoleum",
            "registration_date": date(1983, 12, 1),
            "visibility": True,
        },
    ]

    for site_data in sites_data:
        existing_site = historicalSites.get_site_by_name(site_data["name"])
        if not existing_site:
            historicalSites.create_site(**site_data)
            print(f"Added site: {site_data['name']}")
        else:
            print(f"Site already exists: {site_data['name']}")

    print("Database seeding complete.")


def users():
    """Crea un usuario administrador por defecto si no existe."""
    exists = User.query.filter_by(
        email="admin@example.com"
    ).first()  # Implementar con la funcion get_user_by_email
    if not exists:  # implementar con la funcion create_user
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
