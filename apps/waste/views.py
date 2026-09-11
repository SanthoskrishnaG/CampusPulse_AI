from django.shortcuts import render, redirect
from django.contrib import messages
from .models import WasteRecord, WasteImagePrediction
from .classifier import WasteImageClassifier

def waste_dashboard(request):
    """
    Campus Waste & Sustainability Hub:
    Segregation stats, generation forecasts, and AI image classification scanner.
    """
    recent_records = WasteRecord.objects.all()[:14]
    recent_classifications = WasteImagePrediction.objects.all()[:8]

    # Campus totals
    total_recycled = sum(r.recyclable_kg for r in recent_records)
    total_waste = sum(r.total_kg() for r in recent_records)
    diversion_rate = round((total_recycled / max(total_waste, 1.0)) * 100.0, 1)

    return render(request, 'waste/dashboard.html', {
        'recent_records': recent_records,
        'recent_classifications': recent_classifications,
        'total_recycled': round(total_recycled, 1),
        'total_waste': round(total_waste, 1),
        'diversion_rate': diversion_rate,
    })

def classify_waste_image(request):
    """
    Accepts an uploaded image of a waste item, runs 6-class TrashNet classification,
    and returns immediate disposal guidance.
    """
    if request.method == 'POST' and request.FILES.get('image'):
        img = request.FILES['image']
        pred = WasteImagePrediction.objects.create(image=img)

        result = WasteImageClassifier.classify_image(pred.image.path)
        pred.predicted_class = result['predicted_class']
        pred.confidence = result['confidence']
        pred.disposal_recommendation = result['disposal_advice']
        pred.save()

        messages.success(
            request,
            f"Classified as '{pred.get_predicted_class_display()}' ({pred.confidence*100:.0f}% confidence). {pred.disposal_recommendation}"
        )
        return redirect('waste:dashboard')

    return redirect('waste:dashboard')
