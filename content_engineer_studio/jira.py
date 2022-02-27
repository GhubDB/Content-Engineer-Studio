from jira import JIRA
import requests

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequest)

class JiraException(Exception):
    pass

class Jira(object):
    __options = {
        'server' : '<protocols>://<your.company.com>',
        'verify' : False
    }
    
    __client = None
    
    def __init__(self, **kwargs):
        if len(kwargs) != 2:
            raise JiraException('Username and password needed')
        
        if 'username' in kwargs.keys():
            self.__username = kwargs['username']
        else:
            raise JiraException('Username needed.')
        if 'password' in kwargs.keys():
            self.__password = kwargs['password']
        else:
            raise JiraException('Password needed.')
        
        try:
            self.__client = JIRA(self.__options, basic_auth=(self.__username, self.__password))
        except:
            raise JiraException('Could not connect to the API, invalid username or password') from None
        
    def __str__(self):
        return 'Jira(username = {}, password = {}, endpoint = {}'.format(self.__username, self.__password, self.__options)
    def __repr__(self):
        return 'Jira(username = {}, password = {}, endpoint = {}'.format(self.__username, self.__password, self.__options)
    def __format__(self):
        return 'Jira(username = {}, password = {}, endpoint = {}'.format(self.__username, self.__password, self.__options)