


# chat/utils.py

def generate_private_room_name(user1_id, user2_id):
    return f"private_{min(user1_id, user2_id)}_{max(user1_id, user2_id)}"
