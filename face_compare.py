import face_recognition

def get_face(img):
    img_face_encoding = face_recognition.face_encodings(img)[0]
    return img_face_encoding

def compare_face(face1_encoding, face2_encoding):
    known_face_encodings = [
        face1_encoding
    ]

    known_face_names = [
        'same'
    ]

    matches = face_recognition.compare_faces(known_face_encodings, face2_encoding)
    name = 'Unknown'
    if True in matches:
        first_match_index = matches.index(True)
        name = known_face_names[first_match_index]

    if name == 'same':
        return 'Same Image'
    else:
        return 'Different Image'

def compare_face_image(img1, img2):
    img1_face_encoding = face_recognition.face_encodings(img1)[0]

    known_face_encodings = [
        img1_face_encoding
    ]

    known_face_names = [
        'same'
    ]

    face_locations = face_recognition.face_locations(img2)
    face_encodings = face_recognition.face_encodings(img2, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = 'Unknown'
        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]

        if name == 'same':
            return 'Same Image'
        else:
            return 'Different Image'

def face_compare(img1, img2):
    img1_face_encoding = face_recognition.face_encodings(img1)[0]

    known_face_encodings = [
        img1_face_encoding
    ]

    known_face_names = [
        'same'
    ]

    face_locations = face_recognition.face_locations(img2)
    face_encodings = face_recognition.face_encodings(img2, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = 'Unknown'
        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]

        if name == 'same':
            return 'Same Image'
        else:
            return 'Different Image'