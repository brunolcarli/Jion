from time import sleep
import logging
from base64 import b64decode
import graphene
from django.conf import settings
from luci.models import Emotion, Quote, User, Message, CustomConfig, Word
from luci.util import CompressedString
from web3 import Web3


class WordType(graphene.ObjectType):
    token = graphene.String()
    language = graphene.String()
    pos_tag = graphene.String()
    lemma = graphene.String()
    entity = graphene.String()
    polarity = graphene.Float()
    length = graphene.Int()


class CustomConfigType(graphene.ObjectType):
    reference = graphene.String()
    server_name = graphene.String()
    main_channel = graphene.String()
    allow_auto_send_messages = graphene.Boolean()
    filter_offensive_messages = graphene.Boolean()
    allow_learning_from_chat = graphene.Boolean()


class MessageType(graphene.ObjectType):
    reference = graphene.String()
    global_intention = graphene.String()
    specific_intention = graphene.String()
    text = graphene.String()
    message_datetime = graphene.DateTime()
    possible_responses = graphene.List(lambda: MessageType)
    author = graphene.String()

    def resolve_text(self, info, **kwargs):
        return CompressedString.decompress_bytes(self.text)

    def resolve_author(self, info, **kwargs):
        return self.user.name if self.user else None

    def resolve_possible_responses(self, info, **kwargs):
        return self.possible_responses.all().exclude(text__startswith='!').exclude(text__startswith='http').exclude(text__startswith=';;')


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

    def resolve_quote(self, info, **kwargs):
        return CompressedString.decompress_bytes(self.quote)


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
        reference=graphene.String(),
        text__startswith=graphene.String(),
        text__not_startswith=graphene.List(graphene.String),
        text__not_contains= graphene.List(graphene.String),
    )

    def resolve_messages(self, info, **kwargs):
        startswith_exclude = []
        if kwargs.get('text__not_startswith') is not None:
            startswith_exclude = kwargs.pop('text__not_startswith')

        contains_exclude = []
        if kwargs.get('text__not_contains') is not None:
            contains_exclude = kwargs.pop('text__not_contains')

        messages = Message.objects.filter(**kwargs)
        for constraint in startswith_exclude:
            messages = messages.exclude(text__istartswith=constraint)

        for constraint in contains_exclude:
            messages = messages.exclude(text__icontains=constraint)
        return messages

    custom_config = graphene.Field(
        CustomConfigType,
        reference=graphene.String(required=True)   
    )

    def resolve_custom_config(self, info, **kwargs):
        return CustomConfig.objects.get(reference=kwargs['reference'])

    words = graphene.List(
        WordType,
        token__icontains=graphene.String(),
        length=graphene.Int(),
        length__lte=graphene.Int(),
        length__gte=graphene.Int(),
        token__startswith=graphene.String(),
        token__endswith=graphene.String()
    )

    def resolve_words(self, info, **kwargs):
        return Word.objects.filter(**kwargs)


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
            quote=CompressedString(kwargs['quote']).bit_string,
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
        message = graphene.Argument(MessageInput, required=True)

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
                text=CompressedString(kwargs['message'].get('text')).bit_string,
                user=user,
                reference=kwargs['reference']
            )
            message.save()

        user.save()

        w3 = Web3(Web3.HTTPProvider('https://sepolia.infura.io/v3/c0e36045c28c479eb09b407479b1d493'))
        contract_address = w3.to_checksum_address(settings.CONTRACT_ADDRESS)
        contract = w3.eth.contract(address=contract_address, abi=settings.ABI)

        try:
            key = b64decode(user.reference.encode('utf-8')).decode('utf-8')
            _, uid = key.split(':')
            tx_meta = {
                'from': settings.ACCOUNT_ADDRESS,
                'nonce': w3.eth.get_transaction_count(settings.ACCOUNT_ADDRESS),
                'gas': 200000,
                'gasPrice': w3.to_wei('40', 'gwei')
            }
            transaction = contract.functions.update_member_msg_count(int(uid)).build_transaction(tx_meta)
            signed_txn = w3.eth.account.sign_transaction(transaction, settings.PRIVATE_KEY)
            transaction_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

            retries = 0
            while retries < settings.MAX_RETRIES:
                try:
                    transaction_receipt = w3.eth.get_transaction_receipt(transaction_hash)
                    break
                except:
                    sleep(1)
                    retries += 1

            result = contract.functions.update_member_msg_count(int(uid)).call()
            print("Result: ", result)
            print('Gas used', transaction_receipt.gasUsed)
            print('Transaction Hash: ', transaction_receipt.transactionHash)
        except Exception as ex:
            print('WEB3 ERROR: ')
            print(str(ex))

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
            text=CompressedString(kwargs['response']['text']).bit_string,
        )
        response.save()

        for message in messages:
            message.possible_responses.add(response)
            message.save()

        return AssignResponse(messages)


class UpdateCustomConfig(graphene.relay.ClientIDMutation):
    custom_config = graphene.Field(CustomConfigType)

    class Input:
        reference = graphene.String(required=True)
        server_name = graphene.String()
        main_channel = graphene.String()
        allow_auto_send_messages = graphene.Boolean()
        filter_offensive_messages = graphene.Boolean()
        allow_learning_from_chat = graphene.Boolean()

    def mutate_and_get_payload(self, info, **kwargs):
        custom_config, _ = CustomConfig.objects.get_or_create(
            reference=kwargs['reference']
        )
        allow_auto_send = kwargs.get('allow_auto_send_messages')
        filter_offensive_messages = kwargs.get('filter_offensive_messages')
        allow_learning_from_chat = kwargs.get('allow_learning_from_chat')

        if kwargs.get('server_name'):
            custom_config.server_name = kwargs['server_name']
        if kwargs.get('main_channel'):
            custom_config.main_channel = kwargs['main_channel']
        if allow_auto_send is True or allow_auto_send is False:
            custom_config.allow_auto_send_messages = allow_auto_send
        if allow_learning_from_chat is True or allow_learning_from_chat is False:
            custom_config.allow_learning_from_chat = allow_learning_from_chat
        if filter_offensive_messages is True or filter_offensive_messages is False:
            custom_config.filter_offensive_messages = filter_offensive_messages

        custom_config.save()
        return UpdateCustomConfig(custom_config)


class Mutation:
    emotion_update = EmotionUpdate.Field()
    create_quote = CreateQuote.Field()
    update_user = UpdateUser.Field()
    assign_response = AssignResponse.Field()
    update_custom_config = UpdateCustomConfig.Field()
