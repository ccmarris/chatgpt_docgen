import logging
import configparser
import os
import openai
import json
from platformdirs import user_cache_dir
from datetime import datetime

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
    def __init__(self, inifile:str='', cache_file='prompt_cache.json'):
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
        _logger.debug(f'ChatGPTClient initialized with model: {self.model}, temperature: {self.temperature}, top_p: {self.top_p}, frequency_penalty: {self.frequency_penalty}, presence_penalty: {self.presence_penalty}')

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
        _logger.debug(f'ChatGPTClient initialized')
    
        self.cache_dir = user_cache_dir("chatgpt_docgen")
        self.cache_file = self.cache_dir + '/' + cache_file
        self.cache = self._load_cache()

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


    def _load_cache(self):
        '''
        Load the cache from the cache file.

        Returns:
            list: List of cached responses.
        '''
        cache = []

        if os.path.exists(self.cache_file):
            with open(self.cache_file, "r", encoding="utf-8") as f:
                cache = json.load(f)
            cache = self._validate_cache(cache)
        else:
            # Create the cache directory if it doesn't exist
            os.makedirs(self.cache_dir, exist_ok=True)
            _logger.debug(f'Cache file not found, creating new cache file: {self.cache_file}')
            # Initialize an empty cache
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(cache, f, indent=2)
            
        _logger.debug(f'Cache loaded with {len(cache)} entries.')

        return cache

    def _validate_cache(self, cache):
        # Ensure all entries have the required fields
        # Ensure the cache is a list
        if not isinstance(cache, list):
            _logger.error(f'Cache file {self.cache_file} is not a valid JSON list. Resetting cache.')
            cache = []
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(cache, f, indent=2)
        # Ensure the cache is a list of dictionaries
        if not all(isinstance(entry, dict) for entry in cache):
            _logger.error(f'Cache file {self.cache_file} contains non-dictionary entries. Resetting cache.')
            cache = []
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(cache, f, indent=2)
        for entry in cache:
            if not all(key in entry for key in ["prompt", "model", "temperature", "top_p", "frequency_penalty", "presence_penalty", "response", "timestamp"]):
                _logger.error(f'Cache entry {entry} is missing required fields. Resetting cache.')
                cache = []
                with open(self.cache_file, "w", encoding="utf-8") as f:
                    json.dump(cache, f, indent=2)
                break
        _logger.debug(f'Cache loaded successfully with {len(cache)} entries.')
        # Return the loaded cache
        
        return cache

    def _clean_cache(self, cache_file="openai_cache.json", days=28):

        cutoff = datetime.now() - timedelta(days=days)
        cleaned_cache = [
            entry for entry in self.cache
            if "timestamp" in entry and datetime.fromisoformat(entry["timestamp"]) >= cutoff
        ]

        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cleaned_cache, f, indent=2)

        _logger.debug(f"Cleaned cache. {len(cache) - len(cleaned_cache)} entries removed.")
        self.cache = cleaned_cache
        self._save_cache()
        _logger.debug(f'Cache cleaned. {len(self.cache)} entries remaining.') 

        return cleaned_cache


    def _clear_cache(self):
        '''
        Clear the cache by removing the cache file.
        '''
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
            self.cache = self._load_cache()  # Reload the cache to ensure it's empty
            _logger.info(f'Cache cleared: {self.cache_file}')
        else:
            _logger.info('No cache file to clear.')
        return

    def _save_cache(self):
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(self.cache, f, indent=2)
        return

    def _find_in_cache(self, prompt, params):
        response = None
        for entry in self.cache:
            if (entry["prompt"] == prompt and entry["model"] == self.model and
                entry["temperature"] == params["temperature"] and
                entry["top_p"] == params["top_p"] and
                entry["frequency_penalty"] == params["frequency_penalty"] and
                entry["presence_penalty"] == params["presence_penalty"]):
                response = entry["response"]
        return response

    def _cache_response(self, prompt, params, response):
        self.cache.append({
            "prompt": prompt,
            "model": self.model,
            "temperature": params["temperature"],
            "top_p": params["top_p"],
            "frequency_penalty": params["frequency_penalty"],
            "presence_penalty": params["presence_penalty"],
            "response": response,
            "timestamp": datetime.now().isoformat()
        })
        self._save_cache()
        return 

    def _clear_cache(self):
        '''
        Clear the cache by removing the cache file.
        '''
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
            self.cache = []
            _logger.debug(f'Cache cleared: {self.cache_file}')
        else:
            _logger.debug('No cache file to clear.')
        return 

    def use_cache(self, prompt, **params):
        cached = self._find_in_cache(prompt, params)
        if cached:
            self.last_response = cached
            _logger.debug(f'Cache hit for prompt: {prompt}')
            response = 'Success'
        else:
            _logger.debug(f'Cache miss for prompt: {prompt}')
            # If not found in cache, get a new response
            response = self.get_response(prompt, **params)
            if response is "Success":
                self._cache_response(prompt, params, self.last_response)

        return response


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