from flask import Blueprint, render_template
from src.core import historicalSites
tags_bp = Blueprint("tags", __name__, url_prefix="/tags")

@tags_bp.route("/", methods=["GET"])
def list_tags():
    tags = "";
    return render_template("historicalSites/tags/indexTags.html", tags=tags)