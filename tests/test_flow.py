import db
import pytest


def test_publish_requires_approval(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.sqlite3")
    db.init_db()
    db.upsert_reviews([{"external_id":"x", "author":"A", "rating":5, "text":"Ótimo", "reviewed_at":"2026-10-07"}])
    review = db.get_review(1)
    with pytest.raises(ValueError):
        db.publish(review["id"])


def test_approved_review_can_publish(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.sqlite3")
    db.init_db()
    db.upsert_reviews([{"external_id":"x", "author":"A", "rating":5, "text":"Ótimo", "reviewed_at":"2026-10-07"}])
    db.approve(1, "Obrigado!")
    db.publish(1)
    assert db.get_review(1)["status"] == "published"
