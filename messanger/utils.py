# chat/utils.py
import base64

def generate_private_room_name(user1_id, user2_id):
    room_name = f"private_{min(user1_id, user2_id)}_{max(user1_id, user2_id)}"
    # room_name_encoded = base64.urlsafe_b64encode(room_name.encode()).decode()
    return room_name

# def decode_private_room_name(encoded_room_name):
#     room_name = base64.urlsafe_b64decode(encoded_room_name.encode()).decode()
#     return room_name

# def extract_reciever_user_id(encoded_room_name,current_userid):
#     decoded_room_name = decode_private_room_name(encoded_room_name)
#     if decoded_room_name:
#         _,user1_id,user2_id = decoded_room_name.split("_")
#         return int(user1_id) if user1_id != current_userid else int(user2_id)
#     return None