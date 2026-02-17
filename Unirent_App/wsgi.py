from app import create_app

app = create_app()

if __name__ == '__main__':
    # Development server
    app.run(port=5001, debug=True)