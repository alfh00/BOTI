

class ApiSecrets:
    def __init__(self, ob):
        self.apiKey = ob['apiKey']
        self.secretKey= ob['secretKey']
        self.passphrase= ob['passphrase']

    def __repr__(self):
        return str(vars(self))
    
    @classmethod
    def settings_to_str(cls, settings):
        ret_str = 'Api Secrets:\n'
        for _, v in settings.items():
            ret_str += f'{v}\n'
        ret_str += '\n'

        return ret_str