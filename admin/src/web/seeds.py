from src.core.database import db
from src.core import historicalSites


def run():
    print("Seeding database with initial data...")

    sites_data = [
        {
            "name": "Great Wall of China",
            "description_short": "Ancient series of walls and fortifications.",
            "location": "China",
            "year_declared": -700,
        },
        {
            "name": "Machu Picchu",
            "description_short": "15th-century Inca citadel.",
            "location": "Peru",
            "year_declared": 1450,
        },
        {
            "name": "Pyramids of Giza",
            "description_short": "Ancient pyramid complex.",
            "location": "Egypt",
            "year_declared": -2580,
        },
        {
            "name": "Colosseum",
            "description_short": "Large amphitheater in Rome.",
            "location": "Italy",
            "year_declared": 80,
        },
        {
            "name": "Taj Mahal",
            "description_short": "Ivory-white marble mausoleum.",
            "location": "India",
            "year_declared": 1643,
        },
    ]

    for site_data in sites_data:
        existing_site = historicalSites.get_by_name(site_data["name"])
        if not existing_site:
            historicalSites.create_site(**site_data)
            print(f"Added site: {site_data['name']}")
        else:
            print(f"Site already exists: {site_data['name']}")

    print("Database seeding complete.")
