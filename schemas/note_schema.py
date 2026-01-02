def note_entity(note) -> dict:
    return {
        "id": str(note["_id"]),
        "title": note["title"],
        "desc": note["desc"],
        "important": note.get("important", False),
        "user_id": note.get("user_id"),
        "created_at": note["created_at"],
        "updated_at": note["updated_at"]
    }


def notes_entity(notes) -> list:
    return [note_entity(note) for note in notes]
