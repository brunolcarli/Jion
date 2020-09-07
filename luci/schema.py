import logging
import graphene
from django.conf import settings
from luci.models import Emotion, Quote, User


class UserType(graphene.ObjectType):
    reference = graphene.String()
    name = graphene.String()
    friendshipness = graphene.Float()
    emotion_resume = graphene.Field('luci.schema.EmotionType')


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

    users = graphene.List(UserType)
    def resolve_users(self, info, **kwargs):
        return User.objects.all()

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

        user.save()

        return UpdateUser(user)


class Mutation:
    emotion_update = EmotionUpdate.Field()
    create_quote = CreateQuote.Field()
    update_user = UpdateUser.Field()
