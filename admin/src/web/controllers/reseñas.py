from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify

reseñas_bp = Blueprint("reseñas", __name__, url_prefix="/reseñas")

@reseñas_bp.route("/", methods=["GET"])
def list_reseñas():
    # Lógica para listar reseñas
    return render_template("reseñas/list_reseñas.html")

@reseñas_bp.route("/<int:id>", methods=["GET"])
def ver_reseña(id):
    # Lógica para ver una reseña específica
    return render_template("reseñas/ver.html", id=id)
