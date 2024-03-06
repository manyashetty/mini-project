from pymongo import MongoClient
from bson import Binary
import os

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['images']
collection = db['img']

# Directory containing your images
images_directory = 'C:\mini-project\KannadaHandwritingRecognition-master\web_app\hwrkannada\hwrapp\static\hwrapp\images\Processed_we\Segmented_we\lines'

# Function to read and store images
def store_images(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            with open(os.path.join(directory, filename), 'rb') as image_file:
                image_data = Binary(image_file.read())
                document = {'filename': filename, 'image': image_data}
                collection.insert_one(document)

# Call the function with your images directory
store_images(images_directory)
