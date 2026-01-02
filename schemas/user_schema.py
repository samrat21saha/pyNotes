def user_entity(user) -> dict:
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "created_at": user["created_at"]
    }
