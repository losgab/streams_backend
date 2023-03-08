import pytest
import requests
import os
from urllib.request import urlretrieve

from PIL import Image
from src.error import InputError
from src import config

# Fixture that clears the data store 
@pytest.fixture
def clear():
    requests.delete(config.url + 'clear/v1')

# Fixture that registers 3 users. returns their tokens and u_ids
@pytest.fixture
def user_setup():
    user_0_json = requests.post(config.url + 'auth/register/v2', json={'email': 'gabriel@domain.com', 'password': 'password', 'name_first': 'gabriel', 'name_last': 'thien'})
    return {
        'user0_token': user_0_json.json()['token'],
        'user0_id': user_0_json.json()['auth_user_id'],
    }

# Tests giving a broken URL
def test_broken_url(clear, user_setup):
    # Give server an invalid URL
    img_url = "http://www.akjsdhfjkasdhfljkhsdfl.com/"
    resp_data = requests.post(config.url + "user/profile/uploadphoto/v1", json={
        'token': user_setup['user0_token'],
        'img_url': img_url,
        'x_start': -1,
        'y_start': -1,
        'x_end': -1,
        'y_end': -1,
    })
    # Expecting a InputError for Invalid URL
    assert resp_data.status_code == InputError.code

# Tests giving a 404 URL that should pose some issues 
def test_404_url(clear, user_setup):
    # Give server a 404 url
    img_url = "http://www.redbackracing.com/"
    resp_data = requests.post(config.url + "user/profile/uploadphoto/v1", json={
        'token': user_setup['user0_token'],
        'img_url': img_url,
        'x_start': -1,
        'y_start': -1,
        'x_end': -1,
        'y_end': -1,
    })
    # Expecting a InputError for invalid url
    assert resp_data.status_code == InputError.code

# Tests giving a non image URL such as a webpage
def test_non_image_url(clear, user_setup):
    # Give server a non image URL
    img_url = "https://www.switchkeys.com.au/"
    resp_data = requests.post(config.url + "user/profile/uploadphoto/v1", json={
        'token': user_setup['user0_token'],
        'img_url': img_url,
        'x_start': -1,
        'y_start': -1,
        'x_end': -1,
        'y_end': -1,
    })
    # Expecting a InputError for invalid URL
    assert resp_data.status_code == InputError.code

# Tests when given a URL to a non jpg image
def test_non_jpg_image(clear, user_setup):
    # Give server a non jpg image URL
    img_url = "http://www.sushihub.com.au/wp-content/uploads/2021/04/Sushi-Hub_Mini-Roll-sushi-box_Slider.png"
    resp_data = requests.post(config.url + "user/profile/uploadphoto/v1", json={
        'token': user_setup['user0_token'],
        'img_url': img_url,
        'x_start': -1,
        'y_start': -1,
        'x_end': -1,
        'y_end': -1,
    })
    # Expecting a InputError for Error retrieving image
    assert resp_data.status_code == InputError.code

# Tests when x_end <= x_start or y_end <= y_start
def test_invalid_end_values(clear, user_setup):
    # Give server a valid image URL
    img_url = "http://www.4ingredients.com.au/wp-content/uploads/2018/07/4I-Sushi-sml.jpg"
    resp_data = requests.post(config.url + "user/profile/uploadphoto/v1", json={
        'token': user_setup['user0_token'],
        'img_url': img_url,
        'x_start': 0,
        'y_start': 0,
        'x_end': -1,
        'y_end': -1,
    })
    # Expecting a InputError for bad end values
    assert resp_data.status_code == InputError.code

# Tests when any of crop values are outside of image dimensions
def test_invalid_xcrop_values(clear, user_setup):
    # Give server a valid image URL
    img_url = "http://www.4ingredients.com.au/wp-content/uploads/2018/07/4I-Sushi-sml.jpg"
    # Downloads the image into server-side folder, loads into a python object
    urlretrieve(img_url, "src/img0.jpg")
    imageObject = Image.open("src/img0.jpg")
    width, height = imageObject.size
    resp_data = requests.post(config.url + "user/profile/uploadphoto/v1", json={
        'token': user_setup['user0_token'],
        'img_url': img_url,
        'x_start': -1,
        'y_start': 0,
        'x_end': width + 10,
        'y_end': height-10,
    })
    # Expecting a InputError for bad crop values
    assert resp_data.status_code == InputError.code
    # Close Image object and remove the temporary file 
    imageObject.close()
    os.remove("src/img0.jpg")

# Tests when any of crop values are outside of image dimensions
def test_invalid_7crop_values(clear, user_setup):
    # Give server a valid image URL
    img_url = "http://www.4ingredients.com.au/wp-content/uploads/2018/07/4I-Sushi-sml.jpg"
    # Downloads the image into server-side folder, loads into a python object
    urlretrieve(img_url, "src/img0.jpg")
    imageObject = Image.open("src/img0.jpg")
    width, height = imageObject.size
    resp_data = requests.post(config.url + "user/profile/uploadphoto/v1", json={
        'token': user_setup['user0_token'],
        'img_url': img_url,
        'x_start': 0,
        'y_start': -1,
        'x_end': width-10,
        'y_end': height + 10,
    })
    # Expecting a InputError for bad crop values
    assert resp_data.status_code == InputError.code
    # Close Image object and remove the temporary file 
    imageObject.close()
    os.remove("src/img0.jpg")
    
# Tests success case 
def test_success_cropped_photo_upload(clear, user_setup):
    # Give server a valid image URL
    img_url = "http://www.4ingredients.com.au/wp-content/uploads/2018/07/4I-Sushi-sml.jpg"
    # Downloads the image into server-side folder, loads into a python object and crops
    urlretrieve(img_url, "src/img0.jpg")
    originalImage = Image.open("src/img0.jpg")
    originalImage = originalImage.crop((0, 0, 400, 400))
    originalImage.save("src/img0.jpg")
    originalImage = Image.open("src/img0.jpg")
    # Get server to do the cropping and upload
    resp_data = requests.post(config.url + "user/profile/uploadphoto/v1", json={
        'token': user_setup['user0_token'],
        'img_url': img_url,
        'x_start': 0,
        'y_start': 0,
        'x_end': 400,
        'y_end': 400,
    })
    assert resp_data.status_code == 200
    assert resp_data.json() == {}
    check_data = requests.get(config.url + "user/profile/v1", params={'token': user_setup['user0_token'], 'u_id': user_setup['user0_id']})
    # Expecting server response should be the cropped originalImage
    server_returned_photo_url = check_data.json()['user']['profile_img_url']
    urlretrieve(server_returned_photo_url, "src/server_returned.jpg")
    serverImage = Image.open("src/server_returned.jpg")
    # Cropped image should be same as the server cropped image
    assert originalImage == serverImage
    # Close stuff and remove stuff
    originalImage.close()
    serverImage.close()
    os.remove("src/img0.jpg")
    os.remove("src/server_returned.jpg")