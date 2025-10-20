def setup_db(app, db):
    with app.app_context():
        db.create_all() # Creates DB and tables if not present, can change to flask migrate later