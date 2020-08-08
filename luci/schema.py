import logging
import graphene
from luci.models import Emotion

    
class EmotionType(graphene.ObjectType):
    reference = graphene.String()
    pleasantness = graphene.Float()
    attention = graphene.Float()
    sensitivity = graphene.Float()
    aptitude = graphene.Float()


class Query(object):
    foo = graphene.String()
    def resolve_foo(self, info, **kwargs):
        return 'Ok'

    emotions = graphene.List(
        EmotionType,
        reference=graphene.String(
            required=True,
            description='Filters by reference'
        )
    )

    def resolve_emotions(self, info, **kwargs):
        return Emotion.objects.filter(reference=kwargs['reference'])


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


class Mutation:
    emotion_update = EmotionUpdate.Field()
