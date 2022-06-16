def device_context_processor(request):
    return {'is_mobile': request.user_agent.is_mobile or request.user_agent.is_tablet}
