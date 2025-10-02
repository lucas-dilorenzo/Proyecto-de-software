from src.core import historicalSites
from src.web.helpers.validations.sites import SiteForm
from src.core.historicalSites.tags import get_all_tags
from flask import (
    Blueprint,
    Response,
    redirect,
    render_template,
    request,
    url_for,
    abort,
    flash,
)
import csv
from src.web.helpers import login_required

historical_sites_bp = Blueprint("sites", __name__, url_prefix="/sites")


@historical_sites_bp.route("/", methods=["GET"])
@login_required
def list_sites():
    # if not authenticated(session):
    # abort(401)

    # if not has_permission(session["user"].id, permission="asc_index"):
    #     abort(403)
    page = request.args.get("page", 1, type=int)
    # legacy search input name used in template
    stringBusqueda = request.args.get("stringBusqueda", type=str)
    # Leer filtros desde query params
    city = request.args.get("city")
    province = request.args.get("province")
    tags = request.args.getlist("tags")  # puede venir como tags=1&tags=2
    conservation_status = request.args.get("conservation_status", type=str)
    date_from = request.args.get("date_from", type=str)
    date_to = request.args.get("date_to", type=str)
    visibility_raw = request.args.get("visibility")
    if visibility_raw is None:
        visibility = None
    else:
        visibility = visibility_raw.lower() in ("1", "true", "on", "yes")
    # support both 'search_text' and legacy 'stringBusqueda'
    search_text = request.args.get("search_text", type=str) or stringBusqueda

    sites = historicalSites.get_sites_paginated_by_id(
        page=page,
        per_page=3,
        order="asc",
        city=city,
        province=province,
        tags=tags,
        conservation_status=conservation_status,
        date_from=date_from,
        date_to=date_to,
        visibility=visibility,
        search_text=search_text,
    )

    # Mandás también la lista de tags y provincias para armar el formulario
    all_tags = historicalSites.tags.get_all_tags()
    all_provinces = historicalSites.get_all_provinces() 

    # determinar si hay filtros activos para mostrar el botón Limpiar
    has_filters = any([stringBusqueda, city, province, tags, conservation_status, date_from, date_to, visibility, search_text])

    return render_template(
        "historicalSites/list_sites.html",
        sites=sites,
        city=city,
        provinces=[p.province for p in all_provinces],
        tags=all_tags,
        conservation_status=conservation_status,
        date_from=date_from,
        date_to=date_to,
        visibility=visibility,
        search_text=search_text,
        stringBusqueda=stringBusqueda,
        has_filters=has_filters,
    )


@historical_sites_bp.route("/<int:site_id>", methods=["GET"])
@login_required
def show_site(site_id):
    site = historicalSites.get_site_by_id(site_id)
    if site is None:
        return "Site not found", 404
    return render_template("historicalSites/show_site.html", site=site)


@historical_sites_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_site():
    if request.method == "POST":
        form = SiteForm()
        if form.validate_on_submit():
            formulario = request.form
            visibility_ = True if formulario.get("visibility") is not None else False
            historicalSites.create_site(
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
                visibility=visibility_,
            )
            return redirect(url_for("sites.list_sites"))
        else:
            if form.errors:
                for field, errors in form.errors.items():
                    for error in errors:
                        flash(f"Error en el campo {field}: {error}", "danger")
            return render_template("historicalSites/create_site.html", tags=tags)
        tags = get_all_tags()
    return render_template("historicalSites/create_site.html", tags=tags)


@historical_sites_bp.route("/<int:site_id>/edit", methods=["GET", "POST"])
@login_required
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
@login_required
def delete_site(site_id):
    site = historicalSites.get_site_by_id(site_id)
    if site is None:
        return "Site not found", 404
    if request.method == "GET":
        historicalSites.delete_site(site_id)
        return redirect(url_for("sites.list_sites"))
        # return f"Site {site.name} deleted", 200


@historical_sites_bp.route("/download_CSV", methods=["GET"])
@login_required
def download_csv_sites():
    # Logic to download the list of sites
    sites = historicalSites.list_all_sites()
    if sites is None:
        return "No sites found", 404

    csv_data = "Nombre,Descripción breve,Descripción completa,Ciudad,Provincia,Lugar,Estado de conservación,Año de declaración,Categoría,Fecha de registro \n"
    for site in sites:
        csv_data += (
            f"{normalizar(site.name)},"
            f"{normalizar(site.description_short)},"
            f"{normalizar(site.description)},"
            f"{normalizar(site.city)},"
            f"{normalizar(site.province)},"
            f"{normalizar(site.location)}),"
            f"{normalizar(site.conservation_status)},"
            f"{normalizar(site.year_declared)},"
            f"{normalizar(site.category)},"
            f"{normalizar(site.registration_date)}\n"
        )

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-disposition": "attachment; filename=sitios_<YYYYMMDD_HHMM>.csv"
        },
    )


# USAR ESTE NORMALIZADOR PARA INTENTAR EVITAR EL ERROR CSV
def normalizar(valor):
    if valor is not None:
        valor = str(valor).replace(",", "-")
    else:
        valor = "-"
    return valor
