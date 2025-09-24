from src.core import historicalSites
from flask import Blueprint, redirect, render_template, request, url_for

historical_sites_bp = Blueprint("sites", __name__, url_prefix="/sites")


@historical_sites_bp.route("/", methods=["GET"])
def list_sites():
    # if not authenticated(session):
    # abort(401)

    # if not has_permission(session["user"].id, permission="asc_index"):
    #     abort(403)
    page = request.args.get("page", 1, type=int)
    sites = historicalSites.get_sites_paginated_by_id(
        page=page, per_page=3, order="asc"
    )
    return render_template("historicalSites/list_sites.html", sites=sites)


@historical_sites_bp.route("/<int:site_id>", methods=["GET"])
def show_site(site_id):
    site = historicalSites.get_site_by_id(site_id)
    if site is None:
        return "Site not found", 404
    return render_template("historicalSites/show_site.html", site=site)


@historical_sites_bp.route("/create", methods=["GET", "POST"])
def create_site():
    if request.method == "POST":
        # Logic to create a new site
        return redirect(url_for("sites.list_sites"))
    return render_template("historicalSites/create_site.html")


@historical_sites_bp.route("/<int:site_id>/edit", methods=["GET", "POST"])
def edit_site(site_id):
    site = historicalSites.get_site_by_id(site_id)
    if site is None:
        return "Site not found", 404
    return render_template("historicalSites/edit_site.html", site=site)


@historical_sites_bp.route("/<int:site_id>/delete", methods=["POST"])
def delete_site(site_id):
    site = historicalSites.get_site_by_id(site_id)
    if site is None:
        return "Site not found", 404
    # Logic to delete the site would go here
    return f"Site {site.name} deleted", 200
