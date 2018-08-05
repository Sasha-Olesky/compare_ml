import cv2

def get_hist(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    hist = cv2.calcHist([img], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    cv2.normalize(hist, hist)
    return hist

def compare_hist(hist1, hist2):
    similar = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL) * 100
    if similar > 70:
        return 'Same Image'
    else:
        return 'Different Image'

def hist_compare(img1, img2):
    img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
    hist1 = cv2.calcHist([img1], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    cv2.normalize(hist1, hist1)

    img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
    hist2 = cv2.calcHist([img2], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    cv2.normalize(hist2, hist2)

    similar = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL) * 100
    if similar > 70:
        return ('Same Image', similar)
    else:
        return ('Different Image', similar)