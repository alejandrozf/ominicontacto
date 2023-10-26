from notification_app.notification import AgentNotifier
an = AgentNotifier()


async def send_notify(notify_type, **kwargs):
    try:
        print("notify_type >>>>", notify_type, kwargs)
        notify = getattr(an, notify_type)
        agents = []
        if kwargs.get('conversation', None):
            if kwargs['conversation'].agent:
                agents.append(kwargs['conversation'].agent)
            elif kwargs['conversation'].campana:
                agents = kwargs['conversation'].campana.obtener_agentes()
            print(agents)
            for agent in agents:
                await notify(agent.user_id, **kwargs)
    except Exception as e:
        print('error en send_notify >>>>', e)
