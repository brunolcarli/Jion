import logging
import graphene
from django.conf import settings
from luci.models import Emotion, Quote


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


class Query(object):
    version = graphene.String()

    def resolve_version(self, info, **kwargs):
        return settings.VERSION

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
            emotion.__setattr__(key, current + value)
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


class Mutation:
    emotion_update = EmotionUpdate.Field()
    create_quote = CreateQuote.Field()
