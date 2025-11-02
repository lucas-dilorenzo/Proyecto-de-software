from src.core import historicalSites
from src.web.auth import permission_required
from src.core.permissions.permission import UserPermission
from src.web.helpers.validations.sites import SiteForm
from src.core.historicalSites.tags import get_all_tags
from src.core.historicalSites.enums import ConservationStatus, SiteCategory
from src.core import images
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
    current_app,
)
import csv
import json
from src.web.helpers import login_required
from urllib.parse import urlparse, parse_qs
from werkzeug.datastructures import MultiDict
from os import fstat


# --------------------------------------------------------------------
# Blueprint
# --------------------------------------------------------------------
historical_sites_bp = Blueprint("sites", __name__, url_prefix="/sites")


# --------------------------------------------------------------------
# Helpers de filtros (comparten listado y CSV)
# --------------------------------------------------------------------
def _parse_list_filters(args):
    city = args.get("city", type=str)
    province = args.get("province", type=str)
    tags = args.getlist("tags")  # ?tags=1&tags=2
    conservation_status = args.get("conservation_status", type=str)
    date_from = args.get("date_from", type=str)
    date_to = args.get("date_to", type=str)

    # visibility: None (no filtra), True/False
    visibility_list = args.getlist("visibility")
    if not visibility_list:
        visibility = None
    else:
        visibility = any(
            v.lower() in ("1", "true", "on", "yes") for v in visibility_list
        )

    # aceptar 'search_text' y el legacy 'stringBusqueda'
    search_text = args.get("search_text") or args.get("stringBusqueda")

    order_by = args.get("order_by") or "name"
    order_dir = args.get("order_dir") or "asc"

    return dict(
        city=city,
        province=province,
        tags=tags,
        conservation_status=conservation_status,
        date_from=date_from,
        date_to=date_to,
        visibility=visibility,
        search_text=search_text,
        order_by=order_by,
        order_dir=order_dir,
    )


# --------------------------------------------------------------------
# Helpers de labels legibles para CSV
# --------------------------------------------------------------------
_CATEGORY_MAP = {category.code: category.label for category in SiteCategory}
_STATUS_MAP = {status.code: status.label for status in ConservationStatus}


def get_category_label(key):
    if key is None:
        return None
    return _CATEGORY_MAP.get(key) or _CATEGORY_MAP.get(str(key)) or str(key)


def get_status_label(key):
    if key is None:
        return None
    return _STATUS_MAP.get(key) or _STATUS_MAP.get(str(key)) or str(key)


# Lo importan desde src/web/__init__.py — mantengámoslo para compatibilidad
def get_conservation_status(key):
    """
    Devuelve el label legible para un estado de conservación (código -> etiqueta).
    """
    if key is None:
        return None
    return _STATUS_MAP.get(key) or _STATUS_MAP.get(str(key)) or None


# (opcional) utilidades que quizá uses en vistas/plantillas
def get_categories():
    return _CATEGORY_MAP


def get_conservation_statuses():
    return _STATUS_MAP


# --------------------------------------------------------------------
# Rutas
# --------------------------------------------------------------------
@historical_sites_bp.route("/", methods=["GET"])
@login_required
@permission_required(UserPermission.SITE_LIST)
def list_sites():
    """Lista los sitios históricos con paginación y filtros"""
    page = request.args.get("page", 1, type=int)

    # legacy search input name usado en template
    stringBusqueda = request.args.get("stringBusqueda", type=str)

    # Leer filtros desde query params
    city = request.args.get("city")
    province = request.args.get("province")
    tags = request.args.getlist("tags")  # ?tags=1&tags=2
    conservation_status = request.args.get("conservation_status", type=str)
    date_from = request.args.get("date_from", type=str)
    date_to = request.args.get("date_to", type=str)

    # visibility como lista para distinguir ausencia (no se filtró) de false/true
    visibility_list = request.args.getlist("visibility")
    if not visibility_list:
        visibility = None
    else:
        visibility = any(
            v.lower() in ("1", "true", "on", "yes") for v in visibility_list
        )

    # soportar 'search_text' y legacy 'stringBusqueda'
    search_text = request.args.get("search_text", type=str) or stringBusqueda

    # parámetros para ordenamiento
    order_by = request.args.get("order_by", default="name", type=str)
    order_dir = request.args.get("order_dir", default="asc", type=str)

    # Pasar los parámetros al servicio (paginado)
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

    # Datos para el formulario
    all_tags = historicalSites.tags.get_all_tags()
    all_provinces = historicalSites.get_all_provinces()

    # determinar si hay filtros activos para mostrar "Limpiar"
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

    # construir query actual (excepto page) para reutilizar en paginado/export

    current_query = {}
    list_keys = {"tags", "visibility"}  # <-- ambos como lista
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
        v = request.args.getlist(k) if k in list_keys else request.args.get(k)
        if v:
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
        order_by=order_by,
        order_dir=order_dir,
    )


