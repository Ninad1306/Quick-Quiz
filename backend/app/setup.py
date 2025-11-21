def setup_db(app, db):
    with app.app_context():
        db.create_all()
