# utils.py
def add_accounts_tag(result, generator, request, public):
    for path, operations in result['paths'].items():
        if path.startswith('/api/accounts/'):
            for method in operations.values():
                method['tags'] = ['Accounts'] 
        elif path.startswith('/api/orders/'):
            for method in operations.values():
                method['tags'] = ['Orders']
        elif path.startswith('/api/payment/'):
            for method in operations.values():
                method['tags'] = ['Payment']
        elif path.startswith('/api/products/'):
            for method in operations.values():
                method['tags'] = ['Products']
    return result