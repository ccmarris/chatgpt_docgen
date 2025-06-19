import logging
import configparser
import os
import response_cache
import openai

__author__ = "Chris Marrison"
__copyright__ = "Copyright 2025, Chris Marrison / Infoblox"
__license__ = "BSD2"
__version__ = "0.2.1"
__email__ = "chris@infoblox.com"

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

class LLMClient:
    """Abstract base class for LLM providers."""
    def get_response(self, prompt, **kwargs):
        raise NotImplementedError("Subclasses must implement get_response()")

class OpenAIClient(LLMClient):
    """
    Client for OpenAI's GPT models.
    This client supports configuration via an ini file or environment variables.
    """
    def __init__(self, inifile='', use_cache:bool=True):
        """
        Initialize the OpenAI API with configuration from an ini file.

        Parameters:
            ini_file (str): Path to the ini file containing configuration.
        """

        if inifile:
            _logger.info(f'Using ini file: {inifile}')
            config = self.read_ini(filename=inifile)
            # Set attributes from config or take defaults
            self.model = config.get('model', 'gpt-3.5-turbo')
            self.api_key = config.get('api_key', '')
            self.temperature = float(config.get('temperature', 1.0))
            self.top_p = float(config.get('top_p', 1.0))
            self.frequency_penalty = float(config.get('frequency_penalty', 0.0))
            self.presence_penalty = float(config.get('presence_penalty', 0.0))
        # If no ini file is provided, use environment variables or defaults
        else:
            self.model = 'gpt-3.5-turbo'
            self.api_key = os.getenv("OPENAI_API_KEY")
            self.temperature = 1.0
            self.top_p = 1.0
            self.frequency_penalty = 0.0
            self.presence_penalty = 0.0
        _logger.debug(f'OpenAIClient initialized with model: {self.model}, temperature: {self.temperature}, top_p: {self.top_p}, frequency_penalty: {self.frequency_penalty}, presence_penalty: {self.presence_penalty}')

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
        self.last_usage = {}
        _logger.debug(f'OpenAIClient initialized')
    
        if use_cache:
            _logger.info("Using cache for responses.")
            self.cache = response_cache.RESPONSECACHE(cache_type='openai')
        else:
            _logger.info("Cache is disabled. Responses will not be cached.")
            self.cache = None

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
        section = 'OPENAI'
        ini_keys = [ 'api_key', 'model', 
                     'temperature', 'top_p', 
                     'frequency_penalty', 'presence_penalty' ]
    
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
                        _logger.debug(f'Key {key} not found in {section} section.')
                        # raise IniFileKeyError(f'Key "{key}" not found within' +
                        #        f'[{section}] section of ini file {filename}')
                        
            else:
                _logger.error(f'No {section} Section in config file: {filename}')
                raise IniFileSectionError(f'No [{section}] section found in ini file {filename}')
            
        else:
            raise FileNotFoundError('ini file "{filename}" not found.')

        return config


    def check_cache(self, **params):
        '''
        Check if the response for the given prompt and parameters is already cached.
        Parameters:
            prompt (str): The prompt to check in the cache.
            model (str): The model used for generating the response.
            temperature (float): Sampling temperature.
            top_p (float): Nucleus sampling parameter.
            frequency_penalty (float): Frequency penalty parameter.
            presence_penalty (float): Presence penalty parameter.
        Returns:
            bool: True if the response is cached, False otherwise.
        '''
        success = False
        prompt = params.get('prompt', '')
        if self.cache:
            cached = self.cache.check_cache(**params)
            if cached:
                self.last_response = cached
                _logger.debug(f'Cache hit for prompt: {prompt}')
                success = True
            else:
                _logger.debug(f'Cache miss for prompt: {prompt}')
                success = False
        else:
            _logger.debug(f'Cache is disabled, skipping cache check for prompt: {prompt}')
            success = False

        return success


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
        if not temperature:
            temperature = self.temperature
        if not top_p:
            top_p = self.top_p
        if not frequency_penalty:
            frequency_penalty = self.frequency_penalty
        if not presence_penalty:
            presence_penalty = self.presence_penalty
        # Log the parameters being used

        _logger.debug(f'Using model: {model}, temperature: {temperature}, top_p: {top_p}, frequency_penalty: {frequency_penalty}, presence_penalty: {presence_penalty}')

        if self.cache is not None:
            # If cache is enabled, check if the response is already cached
            _logger.debug(f'Cache is enabled, checking cache for prompt: {prompt}')

            if self.check_cache(prompt=prompt, model=model, 
                                temperature=temperature, 
                                top_p=top_p, 
                                frequency_penalty=frequency_penalty, 
                                presence_penalty=presence_penalty):
                status = 'Success'
                _logger.debug(f'Response from cache: {self.last_response}')
            else:
                # If cache miss, call the OpenAI API
                _logger.debug(f'Cache miss for prompt: {prompt}')
                status = self.call_api(prompt, model, temperature, top_p, frequency_penalty, presence_penalty)
                try:
                    _logger.debug(f'Caching response for prompt: {prompt}')
                    self.cache.add_entry(prompt=prompt, 
                                        response=self.last_response, 
                                        model=model, temperature=temperature, 
                                        top_p=top_p, 
                                        frequency_penalty=frequency_penalty, 
                                        presence_penalty=presence_penalty)
                except Exception as e:
                    _logger.error(f"Error saving response to cache: {e}")

        else:
            # If cache is disabled, call the OpenAI API directly
            _logger.debug(f'Cache is disabled, calling OpenAI API directly for prompt: {prompt}')
            status = self.call_api(prompt, model, 
                                   temperature, top_p, 
                                   frequency_penalty, presence_penalty)


        return status


    def call_api(self, prompt, model, temperature, top_p, frequency_penalty, presence_penalty):
        """
        Call the OpenAI API to get a response for the given prompt and parameters.
                _logger.debug(f'Cache miss for prompt: {prompt}')
                status = self._call_openai_api(prompt, model, temperature, top_p, frequency_penalty, presence_penalty)
                if status == 'Success' and self.cache:
                    _logger.debug(f'Caching response for prompt: {prompt}')
                    self.cache.save_response(prompt, self.last_response, model=model, temperature=temperature, top_p=top_p, frequency_penalty=frequency_penalty, presence_penalty=presence_penalty)

        else:
            status = self._call_openai_api(prompt, model, temperature, top_p, frequency_penalty=frequency_penalty, presence_penalty=presence_penalty)
        """
        _logger.debug(f'Calling OpenAI API with prompt: {prompt}')
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
            self.last_usage = {
                'total_tokens': response.usage.total_tokens,
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens
            }
            status = 'Success'
            _logger.debug(f'Response received: {self.last_response}')
        except openai.OpenAIError as e:
            _logger.error(f"OpenAI API error: {e}")
            status = f"Error: {e}"

        return status


