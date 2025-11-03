from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, session
from src.core.reseñas import (
    get_reviews_paginated, get_review_by_id, aprobar_reseña, rechazar_reseña
)
from src.core.historicalSites import get_all_sites
from src.core.reseñas.estadoReseña import estadoReseña
from src.web.helpers import login_required


reseñas_bp = Blueprint("reseñas", __name__, url_prefix="/reseñas")

# @reseñas_bp.before_request
# @permission_required(UserPermission.REVIEW_MODERATE)
# def bp_guard():
#     """Blueprint guard to check permissions before each request."""
#     pass

@reseñas_bp.route("/reseñas", methods=["GET"])
@login_required
def list_reseñas():
    """Lista las reseñas con paginación y filtros para moderación"""
    page = request.args.get("page", 1, type=int)
    estado = request.args.get("estado", type=str) 
    site_id = request.args.get("site", type=int) 
    calificacion = request.args.get("calificacion", type=int)
    fecha_desde = request.args.get("fecha_desde", type=str)
    fecha_hasta = request.args.get("fecha_hasta", type=str)
    usuario = request.args.get("usuario", type=str)

    # Parámetros de ordenamiento
    order_by = request.args.get("order_by", default="fecha_creacion", type=str)
    order_dir = request.args.get("order_dir", default="desc", type=str)
    
    reviews_paginated = get_reviews_paginated(
        page=page,
        per_page=10,
        order=order_dir,
        order_by=order_by,
        estado=estado,
        site_id=site_id,
        calificacion=calificacion,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        usuario=usuario,
    )

    # Listado de sitios para el filtro 'site'
    all_sites = get_all_sites()
    
    has_filters = any(
        [
            estado,
            site_id,
            calificacion,
            fecha_desde,
            fecha_hasta,
            usuario,
        ]
    )

    current_query = {}
    for k in request.args:
        # Excluimos 'page', 'order_by', 'order_dir' y los parámetros vacíos
        if k not in ['page', 'order_by', 'order_dir'] and request.args.get(k):
            current_query[k] = request.args.get(k)
            
    return render_template(
        "reseñas/list_reseñas.html",
        reviews=reviews_paginated,
        pagination=reviews_paginated, 
        
        # Parámetros de filtrado para mantener el estado del formulario
        estado=estado,
        site_id=site_id,
        calificacion=calificacion,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        usuario=usuario,
        all_sites=all_sites,
        review_statuses=estadoReseña, 
        has_filters=has_filters,
        current_query=current_query,
        order_by=order_by,
        order_dir=order_dir,
    )


@reseñas_bp.route("/<int:review_id>", methods=["GET"])
@login_required
def show_review(review_id):
    """
    Muestra los detalles de una reseña específica.
    Args:
        review_id (int): ID de la reseña a mostrar.
    """
    review = get_review_by_id(review_id)
    if not review:
        return "Review not found", 404
    return render_template("reseñas/show_reseña.html", review=review)


@reseñas_bp.route("/<int:review_id>/aprobar", methods=["POST"])
@login_required
def approve_review(review_id):
    """
    Aprueba una reseña específica.
    Args:
        review_id (int): ID de la reseña a aprobar.
    """
    # Verificar permisos (solo MODERATOR, ADMIN, SYS_ADMIN pueden aprobar)
    if session.get('role') not in ['MODERATOR', 'ADMIN', 'SYS_ADMIN']:
        return jsonify({'success': False, 'message': 'No tienes permisos para aprobar reseñas'}), 403
    
    success = aprobar_reseña(review_id)
    
    if success:
        flash('Reseña aprobada correctamente', 'success')
        return jsonify({'success': True, 'message': 'Reseña aprobada correctamente'})
    else:
        flash('Error al aprobar la reseña', 'error')
        return jsonify({'success': False, 'message': 'Error al aprobar la reseña'}), 500


@reseñas_bp.route("/<int:review_id>/rechazar", methods=["POST"])
@login_required
def reject_review(review_id):
    """
    Rechaza una reseña específica con un motivo.
    Args:
        review_id (int): ID de la reseña a rechazar.
    """
    # falta verificar permisos (solo MODERATOR, ADMIN, SYS_ADMIN pueden rechazar)
    if session.get('role') not in ['MODERATOR', 'ADMIN', 'SYS_ADMIN']:
        return jsonify({'success': False, 'message': 'No tienes permisos para rechazar reseñas'}), 403
    
    data = request.get_json()
    motivo_rechazo = data.get('motivo', '').strip()
    
    if not motivo_rechazo:
        return jsonify({'success': False, 'message': 'Debes proporcionar un motivo para el rechazo'}), 400
    
    if len(motivo_rechazo) > 200:
        return jsonify({'success': False, 'message': 'El motivo de rechazo no puede superar los 200 caracteres'}), 400
    
    success = rechazar_reseña(review_id, motivo_rechazo)
    
    if success:
        flash('Reseña rechazada correctamente', 'success')
        return jsonify({'success': True, 'message': 'Reseña rechazada correctamente'})
    else:
        flash('Error al rechazar la reseña', 'error')
        return jsonify({'success': False, 'message': 'Error al rechazar la reseña'}), 500