@historical_sites_bp.route("/deleted", methods=["GET"])
@login_required
@permission_required(UserPermission.SITE_LIST)
def list_deleted_sites():
    """Lista los sitios históricos eliminados (soft delete)"""
    sites = historicalSites.get_deleted_sites()
    return render_template("historicalSites/list_deleted_sites.html", sites=sites)


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

    logs = historicalSites.get_site_logs(site_id)

    # Normalizar 'details' para render
    for l in logs:
        if l.details is None:
            normalizado = None
        elif isinstance(l.details, str):
            try:
                normalizado = json.loads(l.details)
            except Exception:
                normalizado = l.details
        else:
            normalizado = l.details

        display_changes = None
        if isinstance(normalizado, dict):
            display_changes = []
            for field, change in normalizado.items():
                if isinstance(change, dict):
                    old = change.get("old")
                    new = change.get("new")
                else:
                    old = None
                    new = change
                display_changes.append((field, old, new))
        setattr(l, "parsed_changes", display_changes)

    return render_template("historicalSites/site_history.html", site=site, logs=logs)


@historical_sites_bp.route("/create", methods=["GET", "POST"])
@login_required
@permission_required(UserPermission.SITE_CREATE)
def create_site():
    """Crea un nuevo sitio histórico"""
    tags = get_all_tags()

    if request.method == "POST":
        form = SiteForm()
        if form.validate_on_submit():
            formulario = request.form
            visibility_ = True if formulario.get("visibility") is not None else False

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

                site = historicalSites.get_site_by_name(formulario.get("name"))
                site_id = site.id
                if "main_image" in request.files:
                    primary_img = request.files["main_image"]
                    if primary_img and primary_img.filename:
                        file = primary_img
                        size = fstat(file.fileno()).st_size
                        bucket_name = current_app.config["MINIO_BUCKET_NAME"]
                        # ulid = file.filename  # Simplificado para este ejemplo
                        object_name = f"sites/{site_id}/{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}"
                        client = current_app.storage
                        client.put_object(
                            bucket_name=bucket_name,
                            object_name=object_name,
                            data=file,
                            length=size,
                            content_type=primary_img.content_type,
                        )
                        # Devolver en params el path del objeto subido
                        titulo = request.form.get(
                            "main_image_title", "Imagen principal"
                        )
                        descripcion = request.form.get(
                            "main_image_description",
                            "Imagen principal del sitio histórico",
                        )
                        images.create_image(
                            site_id=site_id,
                            url=object_name,
                            order=0,
                            titulo=titulo,
                            descripcion=descripcion,
                        )

                if "secondary_images" in request.files:
                    client = current_app.storage
                    secondary_images = request.files.getlist("secondary_images")

                    # Obtener títulos y descripciones de las imágenes secundarias.
                    # Aceptar varias convenciones de nombre que pueden venir
                    # del template/JS: "secondary_image_titles", "secondary_image_titles[]"
                    # o indexed names como "secondary_image_titles[0]".
                    secondary_titles = (
                        request.form.getlist("secondary_image_titles")
                        or request.form.getlist("secondary_image_titles[]")
                        or []
                    )
                    secondary_descriptions = (
                        request.form.getlist("secondary_image_descriptions")
                        or request.form.getlist("secondary_image_descriptions[]")
                        or []
                    )

                    # Si no encontramos títulos con las claves simples, buscar claves indexadas
                    if not secondary_titles:
                        indexed_keys = [
                            k
                            for k in request.form.keys()
                            if k.startswith("secondary_image_titles[")
                        ]
                        if indexed_keys:
                            # ordenar por índice si es posible
                            def _idx_key(k):
                                try:
                                    i = int(k[k.find("[") + 1 : k.find("]")])
                                    return i
                                except Exception:
                                    return 0

                            indexed_keys.sort(key=_idx_key)
                            secondary_titles = [
                                request.form.get(k) for k in indexed_keys
                            ]

                    if not secondary_descriptions:
                        indexed_keys = [
                            k
                            for k in request.form.keys()
                            if k.startswith("secondary_image_descriptions[")
                        ]
                        if indexed_keys:

                            def _idx_key2(k):
                                try:
                                    i = int(k[k.find("[") + 1 : k.find("]")])
                                    return i
                                except Exception:
                                    return 0

                            indexed_keys.sort(key=_idx_key2)
                            secondary_descriptions = [
                                request.form.get(k) for k in indexed_keys
                            ]

                    # Logging debug (prefer logger sobre print)
                    current_app.logger.debug("Secondary titles: %s", secondary_titles)

                    for idx, img in enumerate(secondary_images):
                        if img and img.filename:
                            file = img
                            size = fstat(file.fileno()).st_size
                            bucket_name = current_app.config["MINIO_BUCKET_NAME"]
                            object_name = f"sites/{site_id}/{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}"

                            client.put_object(
                                bucket_name=bucket_name,
                                object_name=object_name,
                                data=file,
                                length=size,
                                content_type=img.content_type,
                            )

                            # Obtener el order máximo actual para las imágenes del sitio
                            max_order = images.get_max_order_for_site(site_id) or 0
                            new_order = max_order + idx + 1

                            # Obtener título y descripción correspondiente al índice
                            titulo = (
                                secondary_titles[idx]
                                if idx < len(secondary_titles)
                                else f"Imagen secundaria {idx + 1}"
                            )
                            descripcion = (
                                secondary_descriptions[idx]
                                if idx < len(secondary_descriptions)
                                else "Imagen secundaria del sitio histórico"
                            )

                            # Crear registro de imagen con order incremental
                            images.create_image(
                                site_id=site_id,
                                url=object_name,
                                order=new_order,
                                titulo=titulo,
                                descripcion=descripcion,
                            )

            # Asignar tags seleccionados
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
                flash(f"Sitio creado pero no se pudieron asignar tags: {e}", "warning")

            flash("Sitio creado correctamente.", "success")
            return redirect(url_for("sites.show_site", site_id=site.id))
        else:
            if form.errors:
                for field, errors in form.errors.items():
                    for error in errors:
                        flash(f"Error en el campo {field}: {error}", "danger")
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
            if "main_image" in request.files:
                primary_img = request.files["main_image"]
                if primary_img and primary_img.filename:
                    file = primary_img
                    size = fstat(file.fileno()).st_size
                    bucket_name = current_app.config["MINIO_BUCKET_NAME"]
                    # ulid = file.filename  # Simplificado para este ejemplo
                    object_name = f"sites/{site_id}/{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}"
                    client = current_app.storage
                    client.put_object(
                        bucket_name=bucket_name,
                        object_name=object_name,
                        data=file,
                        length=size,
                        content_type=primary_img.content_type,
                    )
                    # Devolver en params el path del objeto subido
                    titulo = request.form.get("main_image_title", "Imagen principal")
                    descripcion = request.form.get(
                        "main_image_description", "Imagen principal del sitio histórico"
                    )
                    images.create_image(
                        site_id=site_id,
                        url=object_name,
                        order=0,
                        titulo=titulo,
                        descripcion=descripcion,
                    )

            if "secondary_images" in request.files:
                client = current_app.storage
                secondary_images = request.files.getlist("secondary_images")

                # Obtener títulos y descripciones de las imágenes secundarias.
                # Aceptar varias convenciones de nombre que pueden venir
                # del template/JS: "secondary_image_titles", "secondary_image_titles[]"
                # o indexed names como "secondary_image_titles[0]".
                secondary_titles = (
                    request.form.getlist("secondary_image_titles")
                    or request.form.getlist("secondary_image_titles[]")
                    or []
                )
                secondary_descriptions = (
                    request.form.getlist("secondary_image_descriptions")
                    or request.form.getlist("secondary_image_descriptions[]")
                    or []
                )

                # Si no encontramos títulos con las claves simples, buscar claves indexadas
                if not secondary_titles:
                    indexed_keys = [
                        k
                        for k in request.form.keys()
                        if k.startswith("secondary_image_titles[")
                    ]
                    if indexed_keys:

                        def _idx_key(k):
                            try:
                                i = int(k[k.find("[") + 1 : k.find("]")])
                                return i
                            except Exception:
                                return 0

                        indexed_keys.sort(key=_idx_key)
                        secondary_titles = [request.form.get(k) for k in indexed_keys]

                if not secondary_descriptions:
                    indexed_keys = [
                        k
                        for k in request.form.keys()
                        if k.startswith("secondary_image_descriptions[")
                    ]
                    if indexed_keys:

                        def _idx_key2(k):
                            try:
                                i = int(k[k.find("[") + 1 : k.find("]")])
                                return i
                            except Exception:
                                return 0

                        indexed_keys.sort(key=_idx_key2)
                        secondary_descriptions = [
                            request.form.get(k) for k in indexed_keys
                        ]

                current_app.logger.debug(
                    "Secondary titles (edit): %s", secondary_titles
                )

                for idx, img in enumerate(secondary_images):
                    if img and img.filename:
                        file = img
                        size = fstat(file.fileno()).st_size
                        bucket_name = current_app.config["MINIO_BUCKET_NAME"]
                        object_name = f"sites/{site_id}/{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}"

                        client.put_object(
                            bucket_name=bucket_name,
                            object_name=object_name,
                            data=file,
                            length=size,
                            content_type=img.content_type,
                        )

                        # Obtener el order máximo actual para las imágenes del sitio
                        max_order = images.get_max_order_for_site(site_id) or 0
                        new_order = max_order + idx + 1

                        # Obtener título y descripción correspondiente al índice
                        titulo = (
                            secondary_titles[idx].strip()
                            if idx < len(secondary_titles)
                            and secondary_titles[idx]
                            and secondary_titles[idx].strip()
                            else f"Imagen secundaria {idx + 1}"
                        )
                        descripcion = (
                            secondary_descriptions[idx].strip()
                            if idx < len(secondary_descriptions)
                            and secondary_descriptions[idx]
                            and secondary_descriptions[idx].strip()
                            else "Imagen secundaria del sitio histórico"
                        )

                        # Crear registro de imagen con order incremental
                        images.create_image(
                            site_id=site_id,
                            url=object_name,
                            order=new_order,
                            titulo=titulo,
                            descripcion=descripcion,
                        )
                        current_app.logger.debug(
                            "Imagen secundaria subida y registrada: %s", object_name
                        )

            # Tags
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
                site = historicalSites.get_site_by_id(site_id)
                historicalSites.asignar_tags_a_sitio(site, tag_objs)
            except Exception as e:
                flash(f"No se pudieron actualizar los tags: {e}", "warning")

                # Manejar cambio de imagen principal
            new_main_image_id = request.form.get("new_main_image_id")
            if new_main_image_id:
                # La nueva imagen principal
                new_main = images.get_image_by_id(int(new_main_image_id))
                # # La antigua imagen principal
                # old_main = images.get_image_by_id(int(new_main_image_id))

                # if new_main and new_main.site_id == site.id:
                #     if old_main and old_main.id != new_main.id:
                #         # Intercambiar: la antigua principal pasa a secundaria
                #         images.set_image_order(old_main, new_main.order)
                #     # La nueva imagen pasa a ser principal (orden 0)
                #     images.set_image_order(new_main, 0)
                images.set_image_order(new_main, 0)

            # Manejar eliminación de imágenes
            images_to_delete = request.form.getlist("delete_images[]")
            for image_id in images_to_delete:
                image = images.get_image_by_id(int(image_id))
                if image and image.site_id == site.id:
                    images.delete_image(image)

            # Actualizar orden de imágenes existentes
            image_orders = request.form.to_dict(flat=False)
            for key, value in image_orders.items():
                if key.startswith("image_orders["):
                    image_id = int(key.replace("image_orders[", "").replace("]", ""))
                    new_order = int(value[0])
                    image = images.get_image_by_id(image_id)
                    if image and image.site_id == site.id:
                        images.set_image_order(image, new_order)

            return redirect(url_for("sites.list_sites"))
        else:
            if form.errors:
                for field, errors in form.errors.items():
                    for error in errors:
                        flash(f"Error en el campo {field}: {error}", "danger")
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
    """Exporta CSV replicando EXACTAMENTE los filtros/orden del listado.
    Si no vienen en query, intenta recuperarlos del referrer (fallback)."""
    from io import StringIO

    # 1) Tomar filtros de la query actual o del referrer si está vacío
    if request.args and len(request.args) > 0:
        parsed = _parse_list_filters(request.args)
        ref = request.headers.get("Referer")
    else:
        ref = request.headers.get("Referer")
        if ref:
            q = parse_qs(urlparse(ref).query)  # dict: key -> [values]
            md = MultiDict(
                [(k, v) for k, vals in q.items() for v in vals]
            )  # simula get/getlist
            parsed = _parse_list_filters(md)
        else:
            parsed = _parse_list_filters(request.args)  # sin filtros

    # 2) Usar el MISMO servicio que el listado, sin paginar (per_page grande)
    page = 1
    per_page = 1_000_000
    sites_page = historicalSites.get_sites_paginated_by_id(
        page=page,
        per_page=per_page,
        order=parsed["order_dir"],
        order_by=parsed["order_by"],
        city=parsed["city"],
        province=parsed["province"],
        tags=parsed["tags"],
        conservation_status=parsed["conservation_status"],
        date_from=parsed["date_from"],
        date_to=parsed["date_to"],
        visibility=parsed["visibility"],
        search_text=parsed["search_text"],
    )
    sites = getattr(sites_page, "items", sites_page) or []

    # 3) Freno: si no hay resultados, no exportar CSV
    if not sites:
        flash("No hay resultados para exportar con los filtros aplicados.", "warning")
        return redirect(ref or url_for("sites.list_sites"))

    # 4) Construir CSV
    si = StringIO()
    writer = csv.writer(si, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(
        [
            "Nombre",
            "Descripción breve",
            "Descripción completa",
            "Ciudad",
            "Provincia",
            "Ubicación (lat,lon)",
            "Estado de conservación",
            "Año de declaración",
            "Categoría",
            "Fecha de registro",
            "Tags",
        ]
    )

    for s in sites:
        tags_str = " | ".join([t.name for t in getattr(s, "tags", [])])
        status_label = get_status_label(getattr(s, "conservation_status", None)) or ""
        category_label = get_category_label(getattr(s, "category", None)) or ""
        location_str = getattr(s, "location", "") or ""

        writer.writerow(
            [
                getattr(s, "name", "") or "",
                getattr(s, "description_short", "") or "",
                getattr(s, "description", "") or "",
                getattr(s, "city", "") or "",
                getattr(s, "province", "") or "",
                str(location_str),
                status_label,
                getattr(s, "year_declared", "") or "",
                category_label,
                getattr(s, "registration_date", "") or "",
                tags_str,
            ]
        )

    csv_str = "\ufeff" + si.getvalue()  # BOM para Excel
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return Response(
        csv_str,
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename=sitios_{ts}.csv"},
    )
