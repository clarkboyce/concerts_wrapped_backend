from app import create_app

app = create_app()

if __name__ == "__main__":
    # Explicitly use port 8000 instead of 5000
    app.run(debug=True, host='0.0.0.0', port=8000)