from flask import Blueprint, request, jsonify
from app.services.user_concerts_service import (
    add_user_concert,
    get_all_user_concerts,
    delete_user_concert
)

user_concerts_bp = Blueprint("user_concerts", __name__)

@user_concerts_bp.route("/", methods=["POST"])
def add_user_to_concert():
    data = request.get_json()
    user_id = data.get("userId")
    concert_id = data.get("concertId")
    ticket_price = data.get("ticketPrice")

    return add_user_concert(user_id, concert_id, ticket_price,)

@user_concerts_bp.route("/", methods=["GET"])
def get_user_concerts():
    data = request.get_json()
    user_id = data.get("userId")
    if not user_id:
        return jsonify({"error": "userId is required"}), 400

    return jsonify(get_all_user_concerts(user_id))

@user_concerts_bp.route("/", methods=["DELETE"])
def delete_user_concert_view(): 
    data = request.get_json()
    user_id = data.get("userId")
    concert_id = data.get("concertId")

    return delete_user_concert(user_id, concert_id)