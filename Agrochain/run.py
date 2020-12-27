from flaskapp import app,db

app.run(host='127.0.0.1', port=5000, debug=True)
db.create_all()