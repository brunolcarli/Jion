import logging
from base64 import b64decode
import graphene
from django.conf import settings
from luci.models import Emotion, Quote, User, Message


class MessageType(graphene.ObjectType):
    global_intention = graphene.String()
    specific_intention = graphene.String()
    text = graphene.String()
    message_datetime = graphene.DateTime()
    possible_responses = graphene.List(lambda: MessageType)
    author = graphene.String()

    def resolve_author(self, info, **kwargs):
        return self.user.name if self.user else None

    def resolve_possible_responses(self, info, **kwargs):
        return self.possible_responses.all()


class UserType(graphene.ObjectType):
    reference = graphene.String()
    name = graphene.String()
    friendshipness = graphene.Float()
    emotion_resume = graphene.Field('luci.schema.EmotionType')
    messages = graphene.List(MessageType)

    def resolve_messages(self, info, **kwargs):
        return self.message_set.all()

class EmotionType(graphene.ObjectType):
    reference = graphene.String()
    pleasantness = graphene.Float()
    attention = graphene.Float()
    sensitivity = graphene.Float()
    aptitude = graphene.Float()


class QuoteType(graphene.ObjectType):
    id = graphene.ID()
    reference = graphene.String()
    quote = graphene.String()
    author = graphene.String()
    date = graphene.Date()


class Query:
    version = graphene.String()

    def resolve_version(self, info, **kwargs):
        return settings.VERSION

    users = graphene.List(
        UserType,
        reference=graphene.String(
            description='Filters by reference'
        ),
        friendshipness__lte=graphene.Float(
            description='Affection level less or equal than inputed value'
        ),
        friendshipness__gte=graphene.Float(
            description='Affection level greather or equal than inputed value'
        ),
        user_id=graphene.String(),
        server_id=graphene.String(),
    )

    def resolve_users(self, info, **kwargs):
        user_id = kwargs.pop('user_id', None)
        server_id = kwargs.pop('server_id', None)
        users = User.objects.filter(**kwargs)

        if not user_id and not server_id:
            return users

        if user_id and not server_id:
            filtered = []
            for user in users:
                key = b64decode(user.reference.encode('utf-8')).decode('utf-8')
                _, uid = key.split(':')
                if user_id == uid:
                    filtered.append(user)
            return filtered

        if server_id and not user_id:
            filtered = []
            for user in users:
                key = b64decode(user.reference.encode('utf-8')).decode('utf-8')
                sid, _ = key.split(':')
                if server_id == sid:
                    filtered.append(user)
            return filtered
    
        if server_id and user_id:
            filtered = []
            for user in users:
                key = b64decode(user.reference.encode('utf-8')).decode('utf-8')
                sid, uid = key.split(':')
                if server_id == sid and user_id == uid:
                    filtered.append(user)
            return filtered

        return users

    emotions = graphene.List(
        EmotionType,
        reference=graphene.String(
            required=True,
            description='Filters by reference'
        )
    )

    def resolve_emotions(self, info, **kwargs):
        return Emotion.objects.filter(reference=kwargs['reference'])

    quotes = graphene.List(
        QuoteType,
        reference=graphene.String(required=True),
        author=graphene.String(),
        date=graphene.Date()
    )

    def resolve_quotes(self, info, **kwargs):
        return Quote.objects.filter(**kwargs)

    messages = graphene.List(
        MessageType,
        text__icontains=graphene.String(),
        text__contains=graphene.String(),
        global_intention=graphene.String(),
        specific_intention=graphene.String(),
        user__name=graphene.String(),
    )

    def resolve_messages(self, info, **kwargs):
        return Message.objects.filter(**kwargs)


class EmotionInputs(graphene.InputObjectType):
    pleasantness = graphene.Float()
    attention = graphene.Float()
    sensitivity = graphene.Float()
    aptitude = graphene.Float()


