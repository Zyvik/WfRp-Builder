from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import GameModel, MessagesModel, MapModel, NPCModel
from .forms import CreateNpcForm, RemoveNpcForm
from .serializers import ChatSerializer, MapSerializer


class ChatView(APIView):
    msg_limit = 15
    authentication_classes = []

    def get(self, request, pk):
        game = get_object_or_404(GameModel, pk=pk)
        messages = MessagesModel.objects.filter(game=game).order_by('-id')
        messages = messages[:self.msg_limit]
        tactical_map = MapModel.objects.get(game=game)

        serializer = ChatSerializer(messages, many=True)
        map_serializer = MapSerializer(tactical_map, many=False)
        return Response({
            'chat': serializer.data,
            'map': map_serializer.data
        })

    def post(self, request, pk):
        serializer = ChatSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        game = get_object_or_404(GameModel, pk=pk)
        tactical_map = MapModel.objects.get(game=game)
        serializer = MapSerializer(tactical_map, request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class GmRoomView(View):
    def get(self, request, pk):
        game = get_object_or_404(GameModel, pk=pk)
        npc_list = NPCModel.objects.filter(game=game)
        if request.user == game.admin:
            form = CreateNpcForm
            context = {
                'game': game,
                'form': form,
                'npc_list': npc_list,
                'columns': range(7),  # for tactical map
                'rows': range(10)
            }
            return render(request, 'wh_chat/DMRoom.html', context)
        login_error = 'Nie jestesteś mistrzem tej gry - zawróć.'
        return render(request, 'wh_chat/DMRoom.html', {'error': login_error})

    def post(self, request, pk):
        # Create NPC
        game = get_object_or_404(GameModel, pk=pk)
        form = CreateNpcForm(request.POST)
        if form.is_valid():
            npc = form.save(commit=False)
            npc.game = game
            npc.save()
            return redirect('wh-chat:gm_room', pk=pk)

        # Remove NPC
        npc_list = NPCModel.objects.filter(game=game)
        form = RemoveNpcForm(request.POST)
        if form.is_valid():
            npc_pk = form.cleaned_data['npc_pk']
            npc = get_object_or_404(npc_list, pk=npc_pk)
            npc.delete()
        return redirect('wh-chat:gm_room', pk=pk)

