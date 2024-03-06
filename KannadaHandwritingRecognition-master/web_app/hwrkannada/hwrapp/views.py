from django.http import HttpResponse
from .models import DocumentImage
from django.template import loader
from .forms import DocumentForm
from django.shortcuts import render
from django.shortcuts import redirect
# from PIL import Image
from PIL import Image, ImageOps, ImageEnhance
import pytesseract
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

import html
# Import module here
import os
import sys
print(sys.path)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

rootdir = ""
segdir = ""
augdir = ""
enddir = ""
"""
    Index page. Lists last 6 images that were added to database. 
    Provides option to upload image, the transition between pages(from index to model_form_upload) 
    happens in html file through <a href> tag
"""


def index(request):
    if request.method == 'POST':
        return redirect('/hwrapp/upload/')
    latest_image_list = DocumentImage.objects.order_by('-pub_date')[:6]
    template = loader.get_template('hwrapp/index.html')
    print(latest_image_list)
    context = {
        'latest_image_list': latest_image_list,
    }
    return HttpResponse(template.render(context, request))


"""
    Shows the selected image.
    Provides a button to proceed to analysis of image
"""


def details(request, image_id):
    if request.method == 'POST':
        return redirect('/hwrapp/results/linesegments/' + str(image_id), {
            'image_id': image_id
        })

    template = loader.get_template('hwrapp/details.html')
    myobject = DocumentImage.objects.get(pk=image_id)
    print(myobject)
    context = {
        'myobject': myobject,
        'myobjectid': image_id
    }
    return HttpResponse(template.render(context, request))


"""
    A form to upload image from system.
"""


def model_form_upload(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            latest_image = DocumentImage.objects.order_by('-pub_date')[:1]
            for image in latest_image:
                print(image.image_id)
                # Use "/" before the path so that the given new path isnt concatenated with present path
                return redirect('/hwrapp/details/' + str(image.image_id), {
                    'image_id': image.image_id
                })

    # If form data wasnt valid, display empty form again to the user.
    else:
        form = DocumentForm()
    return render(request, 'hwrapp/model_form_upload.html', {
        'form': form
    })


"""
    Call for segmentation. Show line segmentation
"""


def linesegments(request, image_id):
    global rootdir, segdir, enddir
    template = loader.get_template('hwrapp/linesegments.html')
    myobject = DocumentImage.objects.get(pk=image_id)
    # Image path of selected image which is to be sent to module for processing
    image_path = myobject.image_url.url
    """
         Call script here for segmentation
    """
    image_path = os.path.join(
        'web_app/hwrkannada/hwrkannada', image_path[1:len(image_path)])

    path = os.path.join(os.path.dirname(__file__), '../../../')
    os.chdir(path)
    sys.path.insert(0, os.getcwd())
    from main import segmentation_call

    rootdir, segdir = segmentation_call(image_path)
    enddir = segdir.split('/images/')[1]
    imagelist = os.listdir(segdir+"/lines")
    imagelist.sort()
    context = {
        'image_id': image_id,
        'enddir': enddir,
        'imagelist': imagelist
    }
    return HttpResponse(template.render(context, request))


"""
    Show word segmentation
"""


def wordsegments(request, image_id):
    global segdir, enddir
    template = loader.get_template('hwrapp/wordsegments.html')
    imagelist = os.listdir(segdir+"/words")
    imagelist.sort()
    context = {
        'image_id': image_id,
        'enddir': enddir,
        'imagelist': imagelist
    }
    return HttpResponse(template.render(context, request))


"""
    Character and ottakshara segmentation
"""


def charsegments(request, image_id):
    global segdir, enddir
    template = loader.get_template('hwrapp/charsegments.html')
    imagelist = []
    for files in os.listdir(segdir):
        if os.path.isfile(os.path.join(segdir, files)):
            imagelist.append(files)
    imagelist.sort()
    print(imagelist)
    context = {
        'image_id': image_id,
        'enddir': enddir,
        'imagelist': imagelist
    }
    return HttpResponse(template.render(context, request))


"""
    Show Augmented characters and ottaksharas
"""


def augmentation(request, image_id):
    global rootdir, segdir, augdir
    template = loader.get_template('hwrapp/augmentation.html')
    myobject = DocumentImage.objects.get(pk=image_id)
    # Image path of selected image which is to be sent to module for processing
    image_path = myobject.image_url.url
    """
         Call script here for segmentation
    """
    image_path = os.path.join(
        'web_app/hwrkannada/hwrkannada', image_path[1:len(image_path)])

    path = os.path.join(os.path.dirname(__file__), '../../../')
    os.chdir(path)
    sys.path.insert(0, os.getcwd())
    from main import augmentation_call

    augdir = augmentation_call(image_path, segdir)
    enddir = augdir.split('/images/')[1]
    imagelist = os.listdir(augdir)
    imagelist.sort()
    context = {
        'image_id': image_id,
        'enddir': enddir,
        'imagelist': imagelist
    }
    return HttpResponse(template.render(context, request))


"""
    Result page. Needs to be updated to call our HWR module to analyse image
"""


def results(request, image_id):
    template = loader.get_template('hwrapp/results.html')

    from main import prediction_call

    output = prediction_call(augdir)
    # The output is parsed and results page is rendered to show the output
    h = html.parser.HTMLParser()
    h.unescape(output)
    myobject = DocumentImage.objects.get(pk=image_id)
    context = {
        'image_id': image_id,
        'myobject': myobject,
        'output': output
    }
    return HttpResponse(template.render(context, request))


def delete_image(request, image_id):
    image = DocumentImage.objects.get(pk=image_id).delete()
    return redirect('/hwrapp/')

# views.py
def download_text(request, image_id):
    # Define the relative path within the static directory
    images_relative_path = os.path.join('hwrapp', 'images', str(image_id), 'lines')

    # Construct the absolute path using BASE_DIR
    images_directory = os.path.join(settings.BASE_DIR, 'hwrkannada', 'hwrapp', 'static', images_relative_path)

    # Create directories if they don't exist
    os.makedirs(images_directory, exist_ok=True)

    # List to store extracted text from each image
    extracted_texts = []

    try:
        # Iterate through the images in the directory
        for image_file in os.listdir(images_directory):
            image_path = os.path.join(images_directory, image_file)

            # Print the image path (for debugging purposes)
            print(f"Processing image: {image_path}")

            # Use Pillow (PIL) to open and preprocess the image
            image = Image.open(image_path)
            image = preprocess_image(image)  # Implement your preprocessing function

            # Use pytesseract to extract text from the image
            extracted_text = pytesseract.image_to_string(image, lang='kan')  # 'kan' for Kannada language

            # Append the extracted text to the list
            extracted_texts.append(extracted_text)

    except Exception as e:
        logger.error(f"Error during OCR: {e}")
        return HttpResponse("Error during OCR")

    # Combine the extracted texts into a single string
    combined_text = '\n'.join(extracted_texts)

    # Change the file extension to .txt
    filename = 'kannada_text.txt'

    # Serve the content as a text file for download
    response = HttpResponse(combined_text, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename={filename}'

    # Include the extracted text in the response
    response['Extracted-Text'] = combined_text

    return response


def preprocess_image(image):
    # Resize the image to a standard size
    image = image.resize((800, 600))

    # Convert the image to grayscale
    image = ImageOps.grayscale(image)

    # Apply image enhancement techniques (optional)
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)  # Adjust contrast, you can customize the enhancement factor

    # Apply additional preprocessing steps as needed
    # Example: Image normalization, thresholding, denoising, etc.

    return image