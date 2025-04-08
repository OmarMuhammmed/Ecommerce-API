def exclude_schema_endpoints(result, generator, request, public):
    paths_to_exclude = ['/api/schema/', '/api/docs/']
    for path in paths_to_exclude:
        if path in result['paths']:
            del result['paths'][path]
    return result