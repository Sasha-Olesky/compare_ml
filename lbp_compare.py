
import cv2
import numpy as np
from skimage import feature
from sklearn.svm import LinearSVC

orb = cv2.ORB_create()
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

def compare_image(first, second):
    kp1, des1 = orb.detectAndCompute(first, None)
    kp2, des2 = orb.detectAndCompute(second, None)
    try:
        matches = bf.match(des1, des2)
        match_size = matches.__len__()
    except:
        match_size = 0

    if match_size > 200:
        return 'Same Image'
    else:
        return 'Different Image'

class LocalBinaryPatterns:
    def __init__(self, numPoints, radius):
        # store the number of points and radius
        self.numPoints = numPoints
        self.radius = radius

    def describe(self, image, eps=1e-7):
        # compute the Local Binary Pattern representation
        # of the image, and then use the LBP representation
        # to build the histogram of patterns
        lbp = feature.local_binary_pattern(image, self.numPoints,
                                           self.radius, method="uniform")
        (hist, _) = np.histogram(lbp.ravel(),
                                 bins=np.arange(0, self.numPoints + 3),
                                 range=(0, self.numPoints + 2))

        # normalize the histogram
        hist = hist.astype("float")
        hist /= (hist.sum() + eps)

        # return the histogram of Local Binary Patterns
        return hist

def get_lbp(img):
    desc = LocalBinaryPatterns(24, 8)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hist = desc.describe(gray)
    return hist

def compare_lbp(img1, img2):
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    feature.local_binary_pattern(gray1, 10, 5, method="default")  # method="uniform")

    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    feature.local_binary_pattern(gray2, 10, 5, method="default")  # method="uniform")

    return compare_image(gray1, gray2)

def compare_lbps(img1, img2):
    # initialize the local binary patterns descriptor along with
    # the data and label lists
    desc = LocalBinaryPatterns(24, 8)
    data = []
    labels = []

    # convert it to grayscale, and describe it
    gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    hist = desc.describe(gray)

    # extract the label from the image, then update the
    # label and data lists
    labels.append('first')
    data.append(hist)

    horizontal_img = cv2.flip(img1, 0)
    gray = cv2.cvtColor(horizontal_img, cv2.COLOR_BGR2GRAY)
    hist = desc.describe(gray)
    labels.append('first')
    data.append(hist)

    vertical_img = cv2.flip(img1, 1)
    gray = cv2.cvtColor(vertical_img, cv2.COLOR_BGR2GRAY)
    hist = desc.describe(gray)
    labels.append('first')
    data.append(hist)

    vertical_img = cv2.flip(img1, 1)
    gray = cv2.cvtColor(vertical_img, cv2.COLOR_BGR2GRAY)
    hist = desc.describe(gray)
    labels.append('second')
    data.append(hist)

    # train a Linear SVM on the data
    model = LinearSVC(C=100.0, random_state=42)
    model.fit(data, labels)

    gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    hist = desc.describe(gray)
    prediction = model.decision_function(hist.reshape(1, -1))
    if prediction[0] == 'first':
        return 'Same Image'
    else:
        return 'Different Image'
