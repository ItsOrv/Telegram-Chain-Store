import consul

class ConsulClient:
    def __init__(self, host="localhost", port=8500):
        self.client = consul.Consul(host=host, port=port)

    def get_config(self, key):
        index, data = self.client.kv.get(key)
        if data:
            return data['Value'].decode('utf-8')
        return None

    def set_config(self, key, value):
        self.client.kv.put(key, value)

consul_client = ConsulClient()
