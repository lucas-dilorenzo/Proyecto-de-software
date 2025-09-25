from flask import Blueprint, render_template
from core.historicalSites.tags.tag import Tag
from src.core.database import db
from src.core.historicalSites.tags import get_all_tags

tags_bp = Blueprint("tags", __name__, url_prefix="/tags")

@tags_bp.route("/", methods=["GET"])
def list_tags():
    tags = get_all_tags();
    return render_template("historicalSites/tags/indexTags.html", tags=tags)