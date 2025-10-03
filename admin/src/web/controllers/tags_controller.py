from flask import Blueprint, render_template, request, flash, redirect, url_for
from src.core.historicalSites.tags import get_tag_by_name, get_tag_by_id, create_tag, update_tag, delete_tag as delete_tag_helper, crear_slug
from src.core.historicalSites.tags.tag import Tag
from src.core.permissions.permission import UserPermission
from src.web.auth import permission_required
import re

tags_bp = Blueprint("tags", __name__, url_prefix="/tags")

@tags_bp.before_request
@permission_required(UserPermission.SITE_TAGS)
def bp_guard():
    pass

@tags_bp.route("/", methods=["GET"])
def list_tags():
    busqueda = request.args.get("stringBusqueda", "", type=str)
    query = Tag.query
    if busqueda:
        query = query.filter(Tag.name.ilike(f"%{busqueda}%"))

    tags = query.order_by(Tag.created_at.desc()).all()
    return render_template("historicalSites/tags/indexTags.html", tags=tags, busqueda=busqueda)

# Ruta para crear un nuevo tag
@tags_bp.route("/new", methods=["GET", "POST"])
def new_tag():
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
            create_tag(name=name, slug=slug, description=description)
            flash("El tag se creó correctamente.", "success")
            return redirect(url_for("tags.list_tags"))
        except Exception as e:
            flash("Error al crear el tag: " + str(e), "danger")

    # Si es un GET, renderizar el formulario
    return render_template("historicalSites/tags/newTag.html")

@tags_bp.route("/<int:tag_id>/edit", methods=["GET", "POST"])
def edit_tag(tag_id):
    # obtener el tag o 404
    tag = Tag.query.get_or_404(tag_id)
    
    errors = {}
    if request.method == "POST":
        # leo valores enviados
        name = (request.form.get("name"))
        description = (request.form.get("description")) 
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
                tag=tag, name=name, description=description, errors=errors
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
            return render_template("historicalSites/tags/editTag.html",
            tag=tag, name=name, description=description, errors={"form": "Error al guardar."})

    # GET: mostrar formulario con los datos actuales
    return render_template("historicalSites/tags/editTag.html", tag=tag, name=tag.name, description=tag.description)

@tags_bp.route("/<int:tag_id>/delete", methods=["POST"])
def delete_tag(tag_id):
    # obtener el tag o 404
    tag = Tag.query.get_or_404(tag_id)
    try:
        delete_tag_helper(tag_id)  # función helper
        flash("El tag se eliminó correctamente.", "success")
    except Exception as e:
        flash("Error al eliminar el tag: " + str(e), "danger")
    return redirect(url_for("tags.list_tags"))
