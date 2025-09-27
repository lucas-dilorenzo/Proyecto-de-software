from flask import Blueprint, render_template, request, flash, redirect, url_for
from src.core.historicalSites.tags import get_all_tags, get_tag_by_name, create_tag
from src.core.historicalSites.tags.tag import Tag

tags_bp = Blueprint("tags", __name__, url_prefix="/tags")


@tags_bp.route("/", methods=["GET"])
def list_tags():
    # tags = get_all_tags()
    # return render_template("historicalSites/tags/indexTags.html", tags=tags)
    busqueda = request.args.get("stringBusqueda", "", type=str)
    query = Tag.query
    if busqueda:
        query = query.filter(Tag.name.ilike(f"%{busqueda}%"))

    tags = query.order_by(Tag.created_at.desc()).all()
    return render_template("historicalSites/tags/indexTags.html", tags=tags, busqueda=busqueda)

# Ruta para crear un nuevo tag
@tags_bp.route("/new", methods=["GET", "POST"])
def new_tag():
    if request.method == "POST":
        name = request.form.get("name")
        slug = request.form.get("slug")
        description = request.form.get("description")

        # Validaciones
        if not name or not slug:
            flash("El nombre y el slug son obligatorios.", "danger")
            return render_template("historicalSites/tags/newTag.html")
        nombreExistente = get_tag_by_name(name)
        if nombreExistente:
            flash("Ya existe un tag con ese nombre.", "danger")
            return render_template("historicalSites/tags/newTag.html", name=name, slug=slug, description=description)

        # Crear un nuevo objeto Tag
        new_tag = Tag(name=name, slug=slug, description=description)

        # Guardar en la base de datos
        try:
            create_tag(name=name, slug=slug, description=description)
            flash("El tag se creó correctamente.", "success")
            return redirect(url_for("tags.list_tags"))
        except Exception as e:
            flash("Error al crear el tag: " + str(e), "danger")

    # Si es un GET, renderizar el formulario
    return render_template("historicalSites/tags/newTag.html")