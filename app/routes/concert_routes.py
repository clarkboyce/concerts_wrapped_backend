# app/routes/concert_routes.py
from flask import Blueprint, request, jsonify
from app.services.concert_service import (
    get_concerts,
    delete_concert,
    create_concert
)

concert_bp = Blueprint("concert", __name__)

@concert_bp.route("/", methods=["GET"])
def get_all_concerts():
    artist = request.args.get("artist")
    city = request.args.get("city")
    state = request.args.get("state")
    date = request.args.get("date")
    return jsonify(get_concerts(artist, city, state, date))

@concert_bp.route("/<int:id>", methods=["DELETE"])
def delete_concert_view(id):
    return delete_concert(id)

@concert_bp.route("/", methods=["POST"])
def create_concert_view():
    data = request.get_json()
    return create_concert(data)