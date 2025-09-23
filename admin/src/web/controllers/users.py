from flask import Blueprint, request, render_template, redirect, url_for, flash, abort
from sqlalchemy import select, desc, asc, func
from werkzeug.security import generate_password_hash
from web.auth import admin_required
from web.validators.users import validate_user_payload
from core.database import db
from core.models import User, UserRole

users_bp = Blueprint("users", __name__, url_prefix="/admin/users")


def _clamp_per_page(val) -> int:
    try:
        n = int(val)
    except Exception:
        n = 25
    return max(1, min(n, 25))  # máx 25


@users_bp.get("/")
@admin_required
def list_users():
    email = (request.args.get("email") or "").strip()
    activo = (request.args.get("activo") or "").strip().upper()  # "SI" | "NO" | ""
    rol = (request.args.get("rol") or "").strip()
    order = (request.args.get("order") or "desc").lower()  # "asc"|"desc"
    page = max(1, int(request.args.get("page", 1)))
    per_page = _clamp_per_page(request.args.get("per_page", 25))

    q = select(User)
    if email:
        q = q.where(func.lower(User.email).like(f"%{email.lower()}%"))
    if activo in ("SI", "NO"):
        q = q.where(User.activo == (activo == "SI"))
    if rol in (r.value for r in UserRole):
        q = q.where(User.rol == UserRole(rol))

    if order == "asc":
        q = q.order_by(asc(User.created_at), User.id)
    else:
        q = q.order_by(desc(User.created_at), desc(User.id))

    total = db.session.execute(
        select(func.count()).select_from(q.subquery())
    ).scalar_one()
    items = (
        db.session.execute(q.limit(per_page).offset((page - 1) * per_page))
        .scalars()
        .all()
    )

    def qs(**overrides):
        base = request.args.to_dict()
        base.update({k: v for k, v in overrides.items() if v is not None})
        return "&".join(f"{k}={v}" for k, v in base.items() if v not in ("", None))

    return render_template(
        "users/list.html",
        users=items,
        total=total,
        page=page,
        per_page=per_page,
        email=email,
        activo=activo,
        rol=rol,
        order=order,
        roles=[r.value for r in UserRole],
        qs=qs,
    )


# --------- CREATE ----------
@users_bp.get("/new")
@admin_required
def new_user():
    # valores por defecto
    form = {
        "email": "",
        "nombre": "",
        "apellido": "",
        "password": "",
        "activo": "SI",
        "rol": "Usuario público",
    }
    return render_template("users/form.html", form=form, errors={}, mode="create")


@users_bp.post("/new")
@admin_required
def create_user():
    form = {
        "email": (request.form.get("email") or "").strip(),
        "nombre": (request.form.get("nombre") or "").strip(),
        "apellido": (request.form.get("apellido") or "").strip(),
        "password": request.form.get("password") or "",
        "activo": (request.form.get("activo") or "").strip().upper(),
        "rol": (request.form.get("rol") or "").strip(),
    }
    ok, errors = validate_user_payload(form, is_update=False)
    if ok:
        # unicidad de email
        exists = db.session.execute(
            select(User).where(func.lower(User.email) == form["email"].lower())
        ).scalar_one_or_none()
        if exists:
            errors["email"] = "Ya existe un usuario con ese email."

    if not ok or errors:
        return (
            render_template("users/form.html", form=form, errors=errors, mode="create"),
            400,
        )

    u = User(
        email=form["email"],
        nombre=form["nombre"],
        apellido=form["apellido"],
        password_hash=generate_password_hash(form["password"]),
        activo=(form["activo"] == "SI"),
        rol=UserRole(form["rol"]),
    )
    db.session.add(u)
    db.session.commit()
    flash("Usuario creado correctamente.", "success")
    return redirect(url_for("users.list_users"))


# --------- UPDATE ----------
@users_bp.get("/<int:uid>/edit")
@admin_required
def edit_user(uid: int):
    u = db.session.get(User, uid)
    if not u:
        abort(404)
    form = {
        "email": u.email,
        "nombre": u.nombre,
        "apellido": u.apellido,
        "password": "",  # vacío (opcional actualizar)
        "activo": "SI" if u.activo else "NO",
        "rol": u.rol.value,
    }
    return render_template(
        "users/form.html", form=form, errors={}, mode="edit", uid=uid
    )


@users_bp.post("/<int:uid>/edit")
@admin_required
def update_user(uid: int):
    u = db.session.get(User, uid)
    if not u:
        abort(404)

    form = {
        "email": (request.form.get("email") or "").strip(),
        "nombre": (request.form.get("nombre") or "").strip(),
        "apellido": (request.form.get("apellido") or "").strip(),
        "password": request.form.get("password") or "",  # si viene vacío, no cambia
        "activo": (request.form.get("activo") or "").strip().upper(),
        "rol": (request.form.get("rol") or "").strip(),
    }

    ok, errors = validate_user_payload(form, is_update=True)
    if ok:
        # unicidad de email (excluyendo el propio registro)
        exists = db.session.execute(
            select(User).where(
                func.lower(User.email) == form["email"].lower(), User.id != uid
            )
        ).scalar_one_or_none()
        if exists:
            errors["email"] = "Ya existe otro usuario con ese email."

    if not ok or errors:
        return (
            render_template(
                "users/form.html", form=form, errors=errors, mode="edit", uid=uid
            ),
            400,
        )

    u.email = form["email"]
    u.nombre = form["nombre"]
    u.apellido = form["apellido"]
    if form["password"]:
        u.password_hash = generate_password_hash(form["password"])
    u.activo = form["activo"] == "SI"
    u.rol = UserRole(form["rol"])

    db.session.commit()
    flash("Usuario actualizado.", "success")
    return redirect(url_for("users.list_users"))


# --------- DELETE ----------
@users_bp.post("/<int:uid>/delete")
@admin_required
def delete_user(uid: int):
    u = db.session.get(User, uid)
    if not u:
        abort(404)
    db.session.delete(u)
    db.session.commit()
    flash("Usuario eliminado.", "success")
    return redirect(url_for("users.list_users"))
