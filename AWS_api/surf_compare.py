import cv2

def get_feature(img):
    orb = cv2.ORB_create()
    kp, des = orb.detectAndCompute(img, None)
    return des

def compare_feature(des1, des2):
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)

    size = 0
    for m, n in matches:
        size = size + 1

    if size > 20:
        return 'Same Image'
    else:
        return 'Different Image'

def feature_compare(img1, img2):
    # Initiate ORB detector
    orb = cv2.ORB_create()
    # find the keypoints and descriptors with ORB
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)
    # create BFMatcher object
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    # Match descriptors.
    matches = bf.match(des1, des2)

    size = 0
    for m, n in matches:
        size = size + 1

    if size > 20:
        return 'Same Image'
    else:
        return 'Different Image'