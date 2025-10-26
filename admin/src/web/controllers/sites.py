from src.core import historicalSites
from src.web.auth import permission_required
from src.core.permissions.permission import UserPermission
from src.web.helpers.validations.sites import SiteForm
from src.core.historicalSites.tags import get_all_tags
from src.core.historicalSites.enums import ConservationStatus, SiteCategory
from datetime import datetime
from flask import (
    Blueprint,
    Response,
    redirect,
    render_template,
    request,
    url_for,
    abort,
    flash,
    session,
)
import csv
import json
import datetime
from src.web.helpers import login_required


historical_sites_bp = Blueprint("sites", __name__, url_prefix="/sites")


@historical_sites_bp.route("/", methods=["GET"])
@login_required
@permission_required(UserPermission.SITE_LIST)
def list_sites():
    """Lista los sitios históricos con paginación y filtros"""
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

    # parametros para ordenamiento
    order_by = request.args.get("order_by", default="name", type=str)
    order_dir = request.args.get("order_dir", default="asc", type=str)

    # Pasar los parámetros de ordenamiento al servicio
    sites = historicalSites.get_sites_paginated_by_id(
        page=page,
        per_page=10,
        order=order_dir,
        order_by=order_by,
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

    # NOTA: no agregamos order_by/order_dir a current_query para evitar colisiones
    # cuando la plantilla pasa **(current_query) y además especifica order_by/order_dir.

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
        order_by=order_by,
        order_dir=order_dir,
    )


@historical_sites_bp.route("/deleted", methods=["GET"])
@login_required
@permission_required(UserPermission.SITE_LIST)
def list_deleted_sites():
    """Lista los sitios históricos eliminados (soft delete)"""
    # Obtener todos los sitios marcados como eliminados (sin paginación)
    sites = historicalSites.get_deleted_sites()

    return render_template(
        "historicalSites/list_deleted_sites.html",
        sites=sites,
    )


@historical_sites_bp.route("/<int:site_id>", methods=["GET"])
@login_required
@permission_required(UserPermission.SITE_LIST)
def show_site(site_id):
    """Muestra los detalles de un sitio histórico"""
    site = historicalSites.get_site_by_id(site_id)
    if site is None:
        return "Site not found", 404
    return render_template("historicalSites/show_site.html", site=site)


@historical_sites_bp.route("/<int:site_id>/history", methods=["GET"])
@login_required
# @permission_required(UserPermission.SITE_HISTORY)
def show_site_history(site_id):
    """Muestra el historial de cambios de un sitio histórico"""
    site = historicalSites.get_site_by_id(site_id)
    if site is None:
        return "Site not found", 404

    # Obtener los logs asociados al sitio, ordenados por timestamp desc
    # Obtener logs a través de la capa de servicios (respeta MVC)
    logs = historicalSites.get_site_logs(site_id)

    # Normalizar el campo details para facilitar renderizado en la plantilla
    for l in logs:
        parsed = None
        if l.details is None:
            parsed = None
        else:
            # puede venir como JSON o como string serializado
            if isinstance(l.details, str):
                try:
                    normalizado = json.loads(l.details)
                except Exception:
                    # no json -> dejar el string tal cual
                    normalizado = l.details
            else:
                # ya es un objeto (dict/list)
                normalizado = l.details

        # Si normalizado es dict con el formato {field: {old:..., new:...}}, convertir a lista de tuplas
        display_changes = None
        if isinstance(normalizado, dict):
            # cada key -> {old:..., new:...}
            display_changes = []
            for field, change in normalizado.items():
                old = None
                new = None
                if isinstance(change, dict):
                    old = change.get("old")
                    new = change.get("new")
                else:
                    # si el value no sigue el formato esperado, representarlo como str
                    old = None
                    new = change
                display_changes.append((field, old, new))
        else:
            # parsed no es dict -> no hay cambios estructurados
            display_changes = None

        # adjuntar al objeto log para usar en la plantilla
        setattr(l, "parsed_changes", display_changes)

    return render_template("historicalSites/site_history.html", site=site, logs=logs)


