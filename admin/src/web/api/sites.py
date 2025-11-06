from flask import jsonify, request
from src.web.api import api_bp  # 🔹 Usar import absoluto en lugar de relativo

# Datos mock para probar
MOCK_SITES = [
    {
        "id": 1,
        "name": "Fortín del Valle",
        "city": "Córdoba",
        "province": "Córdoba",
        "avg_rating": 4.7,
        "cover_image": "https://picsum.photos/seed/fortin/400/250",
    },
    {
        "id": 2,
        "name": "Ruinas de Quilmes",
        "city": "Tucumán",
        "province": "Tucumán",
        "avg_rating": 4.5,
        "cover_image": "https://picsum.photos/seed/quilmes/400/250",
    },
    {
        "id": 3,
        "name": "Estancia Santa Catalina",
        "city": "Jesús María",
        "province": "Córdoba",
        "avg_rating": 4.8,
        "cover_image": "https://picsum.photos/seed/catalina/400/250",
    },
]

@api_bp.route("/sites", methods=["GET"])
def list_sites():
    """
    Mock temporal de GET /api/sites
    Permite probar el portal público.
    """
    order_by = request.args.get("order_by", "latest")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 12))

    # Por ahora no aplicamos orden ni paginado reales
    data = MOCK_SITES[:per_page]

    return jsonify({
        "data": data,
        "page": page,
        "per_page": per_page,
        "total": len(MOCK_SITES),
    })
