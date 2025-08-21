from fitness_app import create_app, db

app = create_app()

LOCAL = False 

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    if LOCAL:
        app.run(debug=True)
    else:
        app.run(host='0.0.0.0', port=5000, debug=True)