class EmotionUpdate(graphene.relay.ClientIDMutation):
    """
    Updates the emotion state by reference.
    """
    emotion = graphene.Field(EmotionType)

    class Input:
        reference = graphene.String(required=True)
        pleasantness = graphene.Float()
        attention = graphene.Float()
        sensitivity = graphene.Float()
        aptitude = graphene.Float()

    def mutate_and_get_payload(self, info, **kwargs):
        reference = kwargs.pop('reference')
        emotion, _ = Emotion.objects.get_or_create(reference=reference)

        # updates the emotion with inputed values
        for key, value in kwargs.items():
            current = emotion.__getattribute__(key)

            update = current + value
            if update > 9.99:
                update = 9.99

            elif update < -9.99:
                update = -9.99

            emotion.__setattr__(key, update)
        emotion.save()

        return EmotionUpdate(emotion)


class CreateQuote(graphene.relay.ClientIDMutation):
    quote = graphene.Field(QuoteType)

    class Input:
        quote = graphene.String(required=True)
        author = graphene.String(required=True)
        reference = graphene.String(required=True)

    def mutate_and_get_payload(self, info, **kwargs):
        quote = Quote.objects.create(
            quote=kwargs['quote'],
            author=kwargs['author'],
            reference=kwargs['reference']
        )
        quote.save()

        return CreateQuote(quote)


class MessageInput(graphene.InputObjectType):
    global_intention = graphene.String(required=True)
    specific_intention = graphene.String(required=True)
    text = graphene.String(required=True)


class UpdateUser(graphene.relay.ClientIDMutation):
    user = graphene.Field(UserType)

    class Input:
        reference = graphene.String(
            description='user reference',
            required=True
        )
        name = graphene.String(
            description='User name',
            required=True
        )
        friendshipness = graphene.Float(
            description='User affection level'
        )
        emotion_resume = graphene.Argument(
            EmotionInputs,
            description='User emotional data',
        )
        message = graphene.Argument(MessageInput)

    def mutate_and_get_payload(self, info, **kwargs):
        emotion_resume = kwargs.get('emotion_resume')
        friendshipness = kwargs.get('friendshipness', 0)

        user, created = User.objects.get_or_create(
            reference=kwargs['reference']
        )

        user.name = kwargs['name']
        user.friendshipness += friendshipness

        # se o usuário é novo precisamos criar seu relatório emocional
        if created:
            user_emotion = Emotion.objects.create(reference=kwargs['reference'])
            user.emotion_resume = user_emotion

        if emotion_resume:
            user.emotion_resume.pleasantness += emotion_resume.get('pleasantness', 0)
            user.emotion_resume.attention += emotion_resume.get('attention', 0)
            user.emotion_resume.sensitivity += emotion_resume.get('sensitivity', 0)
            user.emotion_resume.aptitude += emotion_resume.get('aptitude', 0)
            user.emotion_resume.save()

        if kwargs.get('message'):
            message = Message.objects.create(
                global_intention=kwargs['message'].get('global_intention', ''),
                specific_intention=kwargs['message'].get('specific_intention', ''),
                text=kwargs['message'].get('text'),
                user=user
            )
            message.save()

        user.save()

        return UpdateUser(user)


class AssignResponse(graphene.relay.ClientIDMutation):
    messages = graphene.List(MessageType).Field()

    class Input:
        text = graphene.String(required=True)
        response = graphene.Argument(
            MessageInput,    
            required=True
        )

    def mutate_and_get_payload(self, info, **kwargs):
        messages = Message.objects.filter(text__icontains=kwargs['text'])

        response = Message.objects.create(
            global_intention=kwargs['response'].get('global_intention', ''),
            specific_intention=kwargs['response'].get('specific_intention', ''),
            text=kwargs['response'].get('text'),
        )
        response.save()

        for message in messages:
            message.possible_responses.add(response)
            message.save()

        return AssignResponse(messages)


class Mutation:
    emotion_update = EmotionUpdate.Field()
    create_quote = CreateQuote.Field()
    update_user = UpdateUser.Field()
    assign_response = AssignResponse.Field()
