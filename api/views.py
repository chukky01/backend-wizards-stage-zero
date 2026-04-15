import requests
from django.http import JsonResponse
from datetime import datetime

# Create your views here.
def classify_name(request):
    name = request.GET.get('name')

    #validate the name of the person
    if not name:
        return JsonResponse({"status": "error", "message": "Name parameter is required"}, status=400)

    if not isinstance(name, str):
        return JsonResponse({"status": "error", "message": "Name must be a string"}, status=422)

    try:
        #call the genderize API
        response = requests.get(
            "https://api.genderize.io",
            params={"name": name},
            timeout=3
        )

        if response.status_code !=200:
            return JsonResponse({"status": "error", "message": "Failed to fetch from external api"}, status=502)

        data = response.json()

        gender = data.get("gender")
        probability = data.get("probability")
        count = data.get("count")

        #Hendle the edge cases
        if gender is None or count == 0:
            return JsonResponse({"status": "error", "message": "No prediction available for the previous name"}, status=422)

        #process data
        sample_size = count
        is_confident = (probability >= 0.7) and (sample_size >= 100)

        processed_at = datetime.utcnow().replace(microsecond=0).isoformat() + "z"

        return JsonResponse({"status": "success", "data": {"name": name.lower(), "gender": gender, "probability": probability, "sample_size": sample_size, "is_confident": is_confident, "processed_at": processed_at}}, status=200)

    except requests.exceptions.RequestException:
        return JsonResponse({"status": "error", "message": "External API request failed"}, status=500)
