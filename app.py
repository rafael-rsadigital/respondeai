from __future__ import annotations

import os
from flask import Flask, flash, redirect, render_template, request, url_for

import db
from reply_generator import generate_reply

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "mvp-local-secret-change-me")


def row_to_dict(row):
    return dict(row) if row else None


@app.before_request
def setup():
    db.init_db()
    db.seed_demo()


@app.get("/")
def index():
    status = request.args.get("status", "all")
    reviews = db.list_reviews(status)
    counts = {key: len(db.list_reviews(key)) for key in ("pending", "draft", "approved", "published")}
    return render_template("index.html", reviews=reviews, status=status, counts=counts)


@app.post("/reviews/<int:review_id>/generate")
def generate(review_id: int):
    review = db.get_review(review_id)
    if not review:
        flash("Avaliação não encontrada.", "error")
    else:
        reply = generate_reply(review["author"], review["rating"], review["text"])
        db.set_reply(review_id, reply)
        flash("Sugestão gerada. Revise antes de aprovar.", "success")
    return redirect(url_for("index"))


@app.post("/reviews/<int:review_id>/approve")
def approve(review_id: int):
    reply = request.form.get("reply", "").strip()
    if not reply:
        flash("A resposta não pode ficar vazia.", "error")
    else:
        db.approve(review_id, reply)
        flash("Resposta aprovada. A publicação ainda precisa ser comandada.", "success")
    return redirect(url_for("index"))


@app.post("/reviews/<int:review_id>/publish")
def publish(review_id: int):
    try:
        db.publish(review_id)
        # TODO: chamar GoogleBusinessAdapter.publish_reply antes de marcar como publicado.
        flash("Publicação registrada no MVP. Conecte o adaptador Google para publicar externamente.", "success")
    except ValueError as exc:
        flash(str(exc), "error")
    return redirect(url_for("index"))


@app.post("/api/reviews/import")
def import_reviews():
    payload = request.get_json(silent=True) or {}
    reviews = payload.get("reviews", [])
    if not isinstance(reviews, list):
        return {"error": "reviews deve ser uma lista"}, 400
    try:
        imported = db.upsert_reviews(reviews)
    except (KeyError, ValueError, TypeError) as exc:
        return {"error": f"formato inválido: {exc}"}, 400
    return {"imported": imported}, 201


@app.get("/api/reviews")
def api_reviews():
    return {"reviews": [row_to_dict(row) for row in db.list_reviews(request.args.get("status"))]}


if __name__ == "__main__":
    db.init_db()
    db.seed_demo()
    app.run(host="0.0.0.0", port=8000, debug=False)
