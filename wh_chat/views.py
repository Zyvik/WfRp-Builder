from django.shortcuts import render, get_object_or_404
from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import GameModel, MessagesModel, MapModel, NPCModel
from .serializers import ChatSerializer, MapSerializer


class ChatView(APIView):
    msg_limit = 15
    authentication_classes = []

    def get_game(self, pk):
        try:
            game = get_object_or_404(GameModel, pk=pk)
        except GameModel.DoesNotExist:
            raise Http404
        return game

    def get(self, request, pk):
        game = self.get_game(pk)
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
        game = self.get_game(pk)
        tactical_map = MapModel.objects.get(game=game)
        serializer = MapSerializer(tactical_map, request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


def game_master_room(request, pk):
    game = get_object_or_404(GameModel, pk=pk)
    if request.user == game.admin:
        npc_list = NPCModel.objects.filter(game=game)
        if request.method == 'POST':
            # Adding NPC
            if request.POST.get('add_npc'):
                try:
                    npc = NPCModel(
                        game=game,
                        name=request.POST.get('npc_name', 'boring name'),
                        WW=int(request.POST.get('npc_WW', '0')),
                        US=int(request.POST.get('npc_US', '0')),
                        notes=request.POST.get('npc_notes')
                    )
                    npc.save()
                except ValueError:
                    pass

            # deleting NPC
            if request.POST.get('delete_npc'):
                npc_pk = int(request.POST.get('delete_npc'))
                npc = NPCModel.objects.get(pk=npc_pk)
                # checks if npc belongs to this game
                if npc.game == game:
                    npc.delete()

        context = {
            'game': game,
            'npcs': npc_list,
            'columns': range(7),
            'rows': range(10)
        }
        return render(request, 'warhammer/DMRoom.html', context)
    else:
        login_error = 'Nie jestesteś mistrzem tej gry - zawróć.'
        context = {
            'game': game,
            'login_error': login_error
        }
        return render(request, 'warhammer/DMRoom.html', context)
