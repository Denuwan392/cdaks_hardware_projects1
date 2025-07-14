from django.shortcuts import render, redirect
from .models import Transaction

# Fixed prices per kg
FRUIT_PRICES = {
    'banana': 150,
    'apple': 300,
}

def index(request):
    return render(request, 'billing/index.html')

def record_transaction(request):
    if request.method == 'POST':
        fruit_name = request.POST.get('fruit_name').lower()
        weight_str = request.POST.get('weight')
        
        try:
            weight = float(weight_str)
        except ValueError:
            return render(request, 'billing/error.html', {'message': 'Invalid weight entered.'})

        if fruit_name not in FRUIT_PRICES:
            return render(request, 'billing/error.html', {'message': 'Fruit not supported.'})
        
        price_per_kg = FRUIT_PRICES[fruit_name]
        weight_in_kg = weight / 1000
        total_price = weight_in_kg * price_per_kg

        transaction = Transaction.objects.create(
            fruit_name=fruit_name,
            weight=weight,
            price_per_kg=price_per_kg,
            total_price=total_price
        )

        return redirect('receipt', transaction_id=transaction.id)

    return render(request, 'billing/transaction_form.html')

def receipt(request, transaction_id):
    transaction = Transaction.objects.get(id=transaction_id)
    context = {
        'transaction': transaction
    }
    return render(request, 'billing/receipt.html', context)


def cashier(request):
    return render(request, 'billing/cashier.html')


from django.http import StreamingHttpResponse
import cv2
from ultralytics import YOLO

model = YOLO('/Users/denuwanwijesinghe/Documents/BSc. Artficial Intellligence/Hardware Project/Models/my_model/my_model.pt')  # Adjust path

# Open camera (adjust index if needed)
cap = cv2.VideoCapture(0)

def gen_frames():
    global latest_detected_fruit
    latest_detected_fruit = None

    while True:
        success, frame = cap.read()
        if not success:
            break

        results = model(frame)[0]
        annotated_frame = results.plot()

        boxes = results.boxes
        names = model.names

        if boxes:
            class_id = int(boxes.cls[0].item())  # First detection only
            latest_detected_fruit = names[class_id]
        else:
            latest_detected_fruit = None

        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')



def video_feed(request):
    return StreamingHttpResponse(gen_frames(), content_type='multipart/x-mixed-replace; boundary=frame')



from django.http import JsonResponse

def get_detected_fruit(request):
    global latest_detected_fruit
    return JsonResponse({'fruit': latest_detected_fruit or "None"})
    
from django.http import JsonResponse
from .models import Item

from .models import Item
from django.http import JsonResponse

def get_item_price(request):
    fruit_name = request.GET.get('fruit')
    if not fruit_name:
        return JsonResponse({'error': 'Missing fruit name'}, status=400)

    try:
        item = Item.objects.get(name__iexact=fruit_name)
        return JsonResponse({'price': item.price_per_kg})
    except Item.DoesNotExist:
        return JsonResponse({'error': 'Fruit not found'}, status=404)
    

    from .models import Item
from django.http import JsonResponse

def get_price(request):
    fruit_name = request.GET.get('fruit', '').strip().lower()

    try:
        item = Item.objects.get(name__iexact=fruit_name)
        return JsonResponse({'price': item.price_per_kg})
    except Item.DoesNotExist:
        return JsonResponse({'error': 'Fruit not found'}, status=404)



