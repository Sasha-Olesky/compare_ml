from object_classfier import *

while True:
    print('Do you want to get image data? (y/n)')
    doGet = input()
    if doGet == 'y':
        print('Do you want to get image data? (y/n)')
        doGet = input()
        if doGet == 'y':
            print('Input Image URL.')
            imageURL = input()
            data, jsonfile, imagefile = getJsonData(imageURL)
            print(data)
        else:
            print('Input Image URL.')
            imageURL = input()
            data, jsonfile = getCropImage(imageURL)
    else:
        print('Do you want to compare images? (y/n)')
        doGet = input()
        if doGet == 'y':
            print('Input First Json File.')
            strFirstJson = input()
            print('Input Second Json File.')
            strSecondJson = input()
            result, jsonfile = image_compare_local(strFirstJson, strSecondJson)
            print(result)
        else:
            print('Input First Json File.')
            strFirstJson = input()
            print('Input Second Json File.')
            strSecondJson = input()
            result, jsonfile = image_similar_local(strFirstJson, strSecondJson)
            print(result)

    print('If exit program, please press "q".')
    print('If continue program, please press another key.')
    doQuit = input()
    if doQuit == 'q':
        break