class AnthropicClient(LLMClient):
    def __init__(self, api_key):
        import anthropic
        self.anthropic = anthropic
        self.api_key = api_key
        # Add other config as needed

    def get_response(self, prompt, **kwargs):
        # Placeholder for Anthropic API call
        # Example:
        # response = self.anthropic.Client(api_key=self.api_key).completions.create(...)
        # return response.completion
        _logger.warning("AnthropicClient is not yet implemented.")
        return "Anthropic integration not implemented."

def get_llm_client(provider="openai", **kwargs):
    if provider == "openai":
        return OpenAIClient(kwargs.get('inifile', ''), use_cache=kwargs.get('use_cache', True))
    elif provider == "anthropic":
           return OpenAIClient(kwargs.get('inifile',''), use_cache=kwargs.get('use_cache', True))
    else:
        raise ValueError(f"Unknown provider: {provider}")

def clear_cache(provider="openai", inifile=''):
    """
    Clear the response cache for the specified provider.
    Parameters:
        provider (str): The LLM provider to clear the cache for.
        inifile (str): Path to the ini file containing configuration.
    """
    success = False
    try:
        cache = response_cache.RESPONSECACHE(cache_type=provider)
        cache.reset()
        success = True
        _logger.info(f"Cache cleared for provider: {provider}")
    except Exception as e:
        _logger.error(f"Error clearing cache for provider {provider}: {e}")
        success = False
    
    return success

# Example usage in main.py:
# client = get_llm_client(provider=args.provider, inifile=args.ini)
# response = client.get_response(prompt, temperature=args.temperature, ...)