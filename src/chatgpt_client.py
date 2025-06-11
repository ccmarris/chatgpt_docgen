import logging
import configparser
import openai
import os

_logger = logging.getLogger(__name__)

class IniFileSectionError(Exception):
    """Exception raised when a required section is missing in the ini file."""
    pass
class IniFileKeyError(Exception):
    """Exception raised when a required key is missing in the ini file."""
    pass
class APIKeyFormatError(Exception):
    """Exception raised when the API key format is incorrect."""
    pass    


class ChatGPTClient():
    """
    A client for interacting with the OpenAI API to generate responses based on prompts.
    This class reads configuration from an ini file, including the API key, and provides
    methods to get responses from the OpenAI API.
    Attributes:
        api_key (str): The API key for OpenAI.
        server (str): The server URL for OpenAI.
        user (str): The username for authentication.
        resolution_field (str): A field used for resolution in the API requests.
    Methods:
        read_ini(filename: str) -> dict:
            Reads the configuration from an ini file.
        get_response(prompt: str, model: str, temperature: float, top_p: float,
                     frequency_penalty: float, presence_penalty: float) -> str:
            Gets a response from the OpenAI API based on the provided prompt and parameters.
    """
    def __init__(self, inifile:str=''):
        """
        Initialize the ChatGPTClient with configuration from an ini file.

        Parameters:
            ini_file (str): Path to the ini file containing configuration.
        """
        # Read configuration from ini file
        if inifile:
            print(f'Using ini file: {inifile}')
            config = self.read_ini(filename=inifile)
            # Set attributes from config or take defaults
            self.model = config.get('model', 'gpt-3.5-turbo')
            self.api_key = config.get('api_key', '')
        else:
            self.model = 'gpt-3.5-turbo'
            self.api_key = os.getenv("OPENAI_API_KEY")
        

        # Validate API key format
        if not self.api_key or not isinstance(self.api_key, str):
            raise APIKeyFormatError("API key must be a non-empty string.")
        if not self.api_key.startswith('sk-'):
            raise APIKeyFormatError("API key must start with 'sk-'.")

        self.ai = openai.OpenAI(
            api_key=self.api_key,
        )
        self.last_response = None
        self.error = None
        _logger.info(f'ChatGPTClient initialized')

        return

    # ** Facilitate ini file for basic configuration including API Key
    """Exception raised when the API key format is incorrect."""
    def read_ini(self, filename:str) -> dict:
        '''
        Open and parse ini file

        Parameters:
            filename (str): name of inifile

        Returns:
            config (dict): Dictionary of BloxOne configuration elements

        Raises:
            IniFileSectionError
            IniFileKeyError
            APIKeyFormatError
            FileNotFoundError

        '''
        # Local Variables
        cfg = configparser.ConfigParser()
        config = {}
        section = 'CHATGPT'
        ini_keys = ['model', 'api_key']
    
        '''
        Add these to the inifile config:
        model="gpt-3.5-turbo",
        temperature=1.0,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0):
        '''

        # Check for inifile and raise exception if not found
        if os.path.isfile(filename):
            # Attempt to read api_key from ini file
            try:
                cfg.read(filename)
            except configparser.Error as err:
                _logger.error(err)

            # Look for BloxOne section
            if section in cfg:
                for key in ini_keys:
                    # Check for key in section
                    if key in cfg[section]:
                        config[key] = cfg[section][key].strip("'\"")
                        _logger.debug(f'Key {key} found in {filename}: {config[key]}')
                    else:
                        _logger.error(f'Key {key} not found in {section} section.')
                        # raise IniFileKeyError(f'Key "{key}" not found within' +
                        #        f'[{section}] section of ini file {filename}')
                        
            else:
                _logger.error(f'No {section} Section in config file: {filename}')
                raise IniFileSectionError(f'No [{section}] section found in ini file {filename}')
            
        else:
            raise FileNotFoundError('ini file "{filename}" not found.')

        return config


    def get_response(self,
        prompt:str,
        model:str='',
        temperature=1.0,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0):

        '''
        Get a response from the OpenAI API based on the provided prompt and parameters.
        Parameters:
            prompt (str): The prompt to send to the OpenAI API.
            model (str): The model to use for generating the response.
            temperature (float): Sampling temperature.
            top_p (float): Nucleus sampling parameter.
            frequency_penalty (float): Frequency penalty parameter.
            presence_penalty (float): Presence penalty parameter.
        Returns:
            str: The response from the OpenAI API.
        Raises:
            openai.error.OpenAIError: If there is an error with the OpenAI API request.
        '''
        # Use the model from the ini file if not provided
        status:str = ''

        if not model:
            model = self.model

        _logger.debug = f'Using model: {model}, temperature: {temperature}, top_p: {top_p}, frequency_penalty: {frequency_penalty}, presence_penalty: {presence_penalty}'

        try:
            response = self.ai.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty
            )
            self.last_response = response.choices[0].message.content.strip()
            status = 'Success'
            _logger.debug(f'Response received: {self.last_response}')
        except openai.OpenAIError as e:
            _logger.error(f"OpenAI API error: {e}")
            status = f"Error: {e}"

        return status