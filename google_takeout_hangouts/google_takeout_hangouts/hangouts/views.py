from django.shortcuts import render
from hangouts.models import hangout_reader


def conversations_list(request):
    context = {
        'conversations': hangout_reader.conversations,
    }
    return render(request, 'conversations-list.html', context)

def conversation(request, id):
    context = {
        'conversation': hangout_reader.conversation(id)
    }
    return render(request, 'conversation.html', context)
