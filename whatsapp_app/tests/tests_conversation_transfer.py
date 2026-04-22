# -*- coding: utf-8 -*-

from django.test import TestCase
from django.utils import timezone

from ominicontacto_app.models import Campana
from ominicontacto_app.tests.factories import AgenteProfileFactory, CampanaFactory, UserFactory
from whatsapp_app.api.v1.conversacion import ConversacionSerializer
from whatsapp_app.api.v1.transfer import ViewSet as TransferViewSet
from whatsapp_app.models import ConfiguracionWhatsappCampana, MensajeWhatsapp
from whatsapp_app.tests.factories import ConversacionFactory, LineaFactory


class ConversationTransferEventTest(TestCase):

    def _set_active_whatsapp_campaign(self, campaign):
        campaign.estado = Campana.ESTADO_ACTIVA
        campaign.whatsapp_habilitado = True
        campaign.save(update_fields=['estado', 'whatsapp_habilitado'])
        return campaign

    def _create_campaign_config(self, campaign, line, user):
        return ConfiguracionWhatsappCampana.objects.create(
            campana=campaign,
            linea=line,
            nivel_servicio=1,
            created_by=user,
            updated_by=user,
        )

    def _create_message(
            self, conversation, timestamp, sender, content,
            origin=None, message_type='text'):
        return MensajeWhatsapp.objects.create(
            message_id='message-{}-{}'.format(conversation.id, timestamp.timestamp()),
            conversation=conversation,
            origen=origin or conversation.line.numero,
            timestamp=timestamp,
            sender=sender,
            content=content,
            type=message_type,
            status='read',
            fail_reason='',
        )

    def test_report_detail_uses_transfer_event_messages_to_build_transfer_metadata(self):
        current_campaign = self._set_active_whatsapp_campaign(CampanaFactory())
        target_campaign = self._set_active_whatsapp_campaign(CampanaFactory())
        initial_agent = AgenteProfileFactory()
        transferred_agent = AgenteProfileFactory()
        line = LineaFactory(numero='5493511111111')
        base_time = timezone.now().astimezone(timezone.get_current_timezone())
        conversation = ConversacionFactory(
            line=line,
            campana=current_campaign,
            agent=initial_agent,
            destination='5493519999999',
            timestamp=base_time,
            date_last_interaction=base_time,
            is_active=True,
        )

        self._create_message(
            conversation=conversation,
            timestamp=base_time,
            sender={'name': initial_agent.user.username, 'agent_id': initial_agent.user_id},
            content={'text': 'Hola desde el agente inicial'},
        )
        self._create_message(
            conversation=conversation,
            timestamp=base_time + timezone.timedelta(seconds=1),
            sender={
                'name': initial_agent.user.username,
                'agent_id': initial_agent.user_id,
                'internal': True,
            },
            content={
                'event_type': 'agent_transfer',
                'by_agent': {
                    'id': initial_agent.user_id,
                    'username': initial_agent.user.username,
                    'name': initial_agent.user.username,
                },
                'from_agent': {
                    'id': initial_agent.user_id,
                    'username': initial_agent.user.username,
                    'name': initial_agent.user.username,
                },
                'to_agent': {
                    'id': transferred_agent.user_id,
                    'username': transferred_agent.user.username,
                    'name': transferred_agent.user.username,
                },
                'from_campaign': {'id': current_campaign.id, 'name': current_campaign.nombre},
            },
            origin='system',
            message_type='transfer_event',
        )
        conversation.agent = transferred_agent
        conversation.save(update_fields=['agent'])
        self._create_message(
            conversation=conversation,
            timestamp=base_time + timezone.timedelta(seconds=2),
            sender={'name': transferred_agent.user.username, 'agent_id': transferred_agent.user_id},
            content={'text': 'Hola desde el agente transferido'},
        )
        self._create_message(
            conversation=conversation,
            timestamp=base_time + timezone.timedelta(seconds=3),
            sender={
                'name': transferred_agent.user.username,
                'agent_id': transferred_agent.user_id,
                'internal': True,
            },
            content={
                'event_type': 'campaign_transfer',
                'by_agent': {
                    'id': transferred_agent.user_id,
                    'username': transferred_agent.user.username,
                    'name': transferred_agent.user.username,
                },
                'from_agent': {
                    'id': transferred_agent.user_id,
                    'username': transferred_agent.user.username,
                    'name': transferred_agent.user.username,
                },
                'to_campaign': {'id': target_campaign.id, 'name': target_campaign.nombre},
                'from_campaign': {'id': current_campaign.id, 'name': current_campaign.nombre},
            },
            origin='system',
            message_type='transfer_event',
        )
        conversation.campana = target_campaign
        conversation.agent = None
        conversation.save(update_fields=['campana', 'agent'])

        data = ConversacionSerializer(conversation).data

        self.assertEqual(data['message_number'], 4)
        self.assertEqual(data['initial_agent']['username'], initial_agent.user.username)
        self.assertEqual(data['transferred_agent']['username'], transferred_agent.user.username)
        self.assertEqual(data['transferred_campaign']['name'], target_campaign.nombre)
        self.assertEqual(
            [message['type'] for message in data['messages']],
            ['text', 'transfer_event', 'text', 'transfer_event']
        )

    def test_eligible_campaigns_are_filtered_by_same_whatsapp_line_for_inbound_and_outbound(self):
        user = UserFactory()
        current_campaign = self._set_active_whatsapp_campaign(CampanaFactory())
        eligible_campaign = self._set_active_whatsapp_campaign(CampanaFactory())
        second_eligible_campaign = self._set_active_whatsapp_campaign(CampanaFactory())
        other_line_campaign = self._set_active_whatsapp_campaign(CampanaFactory())
        disabled_campaign = CampanaFactory()
        disabled_campaign.estado = Campana.ESTADO_ACTIVA
        disabled_campaign.whatsapp_habilitado = False
        disabled_campaign.save(update_fields=['estado', 'whatsapp_habilitado'])
        line = LineaFactory()
        other_line = LineaFactory()

        self._create_campaign_config(current_campaign, line, user)
        self._create_campaign_config(eligible_campaign, line, user)
        self._create_campaign_config(second_eligible_campaign, line, user)
        self._create_campaign_config(other_line_campaign, other_line, user)
        self._create_campaign_config(disabled_campaign, line, user)

        inbound_conversation = ConversacionFactory(
            line=line,
            campana=current_campaign,
            destination='111',
            saliente=False,
        )
        outbound_conversation = ConversacionFactory(
            line=line,
            campana=current_campaign,
            destination='222',
            saliente=True,
        )
        viewset = TransferViewSet()

        expected_ids = {eligible_campaign.id, second_eligible_campaign.id}
        inbound_ids = set(viewset._eligible_campaigns_for_conversation(
            inbound_conversation).values_list('id', flat=True))
        outbound_ids = set(viewset._eligible_campaigns_for_conversation(
            outbound_conversation).values_list('id', flat=True))

        self.assertSetEqual(inbound_ids, expected_ids)
        self.assertSetEqual(outbound_ids, expected_ids)
