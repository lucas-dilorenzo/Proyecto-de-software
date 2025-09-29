from winsound import SND_ASYNC
from src.core import historicalSites
from flask import Blueprint, Response, redirect, render_template, request, url_for, abort

historical_sites_bp = Blueprint("sites", __name__, url_prefix="/sites")


@historical_sites_bp.route("/", methods=["GET"])
def list_sites():
    # if not authenticated(session):
    # abort(401)

    # if not has_permission(session["user"].id, permission="asc_index"):
    #     abort(403)
    page = request.args.get("page", 1, type=int)
    sites = historicalSites.get_sites_paginated_by_id(
        page=page, per_page=3, order="asc"
    )
    return render_template("historicalSites/list_sites.html", sites=sites)


@historical_sites_bp.route("/<int:site_id>", methods=["GET"])
def show_site(site_id):
    site = historicalSites.get_site_by_id(site_id)
    if site is None:
        return "Site not found", 404
    return render_template("historicalSites/show_site.html", site=site)


@historical_sites_bp.route("/create", methods=["GET", "POST"])
def create_site():
    if request.method == "POST":
        # Logic to create a new site
        return redirect(url_for("sites.list_sites"))
    return render_template("historicalSites/create_site.html")


@historical_sites_bp.route("/<int:site_id>/edit", methods=["GET", "POST"])
def edit_site(site_id):
    site = historicalSites.get_site_by_id(site_id)
    if site is None:
        abort(404)
    if request.method == "POST":
        formulario = request.form
        historicalSites.update_site(
            site_id,
            name=formulario.get("name"),
            description_short=formulario.get("description_short"),
            description=formulario.get("description"),
            city=formulario.get("city"),
            province=formulario.get("province"),
            location=formulario.get("location"),
            conservation_status=formulario.get("conservation_status"),
            year_declared=formulario.get("year_declared"),
            category=formulario.get("category"),
            registration_date=formulario.get("registration_date"),
            visibility=formulario.get("visibility") == "on",
        )
        return redirect(url_for("sites.list_sites"))
    
    return render_template("historicalSites/edit_site.html", site=site)


@historical_sites_bp.route("/<int:site_id>/delete", methods=["GET"])
def delete_site(site_id):
    site = historicalSites.get_site_by_id(site_id)
    if site is None:
        return "Site not found", 404
    if request.method == "GET":
        historicalSites.delete_site(site_id)
        return redirect(url_for("sites.list_sites"))
        #return f"Site {site.name} deleted", 200


@historical_sites_bp.route("/download_CSV", methods=["GET"])
def download_csv_sites():
    # Logic to download the list of sites
    sites = historicalSites.list_all_sites()
    if sites is None:
        return "No sites found", 404
    
    csv_data = "Nombre,Descripción breve,Descripción completa,Ciudad,Provincia,Lugar,Estado de conservación,Año de declaración,Categoría,Fecha de registro \n"
    for site in sites:
        csv_data += (
            f"{site.name},"
            f"{site.description_short},"
            f"{site.description},"
            f"{site.city},"
            f"{site.province},"
            f"{site.location},"
            f"{site.conservation_status},"
            f"{site.year_declared},"
            f"{site.category},"
            f"{site.registration_date}\n"
        )

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=sitios_<YYYYMMDD_HHMM>.csv"}
    )

# USAR ESTE NORMALIZADOR PARA INTENTAR EVITAR EL ERROR CSV
def normalizar(valor, default=""):
    return valor if valor is not None else default

