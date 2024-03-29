from urllib.request import urlopen
from pyzbar import pyzbar
import cv2
import json

def appendInfo(file_name, text):
    with open(file_name, "a+") as file:
        file.seek(0)
        # If file is not empty then append '\n'
        information = file.read(100)
        if len(information) > 0:
            file.write("\n")
        file.write(text)

#This function would read the barcodes that are being shown via the webcam
def read_barcodes(image):
    barcodes = pyzbar.decode(image)
    for barcode in barcodes:
        if(len(barcodes) > 0):
            barcString = str(barcodes[0].data)[2:-1]
            #Make an API call to Open Food Facts
            url = "https://world.openfoodfacts.org/api/v0/product/" + barcString + ".json"
            #The text is retuned as json so we need to load it into python
            jsonUrl = urlopen(url)
            loadedJSON = json.loads(jsonUrl.read())
            if(not(loadedJSON["status"] == 0)):
                #Grab product title
                title = loadedJSON["product"]["product_name"]
                #Grab the product brand name
                brand = loadedJSON["product"]["brands_tags"]
                #Grab the nutrient levels of the product
                nutrients = (loadedJSON["product"]["nutrient_levels"])
                #Checks if there is nutrients before being displayed
                if(len(nutrients) > 0):
                    nutrientsList = ""
                    for nutrient, value in nutrients.items():
                        nutrientsList = nutrientsList + ", " + nutrient[0:] + " - " + value[0:]
                    nutrientsList = nutrientsList[1:]
                else:
                    nutrientsList = "Sorry! Nutrient levels not found"
            else:
                title = "Product not found"
                brand = "Brand not found"
                nutrientsList = "Nutrients not found"
        else:
            print("Item not found")

        #Gets the bounding box of the barcode
        (x, y , w, h) = barcode.rect
        barcode = barcode.data.decode('utf-8')
        information = "Barcode: {}, Title: {}, Brand: {}, Nutrients: {}".format(barcode, title, brand[0], nutrientsList)
        #draws a rectangle over the barcode 
        cv2.rectangle(image, (x, y),(x+w, y+h), (0, 255, 0), 2)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(image, barcode, (x + 6, y - 6), font, 0.5, (0, 0, 255), 1)
        cv2.imshow("Image", image)
        #Writes the barcode, title, brand and nutrient info on the text file
        appendInfo("results.txt", information)
    return image

def main():
    stream = cv2.VideoCapture(0)
    ret, frame = stream.read()
    while ret:
        ret, frame = stream.read()
        frame = read_barcodes(frame)
        cv2.imshow('Barcode reader', frame)
        key = cv2.waitKey(1) & 0xFF == 27
        if key == ord("q"):
            break

    #Cleanup
    stream.release()
    cv2.waitKey(1)
    cv2.destroyAllWindows()
    cv2.waitKey(1)

if __name__ == '__main__':
    main()
