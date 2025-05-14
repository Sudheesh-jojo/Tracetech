from django.shortcuts import render,HttpResponse,redirect,get_object_or_404
import requests
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
import imagehash

from .models import Lost,Found,MatchedItem
import cloudinary.uploader
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from Levenshtein import distance
import cv2
import numpy as np
from PIL import Image
from io import BytesIO


@login_required
def home(request):
    return render(request, 'reports/home.html')

def found_success(request):
    return render(request,"reports/success1.html")

def report_lostitem(request):
    if request.method == 'POST':
        item_name = request.POST.get('item_name')
        location = request.POST.get('location')
        category = request.POST.get('category')
        item_desc = request.POST.get('item_desc')
        image = request.FILES.get('image')
        date=request.POST.get('date')
        image_url=None
        if image:
            upload_result = cloudinary.uploader.upload(image)
            image_url = upload_result.get('secure_url')
        new_date = None
        try:
            new_date = datetime.strptime(date, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            error_message = "Invalid or missing date format."
            return render(request, 'reports/found.html', {'error_message': error_message})        


        if item_name and location and category and item_desc and new_date:
            lost_item=Lost.objects.create(
                item_name=item_name,
                user=request.user,
                location=location,
                category=category,
                item_desc=item_desc,
                image_url=image_url,
                date=new_date
            )
            
            print("Saved successfully!")
            return redirect('check_items',lost_item_id=lost_item.id)
        else:
            error_message = "Some fields are missing. Please fill in all the fields."
            return render(request, 'reports/lost.html', {'error_message': error_message})

    return render(request, 'reports/lost.html')


def general_report_found_item(request):
    if request.method == 'POST':
        item_name = request.POST.get('item_name')
        location = request.POST.get('location')
        category = request.POST.get('category')
        item_desc = request.POST.get('item_desc')
        image = request.FILES.get('image')
        date=request.POST.get('date')
        image_url=None
        if image:
            upload_result = cloudinary.uploader.upload(image)
            image_url = upload_result.get('secure_url')
        new_date = None
        try:
            new_date = datetime.strptime(date, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            error_message = "Invalid or missing date format."
            return render(request, 'reports/found.html', {'error_message': error_message})
        
        if item_name and location and category and item_desc and image_url and new_date:
            found_item=Found.objects.create (
                user=request.user,
                item_name=item_name,
                location=location,
                category=category,
                item_desc=item_desc,
                image_url=image_url,
                date=new_date
            )
            print("Saved successfully!")

            lost_items = Lost.objects.filter(category=found_item.category)
            for lost in lost_items:
                desc1 = found_item.item_desc.lower()
                desc2 = lost.item_desc.lower()
                similarity=comparedetails(desc1,desc2,found_item.image_url,lost.image_url)
                location_match = found_item.location.lower() == lost.location.lower()
                category_match = found_item.category.lower() == lost.category.lower()
                date_match = found_item.date==lost.date
                if similarity >=40 and (location_match or category_match or date_match):
                    user_email = lost.user.email  
                    if user_email:
                        send_mail(
                            'Found a similar item to your lost report',
                            f"Dear {lost.user.username},\n\nWe have found an item similar to the one you reported as lost. Please visit the admin office to check if it belongs to you.\n\nDetails of the found item:\nItem Name: {found_item.item_name}\nLocation: {found_item.location}\nCategory: {found_item.category}\nDescription: {found_item.item_desc}\nDate: {found_item.date}\nImage URL: {found_item.image_url}\n\nBest regards,\nLost and Found Team",
                            settings.EMAIL_HOST_USER, 
                            [user_email], 
                            fail_silently=False
                    )



            return render(request,'reports/success1.html')
        else:
            error_message = "Some fields are missing. Please fill in all the fields."
            return render(request, 'reports/found.html', {'error_message': error_message})

    return render(request, 'reports/found.html')
def colorhistogram(image_url):
    response=requests.get(image_url, timeout=5)
    img_pil = Image.open(BytesIO(response.content)).convert("RGB")
    img = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

    lost_img_resize=cv2.resize(img,(256,256))
    lost_img_rgb=cv2.cvtColor(lost_img_resize,cv2.COLOR_BGR2RGB)        
    hist_r=cv2.calcHist([lost_img_rgb],[0],None,[256],[0,256])
    hist_g=cv2.calcHist([lost_img_rgb],[1],None,[256],[0,256])
    hist_b=cv2.calcHist([lost_img_rgb],[2],None,[256],[0,256])        
    cv2.normalize(hist_r, hist_r)
    cv2.normalize(hist_g, hist_g)
    cv2.normalize(hist_b, hist_b)
    return hist_r,hist_g,hist_b
def image_hash_similarity(image_url1, image_url2):
    try:
        response1 = requests.get(image_url1, timeout=5)
        response2 = requests.get(image_url2, timeout=5)
        
        img1 = Image.open(BytesIO(response1.content)).convert('L').resize((256, 256))
        img2 = Image.open(BytesIO(response2.content)).convert('L').resize((256, 256))
        
        hash1 = imagehash.phash(img1)
        hash2 = imagehash.phash(img2)
        
        hash_diff = hash1 - hash2 
        max_bits = len(hash1.hash) ** 2  
        
        shape_similarity = (1 - (hash_diff / max_bits)) * 100  
        return shape_similarity
    except Exception as e:
        print(f"Hash comparison error: {e}")
        return 0
def check_items(request, lost_item_id,):
    selected_lost_item = Lost.objects.get(id=lost_item_id)
    matches = []
    
    found_items = Found.objects.filter(category=selected_lost_item.category)
    for found in found_items:
        desc1 = selected_lost_item.item_desc.lower()
        desc2 = found.item_desc.lower()
        similarity=comparedetails(desc1,desc2,selected_lost_item.image_url,found.image_url)
        location_match = selected_lost_item.location.lower() == found.location.lower()
        category_match = selected_lost_item.category.lower() == found.category.lower()
        date_match = selected_lost_item.date== found.date
        
        

        if similarity >=80 and (location_match or category_match or date_match):
            found.similarity=similarity
            matches.append(found)
    return render(request, 'reports/check.html', {
        'lost_item': selected_lost_item,
        'matches': matches
    })
def comparedetails(desc1,desc2,image_url1,image_url2):
    
    dis = distance(desc1, desc2)
    max_len = max(len(desc1), len(desc2))
    txt_similarity = (1 - dis / max_len) * 100  
    r1,g1,b1=colorhistogram(image_url1)
    r2,g2,b2=colorhistogram(image_url2)
    similarity_r = cv2.compareHist(r1,r2,cv2.HISTCMP_CORREL)
    similarity_g = cv2.compareHist(g1,g2,cv2.HISTCMP_CORREL)
    similarity_b = cv2.compareHist(b1,b2,cv2.HISTCMP_CORREL)
    
    img_similarity=((similarity_r+similarity_g+similarity_b)/3)
    img_similarity = (img_similarity + 1) * 50
    shape_similarity = image_hash_similarity(image_url1, image_url2)
    similarity = (0.3 * txt_similarity) + (0.4 * img_similarity) + (0.3 * shape_similarity)
    return similarity

def success2(request,lost_item_id,found_item_id):

    lost_item = Lost.objects.get(id=lost_item_id)
    found_item = Found.objects.get(id=found_item_id)
    matched_item = MatchedItem.objects.create(
        lost_item=lost_item,
        found_item=found_item,
        collected_by=request.user
    )

    return render(request, 'reports/success2.html')


    








