from waitress import serve
from wsgi import app 

if __name__ == "__main__":
    print(f"Server is running at http://0.0.0.0:5001")
    serve(app, host="0.0.0.0", port=5001, threads=4)