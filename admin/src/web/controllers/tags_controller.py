from flask import Blueprint, render_template, request, flash, redirect, url_for
from src.core.historicalSites.tags import get_all_tags, get_tag_by_name, create_tag, crear_slug
from src.core.historicalSites.tags.tag import Tag
import re

tags_bp = Blueprint("tags", __name__, url_prefix="/tags")


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
            duplicate = Tag.query.filter(Tag.name == name, Tag.id != tag.id).first()
            if duplicate:
                errors["name"] = "Ya existe un tag con ese nombre."

        # (opcional) generar slug si cambió el nombre; usar la función slugify central
        nuevo_slug = crear_slug(name) if name else ""
        # para mantener el slug del tag cuando no cambie el nombre
        slug_final = tag.slug
        if nuevo_slug and nuevo_slug != tag.slug:
            # generar slug si cambio el nombre
            slug_final = nuevo_slug

        if errors:
            # devolver los mismos valores y errores para mostrar en el form
            return render_template("historicalSites/tags/editTag.html",
                                   tag=tag, name=name, description=description, errors=errors)

        # aplicar cambios y guardar
        try:
            tag.name = name
            tag.slug = slug_final
            tag.description = description
            db.session.commit()
            flash("Tag actualizado correctamente.", "success")
            return redirect(url_for("tags.list_tags"))
        except Exception as e:
            db.session.rollback()
            flash("Error al actualizar el tag: " + str(e), "danger")
            return render_template("historicalSites/tags/editTag.html",
                                   tag=tag, name=name, description=description, errors={"form": "Error al guardar."})

    # GET: mostrar formulario con los datos actuales
    return render_template("historicalSites/tags/editTag.html", tag=tag, name=tag.name, description=tag.description)