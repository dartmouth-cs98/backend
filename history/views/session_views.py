from history.models import Session
from history.serializers import SessionSerializer, SessionSerializerNoPVs, ActiveSessionSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import datetime
import pytz

class CreateSession(APIView):

    def post(self, request, format=None):
        cu = request.user

        if cu.session_set.filter(active=True).exists():
            return Response({
                'status': 'Session Running',
                'message': 'There is already a session in process.'
            }, status=status.HTTP_400_BAD_REQUEST)

        title = request.data['title']

        if 'start' in request.data.keys():
            start = request.data['start']
            start = pytz.utc.localize(datetime.strptime(start, '%Y-%m-%dT%H:%M:%S.%fZ'))
        else:
            start = timezone.now()

        if 'end' in request.data.keys():
            end = request.data['end']
            end = pytz.utc.localize(datetime.strptime(end, '%Y-%m-%dT%H:%M:%S.%fZ'))
            session = Session(owned_by=cu, title=title, start=start, end=end)
        else:
            session = Session(owned_by=cu, title=title, start=start)

        session.save()

        sesh = SessionSerializerNoPVs(session)

        return Response(sesh.data)

class EndSession(APIView):

    def get(self, request, format=None):
        cu = request.user

        sessions = cu.session_set.all()

        try:
            session = sessions.get(active=True)
        except:
            raise Http404

        if not session.end or (session.end - timezone.now()).seconds > 60:
            session.end = timezone.now()

        session.active = False

        session.save()

        seshs = SessionSerializerNoPVs(sessions, many=True)

        return Response(seshs.data)

class DeleteSession(APIView):

    def post(self, request, format=None):
        cu = request.user

        pk = request.data['pk']

        try:
            session = cu.session_set.get(pk=pk)
        except Session.DoesNotExist:
            raise Http404

        session.delete()

        return Response()

class EditSession(APIView):

    def post(self, request, format=None):
        cu = request.user

        pk = request.data['pk']

        title = request.data['title']

        try:
            session = cu.session_set.get(pk=pk)
        except Session.DoesNotExist:
            raise Http404

        session.title = title

        session.save()

        sesh = SessionSerializerNoPVs(session)

        return Response(sesh.data)

class SendSessions(APIView):

    def get(self, request, format=None):
        cu = request.user

        sessions = cu.session_set.all()

        for s in sessions:
            setattr(s, 'pagevisits', s.pagevisit_set.all())

        seshs = SessionSerializer(sessions, many=True)

        return Response(seshs.data)

class SendActiveSession(APIView):

    def get(self, request, format=None):
        cu = request.user

        sessions = cu.session_set.all()

        curr_sesh = sessions.filter(active=True)

        if curr_sesh.exists():
            curr_sesh = curr_sesh.first()
            sessions = sessions.exclude(active=True)
        else:
            curr_sesh = None

        holder = {'active_session': curr_sesh, 'other_sessions': sessions}

        send = ActiveSessionSerializer(holder)

        return Response(send.data)
