from src.core import historicalSites
from src.web.auth import permission_required
from src.core.permissions.permission import UserPermission
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
@permission_required(UserPermission.SITE_LIST)
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
    # Leer visibility como lista para distinguir ausencia (no se filtró) de false/true
    visibility_list = request.args.getlist("visibility")
    if not visibility_list:
        visibility = None
    else:
        # si cualquiera de los valores es truthy, lo tomamos como True
        visibility = any(
            v.lower() in ("1", "true", "on", "yes") for v in visibility_list
        )
    # support both 'search_text' and legacy 'stringBusqueda'
    search_text = request.args.get("search_text", type=str) or stringBusqueda

    sites = historicalSites.get_sites_paginated_by_id(
        page=page,
        per_page=5,
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
    # Mando también la lista de tags y provincias para armar el formulario
    all_tags = historicalSites.tags.get_all_tags()
    all_provinces = historicalSites.get_all_provinces()
    # determinar si hay filtros activos para mostrar el botón Limpiar
    visibility_present = "visibility" in request.args
    has_filters = any(
        [
            stringBusqueda,
            city,
            province,
            tags,
            conservation_status,
            date_from,
            date_to,
            visibility_present,
            search_text,
        ]
    )
    # construir un dict con los query params actuales excepto 'page' para reutilizar en paginado
    current_query = {}
    for k in (
        "stringBusqueda",
        "city",
        "province",
        "tags",
        "conservation_status",
        "date_from",
        "date_to",
        "visibility",
        "search_text",
    ):
        v = request.args.getlist(k) if k == "tags" else request.args.get(k)
        if v:
            # si es lista de tags y tiene varios valores, dejalo como lista
            current_query[k] = v

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
        current_query=current_query,
    )


@historical_sites_bp.route("/<int:site_id>", methods=["GET"])
@login_required
@permission_required(UserPermission.SITE_LIST)
def show_site(site_id):
    site = historicalSites.get_site_by_id(site_id)
    if site is None:
        return "Site not found", 404
    return render_template("historicalSites/show_site.html", site=site)


@historical_sites_bp.route("/create", methods=["GET", "POST"])
@login_required
@permission_required(UserPermission.SITE_CREATE)
def create_site():
    # cargar tags para el formulario (se usa tanto en GET como en caso de validación fallida)
    tags = get_all_tags()

    if request.method == "POST":
        form = SiteForm()
        if form.validate_on_submit():
            formulario = request.form
            visibility_ = True if formulario.get("visibility") is not None else False
            # crear el sitio
            if historicalSites.get_site_by_name(formulario.get("name")) is None:
                site = historicalSites.create_site(
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

                # Asignar tags seleccionados (si los hay)
                try:
                    selected_tag_ids = request.form.getlist("tags")
                    if selected_tag_ids:
                        tag_objs = []
                        for t in selected_tag_ids:
                            try:
                                tid = int(t)
                            except Exception:
                                continue
                            tag = historicalSites.tags.get_tag_by_id(tid)
                            if tag:
                                tag_objs.append(tag)
                        if tag_objs:
                            historicalSites.asignar_tags_a_sitio(site, tag_objs)
                except Exception as e:
                    # no fallar la creación por problemas de tags; loguear y seguir
                    flash(
                        f"Sitio creado pero no se pudieron asignar tags: {e}", "warning"
                    )
                flash("Sitio creado correctamente.", "success")
                return redirect(url_for("sites.list_sites"))
            else:
                flash("Ya existe un sitio con ese nombre.", "danger")
                return render_template(
                    "historicalSites/create_site.html",
                    tags=tags,
                    visibility=visibility_,
                )
        else:
            if form.errors:
                for field, errors in form.errors.items():
                    for error in errors:
                        flash(f"Error en el campo {field}: {error}", "danger")
            # preservar estado del checkbox de visibilidad
            visibility_ = True if request.form.get("visibility") is not None else False
            return render_template(
                "historicalSites/create_site.html", tags=tags, visibility=visibility_
            )

    # GET
    return render_template(
        "historicalSites/create_site.html", tags=tags, visibility=True
    )


@historical_sites_bp.route("/<int:site_id>/edit", methods=["GET", "POST"])
@login_required
@permission_required(UserPermission.SITE_UPDATE)
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
            visibility=formulario.get("visibility") == "true",
        )
        # Procesar tags seleccionados; si no se envían tags, vaciar la relación
        try:
            selected_tag_ids = request.form.getlist("tags")
            tag_objs = []
            for t in selected_tag_ids:
                try:
                    tid = int(t)
                except Exception:
                    continue
                tag = historicalSites.tags.get_tag_by_id(tid)
                if tag:
                    tag_objs.append(tag)
            # asignar (incluso lista vacía para limpiar tags)
            site = historicalSites.get_site_by_id(site_id)
            historicalSites.asignar_tags_a_sitio(site, tag_objs)
        except Exception as e:
            flash(f"No se pudieron actualizar los tags: {e}", "warning")

        return redirect(url_for("sites.list_sites"))

    # cargar tags para el formulario de edición
    all_tags = historicalSites.tags.get_all_tags()
    return render_template("historicalSites/edit_site.html", site=site, tags=all_tags)


@historical_sites_bp.route("/<int:site_id>/delete", methods=["GET", "POST"])
@login_required
@permission_required(UserPermission.SITE_DELETE)
def delete_site(site_id):
    site = historicalSites.get_site_by_id(site_id)
    if site is None:
        return "Site not found", 404
    # if request.method == "POST":
    #     # llamada vía AJAX desde SweetAlert
    #     try:
    #         historicalSites.delete_site(site_id)
    #         return {"message": f"Sitio {site.name} eliminado correctamente."}, 200
    #     except Exception as e:
    #         return {"message": str(e)}, 500

    # fallback GET (compatibilidad)
    if request.method == "GET":
        historicalSites.delete_site(site_id)
        flash(f"Sitio {site.name} eliminado correctamente.", "success")
        return redirect(url_for("sites.list_sites"))


@historical_sites_bp.route("/download_CSV", methods=["GET"])
@login_required
@permission_required(UserPermission.SITE_EXPORT)
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


def get_categories():
    """
    Función que devuelve las categorías de sitios históricos disponibles.

    Returns:
        dict: Diccionario con las categorías como pares key:value
    """
    categories = {
        "monumento_nacional": "Monumento Nacional",
        "sitio_historico": "Sitio Histórico",
        "bien_cultural": "Bien Cultural",
        "patrimonio_mundial": "Patrimonio Mundial",
        "monumento_historico_nacional": "Monumento Histórico Nacional",
        "lugar_historico_nacional": "Lugar Histórico Nacional",
    }
    return categories


def get_conservation_statuses():
    """
    Función que devuelve los estados de conservación disponibles.

    Returns:
        dict: Diccionario con los estados de conservación como pares key:value
    """
    statuses = {
        "excelente": "Excelente",
        "bueno": "Bueno",
        "regular": "Regular",
        "malo": "Malo",
        "critico": "Crítico",
        "en_restauracion": "En restauración",
    }
    return statuses


# USAR ESTE NORMALIZADOR PARA INTENTAR EVITAR EL ERROR CSV
def normalizar(valor):
    if valor is not None:
        valor = str(valor).replace(",", "-")
    else:
        valor = "-"
    return valor
