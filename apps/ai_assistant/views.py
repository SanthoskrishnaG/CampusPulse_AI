import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .assistant import CampusAIAssistant

def assistant_page(request):
    """
    Campus AI Assistant interactive conversational chat interface.
    """
    return render(request, 'ai_assistant/chat.html')

@csrf_exempt
def assistant_query_api(request):
    """
    JSON API for real-time natural language query resolution.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.body else request.POST
            query = data.get('query', '').strip()
            if not query:
                return JsonResponse({'status': 'error', 'message': 'Empty query.'}, status=400)

            response = CampusAIAssistant.answer_query(query, request.user)
            return JsonResponse({'status': 'ok', 'query': query, 'response': response})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Method not allowed.'}, status=405)
