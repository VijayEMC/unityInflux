import requests
import json


requests.packages.urllib3.disable_warnings()


class Unity:

    def __init__(self, params):
        self.hostname = params['unity_hostname']
        self.username = params['unity_username']
        self.password = params['unity_password']
        # Base URL of the REST API
        self.apibase = 'https://' + self.hostname
        # HTTP headers for REST API requests, less the 'EMC-CSRF-TOKEN' header
        self.headers = {
                'X-EMC-REST-CLIENT': 'true',
                'content-type': 'application/json',
                'Accept': 'application/json',
                'verify': 'False'
                }
        self.session = requests.Session()
        self.updateResults = []

    def _getMsg(self, resp):
        try:
            msg = json.loads(resp.text)
        except ValueError:
            msg = {'httpStatusCode': resp.status_code, 'messages': [{
                'en-US': resp.text}]}
        return msg

    def _getResult(self, resp, **kwargs):
        if resp.status_code // 100 == 2:    # HTTP status code 2xx = success
            return resp

        self.err = self._getMsg(resp)
        self.err.update({'url': resp.url})
        # Unauthorized password
        if resp.status_code == 401 and kwargs.get('auth'):
            self.err['messages'][0]['en-US'] = "Authentication error for User '" + kwargs['auth'].username + "'"      # Update error message
        self.exitFail()

    def _doGet(self, url, params=None, **kwargs):
        
        if kwargs == {}:
            kwargs = {}
            kwargs.update({'headers' : self.headers, 'verify': False})
            return self.session.get(self.apibase + url)
            
        
        kwargs.update({'headers' : self.headers, 'verify': False})
        resp = self.session.get(self.apibase + url, params=params, **kwargs)
        return self._getResult(resp, **kwargs)

    def _changeResult(
            self,
            resp,
            url,
            args=None,
            changed=True,
            httpMethod='POST',
            **kwargs):
        if resp:
            url = resp.url
        elif 'params' in kwargs:    # Reconstruct URL with parameters
            url += '?'
            for key, value in kwargs['params'].items():
                url += key + '=' + value + '&'
            url = url.strip('?&')
        if resp and resp.status_code // 100 == 2:
            if changed:
                self.changed = changed
                changeContent = {'HTTP_method': httpMethod}
                changeContent['url'] = url
                if args is not None:
                    changeContent['args'] = args
                if resp and resp.text:
                    changeContent['response'] = json.loads(resp.text)
                self.updateResults.append(changeContent)
        else:
            self.err = self._getMsg(resp)
            self.err['url'] = resp.url
            if args is not None:
                self.err['args'] = args
            self.exitFail()

    def _doPost(self, url, args, changed=True, **kwargs):
        #if self.checkMode:
         #   resp = None
        #else:
        if kwargs is None:
            kwargs = {}
        kwargs.update({'headers': self.headers})
        resp = self.session.post(self.apibase + url, json=args, **kwargs)
        self._changeResult(resp, url, args, changed=changed, **kwargs)

    def _doDelete(self, url, **kwargs):
  #      if self.checkMode:
   #         resp = None
    #    else:
        if kwargs is None:
            kwargs = {}
        kwargs.update({'headers': self.headers, 'verify': False})
        resp = self.session.delete(self.apibase + url, **kwargs)
        self._changeResult(resp, url, httpMethod='DELETE', **kwargs)

    def startSession(self):
        url = '/api/instances/system/0'
        auth = requests.auth.HTTPBasicAuth(self.username, self.password)
        resp = self._doGet(url, auth=auth)
        # Add 'EMC-CSRF-TOKEN' header
        self.headers['EMC-CSRF-TOKEN'] = resp.headers['EMC-CSRF-TOKEN']

    def basicInfo(self):
        url = '/api/types/basicSystemInfo/instances'
        resp = self._doGet(url)
        return resp.json()['entries'][0]['content']
    
    def unityPost(self, url, kwargs):
        return self.session.post(url, kwargs, headers=self.headers)