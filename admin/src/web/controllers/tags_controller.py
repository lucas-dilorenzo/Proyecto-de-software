from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from src.core.historicalSites.tags import (
    get_tag_by_name,
    get_tag_by_id,
    create_tag,
    update_tag,
    delete_tag as delete_tag_helper,
    crear_slug,
    get_tags_paginated,
    get_tag_by_slug,
)
from src.core.historicalSites.tags.tag import Tag
from src.core.permissions.permission import UserPermission
from src.web.auth import permission_required
from src.web.helpers import login_required
from src.web.helpers.validations.tags import TagForm

tags_bp = Blueprint("tags", __name__, url_prefix="/tags")


@tags_bp.before_request
@permission_required(UserPermission.SITE_TAGS)
def bp_guard():
    """Blueprint guard to check permissions before each request."""
    pass


@tags_bp.route("/", methods=["GET"])
@login_required
def list_tags():
    """
    Muestra la lista paginada de tags con funcionalidades de búsqueda y ordenamiento.
    Obtiene los parámetros de query string para filtrar, paginar y ordenar los tags.

    Query Parameters:
        stringBusqueda (str, optional): para filtrar por nombre.
        page (int, optional): Número de página para paginación. Default: 1.
        order_by (str, optional): Campo por el cual ordenar. Default: 'name'.
        order_dir (str, optional): Dirección del ordenamiento ('asc'/'desc'). Default: 'asc'.
    """
    busqueda = request.args.get("stringBusqueda", "", type=str)
    page = request.args.get("page", 1, type=int)
    per_page = 10
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


@tags_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_tag():
    """
    Maneja la creación de un tag.

    El slug se genera automáticamente a partir del nombre ingresado.
    Utiliza FlaskForm para validación.

    - POST exitoso: Redirige a la vista de detalle del tag creado.
    - POST con errores: Re-renderiza el formulario con mensajes de error.
    """
    form = TagForm()

    if form.validate_on_submit():
        # Si pasa la validación, creo el tag
        name = form.name.data
        description = form.description.data
        slug = crear_slug(name)

        try:
            newTag = create_tag(name=name, slug=slug, description=description)
            flash("El tag se creó correctamente.", "success")
            # Redirigir a la vista de detalle del tag recién creado
            return redirect(url_for("tags.show_tag", tag_id=newTag.id))
        except Exception as e:
            flash("Error al crear el tag: " + str(e), "danger")
    # Si es un GET o si hay errores en el POST, renderizar el formulario
    return render_template("historicalSites/tags/newTag.html", form=form)


@tags_bp.route("/<int:tag_id>/edit", methods=["GET", "POST"])
@login_required
def edit_tag(tag_id):
    """
    Maneja la edición de un tag existente.

    Args:
        tag_id (int): ID del tag.

    - POST exitoso: Redirige a la lista de tags con mensaje de éxito.
    - POST con errores: Re-renderiza el formulario con mensajes de error.
    - El slug se regenera solo si el nombre cambia.
    """

    tag = get_tag_by_id(tag_id)

    # Crear el form con el ID del tag para las validaciones de unicidad
    form = TagForm(tag_id=tag_id, obj=tag)

    if form.validate_on_submit():
        # Si pasa la validación, actualizo el tag
        name = form.name.data
        description = form.description.data

        try:
            if name != tag.name:
                slug = crear_slug(name)
            else:
                slug = tag.slug  # mantener el slug actual si no cambió el nombre

            update_tag(tag_id=tag.id, name=name, slug=slug, description=description)
            flash("El tag se actualizó correctamente.", "success")
            return redirect(url_for("tags.list_tags"))
        except Exception as e:
            flash("Error al actualizar el tag: " + str(e), "danger")

    # Si es un GET o si hay errores en el POST, renderizar el formulario
    return render_template("historicalSites/tags/editTag.html", tag=tag, form=form)


@tags_bp.route("/<int:tag_id>", methods=["GET"])
@login_required
def show_tag(tag_id):
    """
    Muestra los detalles de un tag específico.
    Args:
        tag_id (int): ID del tag a mostrar.

    """
    tag = get_tag_by_id(tag_id)
    if not tag:
        return "Tag not found", 404
    return render_template("historicalSites/tags/showTag.html", tag=tag)


@tags_bp.route("/<int:tag_id>/delete", methods=["POST"])
@login_required
def delete_tag(tag_id):
    """
    Elimina un tag, verificando que no esté asociado a sitios históricos.

    Args:
        tag_id (int): ID del tag a eliminar.

    - AJAX exitoso: JSON con mensaje de éxito (200).
    - AJAX con error: JSON con mensaje de error (400/500).
    """
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