@historical_sites_bp.route("/create", methods=["GET", "POST"])
@login_required
@permission_required(UserPermission.SITE_CREATE)
def create_site():
    """Crea un nuevo sitio histórico"""
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
                flash(f"Sitio creado pero no se pudieron asignar tags: {e}", "warning")
            flash("Sitio creado correctamente.", "success")
            return redirect(url_for("sites.show_site", site_id=site.id))
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
    """Edita un sitio histórico existente"""
    site = historicalSites.get_site_by_id(site_id)
    if site is None:
        abort(404)
    # cargar tags para el formulario de edición
    all_tags = historicalSites.tags.get_all_tags()
    if request.method == "POST":
        form = SiteForm()
        if form.validate_on_submit():
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
        else:
            if form.errors:
                for field, errors in form.errors.items():
                    for error in errors:
                        flash(f"Error en el campo {field}: {error}", "danger")
            # preservar estado del checkbox de visibilidad
            visibility_ = True if request.form.get("visibility") is not None else False
            return redirect(url_for("sites.edit_site", site_id=site.id))
    return render_template("historicalSites/edit_site.html", site=site, tags=all_tags)


@historical_sites_bp.route("/<int:site_id>/delete", methods=["GET", "POST"])
@login_required
@permission_required(UserPermission.SITE_DELETE)
def delete_site(site_id):
    """Elimina un sitio histórico (soft delete)"""
    site = historicalSites.get_site_by_id(site_id)
    if site is None:
        return "Site not found", 404

    if request.method == "GET":
        # eliminado=site.id
        try:
            historicalSites.delete_site(site_id)
            flash(f"Sitio {site.name} eliminado correctamente.", "success")
        except Exception as e:
            flash(f"No se pudo eliminar el sitio: {e}", "danger")
        return redirect(url_for("sites.list_sites"))


@historical_sites_bp.route("/download_CSV", methods=["GET"])
@login_required
@permission_required(UserPermission.SITE_EXPORT)
def download_csv_sites():
    """Descarga un archivo CSV con la lista de sitios históricos"""
    # Logic to download the list of sites
    sites = historicalSites.list_all_sites()

    if sites is None:
        return "No sites found", 404

    csv_data = "Nombre,Descripción breve,Descripción completa,Ciudad,Provincia,Lugar,Estado de conservación,Año de declaración,Categoría,Fecha de registro, Tags \n"
    for site in sites:

        listado_tags = [tag.name for tag in site.tags]
        tags_str = " | ".join(listado_tags)
        print(tags_str)

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
            f"{normalizar(site.registration_date)},"
            f"{normalizar(tags_str)}\n"
        )

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sitios_{timestamp}"

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={filename}.csv"},
    )


def get_categories():
    """
    Función que devuelve las categorías de sitios históricos disponibles.

    Returns:
        dict: Diccionario con las categorías como pares key:value
    """
    return {category.code: category.label for category in SiteCategory}


def get_category_label(key):
    """
    Función que devuelve el label de una categoría dado su clave.

    Args:
        key (str): Clave de la categoría.

    Returns:
        str: Valor legible de la categoría, o None si no existe.
    """
    category_dict = {category.code: category.label for category in SiteCategory}
    return category_dict.get(key)


def get_conservation_statuses():
    """
    Función que devuelve los estados de conservación disponibles.

    Returns:
        dict: Diccionario con los estados de conservación como pares key:value
    """
    return {status.code: status.label for status in ConservationStatus}


def get_conservation_status(key):
    """
    Función que devuelve el label de un estado de conservación dado su clave.

    Args:
        key (str): Clave del estado de conservación.

    Returns:
        str: Valor legible del estado, o None si no existe.
    """
    status_dict = {status.code: status.label for status in ConservationStatus}
    return status_dict.get(key)


# USAR ESTE NORMALIZADOR PARA INTENTAR EVITAR EL ERROR CSV
def normalizar(valor):
    """Normaliza un valor para evitar errores en CSV (reemplaza comas por guiones)."""
    if valor is not None:
        valor = str(valor).replace(",", "-")
    else:
        valor = "-"
    return valor
