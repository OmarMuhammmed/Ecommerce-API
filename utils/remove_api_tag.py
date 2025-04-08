def remove_api_tag(result, generator, request, public):
    for path, operations in result['paths'].items():
        for method in operations.values():
            if 'tags' in method and 'api' in method['tags']:
                method['tags'].remove('api')
            if 'tags' in method and not method['tags']:
                method['tags'] = ['Miscellaneous']  
    return result