from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from src.core.historicalSites.tags import (
    get_tag_by_name,
    get_tag_by_id,
    create_tag,
    update_tag,
    delete_tag as delete_tag_helper,
    crear_slug,
    get_tags_paginated,
)
from src.core.historicalSites.tags.tag import Tag
from src.core.permissions.permission import UserPermission
from src.web.auth import permission_required
from src.web.helpers import login_required

tags_bp = Blueprint("tags", __name__, url_prefix="/tags")


@tags_bp.before_request
@permission_required(UserPermission.SITE_TAGS)
def bp_guard():
    """Blueprint guard to check permissions before each request."""
    pass


@tags_bp.route("/", methods=["GET"])
@login_required
def list_tags():
    """Lista y busca tags con paginación"""
    busqueda = request.args.get("stringBusqueda", "", type=str)
    page = request.args.get("page", 1, type=int)
    per_page = 25
    order_by = request.args.get("order_by", "name", type=str)
    order_dir = request.args.get("order_dir", "asc", type=str)

    # Solo llama a la capa de servicios
    tags_paginated = get_tags_paginated(
        busqueda, page, per_page, order_by=order_by, order_dir=order_dir
    )

    return render_template(
        "historicalSites/tags/indexTags.html",
        tags=tags_paginated,
        busqueda=busqueda,
        current_query={"stringBusqueda": busqueda},
        order_by=order_by,
        order_dir=order_dir,
    )


# Ruta para crear un nuevo tag
@tags_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_tag():
    """Crear un nuevo tag"""
    errors = {}
    if request.method == "POST":
        name = request.form.get("name")
        slug = crear_slug(name)
        description = request.form.get("description")

        # Validaciones
        if not name:
            errors["name"] = "El nombre es obligatorio."
        else:
            if get_tag_by_name(name):
                errors["name"] = "Ya existe un tag con ese nombre."

        # Manejo de errores en el formulario
        if errors:
            return render_template(
                "historicalSites/tags/newTag.html",
                name=name,
                description=description,
                errors=errors,
            )

        # Mando el tag creado sin errores a la base de datos
        try:
            created = create_tag(name=name, slug=slug, description=description)
            flash("El tag se creó correctamente.", "success")
            # Redirigir a la vista de detalle del tag recién creado
            return redirect(url_for("tags.show_tag", tag_id=created.id))
        except Exception as e:
            flash("Error al crear el tag: " + str(e), "danger")

    # Si es un GET, renderizar el formulario
    return render_template("historicalSites/tags/newTag.html")


@tags_bp.route("/<int:tag_id>/edit", methods=["GET", "POST"])
@login_required
def edit_tag(tag_id):
    """Editar un tag existente"""
    # obtener el tag o 404
    tag = Tag.query.get_or_404(tag_id)

    errors = {}
    if request.method == "POST":
        # leo valores enviados
        name = request.form.get("name")
        description = request.form.get("description")
        # validaciones
        if not name:
            errors["name"] = "El nombre es obligatorio."
        else:
            # verifico unicidad del nombre excluyendo el propio registro
            existing_tag = get_tag_by_name(name)
            if existing_tag and existing_tag.id != tag.id:
                errors["name"] = "Ya existe un tag con ese nombre."

        if errors:
            # devolver los mismos valores y errores para mostrar en el form
            return render_template(
                "historicalSites/tags/editTag.html",
                tag=tag,
                name=name,
                description=description,
                errors=errors,
            )

        # aplicar cambios y guardar
        try:
            # genero nuevo slug si cambió el nombre
            if name != tag.name:
                slug = crear_slug(name)
                tag.slug = slug
            else:
                slug = tag.slug  # mantener el slug actual si no cambió el nombre
            update_tag(tag_id=tag.id, name=name, slug=slug, description=description)
            flash("El tag se actualizó correctamente.", "success")
            return redirect(url_for("tags.list_tags"))
        except Exception as e:
            flash("Error al actualizar el tag: " + str(e), "danger")
            return render_template(
                "historicalSites/tags/editTag.html",
                tag=tag,
                name=name,
                description=description,
                errors={"form": "Error al guardar."},
            )

    # Esto seria el GET
    return render_template(
        "historicalSites/tags/editTag.html",
        tag=tag,
        name=tag.name,
        description=tag.description,
    )


@tags_bp.route("/<int:tag_id>", methods=["GET"])
@login_required
def show_tag(tag_id):
    """Mostrar detalles de un tag"""
    tag = get_tag_by_id(tag_id)
    if not tag:
        return "Tag not found", 404
    return render_template("historicalSites/tags/showTag.html", tag=tag)


@tags_bp.route("/<int:tag_id>/delete", methods=["POST"])
@login_required
def delete_tag(tag_id):
    """Eliminar un tag"""
    tag = get_tag_by_id(tag_id)
    # Si el tag tiene sitios asociados -> devolver error en AJAX
    if tag.sites:
        msg = "No se puede eliminar el tag porque está asociado a uno o más sitios históricos."
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify(message=msg), 400
        flash(msg, "warning")
        return redirect(url_for("tags.list_tags"))

    try:
        delete_tag_helper(tag_id)  # función helper
        msg_ok = "El tag se eliminó correctamente."
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify(message=msg_ok), 200
        flash(msg_ok, "success")
    except Exception as e:
        msg_err = "Error al eliminar el tag: " + str(e)
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify(message=msg_err), 500
        flash(msg_err, "danger")
    return redirect(url_for("tags.list_tags"))
