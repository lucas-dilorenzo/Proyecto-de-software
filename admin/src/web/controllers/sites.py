from src.core import historicalSites
from flask import Blueprint, render_template

historical_sites_bp = Blueprint("sites", __name__, url_prefix="/sites")


@historical_sites_bp.route("/", methods=["GET"])
def list_sites():
    sites = historicalSites.list_all_sites()
    return render_template("historicalSites/listSites.html", sites=sites)
