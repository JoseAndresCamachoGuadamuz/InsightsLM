import os
import ollama
import openai
import anthropic
import google.generativeai as genai
from services.config_service import load_config, decrypt_key
import logging

# Set up logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Model Definitions ---

# A dictionary mapping our app's internal model keys to the actual API model names
# NOTE: Google models will use dynamic discovery, these are fallback names
SUPPORTED_MODELS = {
    # Ollama
    "ollama_mistral": "mistral",
    "ollama_llama3": "llama3",
    # OpenAI
    "openai_gpt5": "gpt-5",
    "openai_gpt5_mini": "gpt-5-mini",
    "openai_gpt5_nano": "gpt-5-nano",
    "openai_gpt4o": "gpt-4o",
    "openai_gpt4_turbo": "gpt-4-turbo",
    # Anthropic
    "claude_3_5_sonnet": "claude-3-5-sonnet-20240620",
    "claude_3_opus": "claude-3-opus-20240229",
    # Google - Original values (will be overridden by dynamic discovery)
    "gemini_1_5_pro": "gemini-1.5-pro",
    "gemini_1_5_flash": "gemini-1.5-flash",
}

# --- Helper Functions for Dynamic Key Loading ---

def _get_fresh_api_keys():
    """
    REQUIREMENT 5.1: Load and decrypt API keys fresh from config on each request.
    This ensures settings changes are picked up immediately.
    """
    try:
        config = load_config()
        api_keys = config.get("api_keys", {})
        
        keys = {
            "openai": decrypt_key(api_keys.get("openai", "")),
            "anthropic": decrypt_key(api_keys.get("anthropic", "")),
            "google": decrypt_key(api_keys.get("google", ""))
        }
        
        logger.info("Successfully loaded and decrypted API keys from config")
        return keys
    except Exception as e:
        logger.error(f"Failed to load API keys: {e}")
        return {"openai": "", "anthropic": "", "google": ""}

def _setup_openai_client(api_key: str):
    """Configure OpenAI client with fresh API key."""
    if not api_key:
        raise ValueError("OpenAI API key is not configured.")
    openai.api_key = api_key
    logger.info("OpenAI client configured with fresh API key")

def _setup_anthropic_client(api_key: str):
    """Configure Anthropic client with fresh API key."""
    if not api_key:
        raise ValueError("Anthropic API key is not configured.")
    client = anthropic.Anthropic(api_key=api_key)
    logger.info("Anthropic client configured with fresh API key")
    return client

def _setup_gemini_client(api_key: str):
    """
    REQUIREMENT 5.2: Configure Google Gemini with correct API syntax.
    Fixed the incorrect genai.config["api_key"] usage.
    """
    if not api_key:
        raise ValueError("Google Gemini API key is not configured.")
    genai.configure(api_key=api_key)
    logger.info("Google Gemini configured with fresh API key")

def _get_working_gemini_model():
    """
    DYNAMIC GEMINI FIX: Get a working Gemini model name with caching to avoid repeated API calls.
    Returns the same model that the test connection found working.
    """
    # Use cached model if available (avoid repeated API calls)
    if hasattr(_get_working_gemini_model, '_cached_model'):
        return _get_working_gemini_model._cached_model
    
    try:
        logger.info("Discovering available Gemini models...")
        
        # List available models
        available_models = list(genai.list_models())
        logger.info(f"Found {len(available_models)} total models")
        
        # Try preferred models in order
        model_preferences = [
            "gemini-1.5-pro-latest",
            "gemini-1.5-pro", 
            "gemini-pro",
            "gemini-1.0-pro"
        ]
        
        # Check if any preferred model is available and supports generation
        for model in available_models:
            model_name = model.name.replace("models/", "")
            if model_name in model_preferences and "generateContent" in model.supported_generation_methods:
                logger.info(f"Found preferred working model: {model_name}")
                # Cache the working model
                _get_working_gemini_model._cached_model = model_name
                return model_name
        
        # Fallback: use first available text generation model
        for model in available_models:
            if "generateContent" in model.supported_generation_methods:
                model_name = model.name.replace("models/", "")
                logger.info(f"Using fallback working model: {model_name}")
                _get_working_gemini_model._cached_model = model_name
                return model_name
                
    except Exception as e:
        logger.error(f"Failed to discover Gemini models: {e}")
    
    # Ultimate fallback (this should not happen if test connection works)
    logger.warning("Using ultimate fallback model: gemini-pro")
    return "gemini-pro"

# --- STEP 1: Model Discovery Functions ---

def get_ollama_models():
    """
    Query Ollama for available local models.
    Returns a list of model dictionaries with 'key' and 'label' fields.
    Returns empty list if Ollama is not available.
    
    STEP 6A: Enhanced error detection with user-friendly messages.
    """
    try:
        logger.info("Querying Ollama for available models...")
        # Query Ollama API for installed models
        models_response = ollama.list()
        
        # FIXED: ollama.list() returns a Pydantic ListResponse object, not a dict
        # Access the models attribute directly
        if hasattr(models_response, 'models'):
            ollama_models = models_response.models
        else:
            logger.warning("Unexpected Ollama response structure")
            return []
        
        # STEP 6A: Check if no models are installed
        if not ollama_models or len(ollama_models) == 0:
            logger.warning("Ollama is running but no models installed")
            raise ValueError("No Ollama models installed. Install a model with: ollama pull llama3")
        
        # Format models for frontend
        formatted_models = []
        for model in ollama_models:
            # FIXED: Each model is a Pydantic Model object with a 'model' attribute
            # Extract model name (e.g., "llama3:latest" -> "llama3")
            if hasattr(model, 'model'):
                model_name = model.model.split(':')[0]  # Remove tag if present
            else:
                logger.warning(f"Unexpected model object structure: {model}")
                continue
            
            if model_name:
                # Create model key (e.g., "ollama_mistral")
                model_key = f"ollama_{model_name}"
                # Create display label (e.g., "Ollama: Mistral")
                model_label = f"Ollama: {model_name.capitalize()}"
                
                formatted_models.append({
                    'key': model_key,
                    'label': model_label,
                    'provider': 'ollama'
                })
        
        logger.info(f"Found {len(formatted_models)} Ollama models")
        return formatted_models
        
    except Exception as e:
        # STEP 6A: Enhanced error detection for user-friendly messages
        error_str = str(e).lower()
        
        # Check if Ollama is not running (connection refused)
        if "connect" in error_str or "connection" in error_str or "refused" in error_str or "unreachable" in error_str:
            logger.warning("Ollama service not running")
            raise ValueError("Ollama is not running. Please start Ollama to use local models.")
        
        # Check if no models installed (our custom message)
        if "no ollama models installed" in error_str:
            raise  # Re-raise our custom message
        
        # Generic Ollama error
        logger.warning(f"Ollama error: {e}")
        raise ValueError(f"Ollama error: {str(e)}")

def get_openai_models():
    """
    Query OpenAI API for available models based on user's API key.
    Returns a list of model dictionaries with 'key' and 'label' fields.
    Returns empty list if OpenAI is not configured or unavailable.
    
    STEP 6A: Enhanced error detection with user-friendly messages.
    """
    try:
        keys = _get_fresh_api_keys()
        if not keys["openai"]:
            logger.info("OpenAI API key not configured, skipping")
            return []
        
        logger.info("Querying OpenAI for available models...")
        _setup_openai_client(keys["openai"])
        
        # Query OpenAI for available models
        models_response = openai.models.list()
        
        # Filter for chat completion models (GPT models)
        chat_models = []
        for model in models_response.data:
            model_id = model.id
            # Filter for GPT models suitable for chat
            if any(prefix in model_id for prefix in ['gpt-4', 'gpt-3.5', 'gpt-5']):
                # Create model key (e.g., "openai_gpt4o")
                model_key = f"openai_{model_id.replace('-', '_').replace('.', '_')}"
                # Create display label (e.g., "OpenAI: GPT-4o")
                model_label = f"OpenAI: {model_id.upper()}"
                
                chat_models.append({
                    'key': model_key,
                    'label': model_label,
                    'provider': 'openai',
                    'model_id': model_id  # Store original model ID for API calls
                })
        
        logger.info(f"Found {len(chat_models)} OpenAI models")
        return chat_models
        
    except Exception as e:
        # STEP 6A: Enhanced error detection for user-friendly messages
        error_str = str(e).lower()
        
        # Check for authentication errors (invalid API key)
        if "401" in error_str or "unauthorized" in error_str or "authentication" in error_str or "api key" in error_str:
            logger.warning("OpenAI API key is invalid")
            raise ValueError("OpenAI API key is invalid. Please check your key in Settings.")
        
        # Check for forbidden errors (key has no access)
        if "403" in error_str or "forbidden" in error_str:
            logger.warning("OpenAI API key lacks permissions")
            raise ValueError("OpenAI API key lacks required permissions. Please check your key in Settings.")
        
        # Check for network errors
        if "connection" in error_str or "timeout" in error_str or "network" in error_str:
            logger.warning("Network error connecting to OpenAI")
            raise ValueError("Unable to connect to OpenAI. Please check your internet connection.")
        
        # Generic OpenAI error
        logger.warning(f"OpenAI error: {e}")
        raise ValueError(f"OpenAI error: {str(e)}")

def get_anthropic_models():
    """
    Return list of available Anthropic Claude models.
    Returns a list of model dictionaries with 'key' and 'label' fields.
    Returns empty list if Anthropic API key is not configured.
    
    Note: Anthropic doesn't have a models.list() API, so we return known models.
    
    STEP 6A: Enhanced error detection with user-friendly messages.
    """
    try:
        keys = _get_fresh_api_keys()
        if not keys["anthropic"]:
            logger.info("Anthropic API key not configured, skipping")
            return []
        
        logger.info("Returning available Anthropic models...")
        
        # Known Anthropic models (no discovery API available)
        anthropic_models = [
            {
                'key': 'claude_3_5_sonnet',
                'label': 'Anthropic: Claude 3.5 Sonnet',
                'provider': 'anthropic',
                'model_id': 'claude-3-5-sonnet-20240620'
            },
            {
                'key': 'claude_3_5_haiku',
                'label': 'Anthropic: Claude 3.5 Haiku',
                'provider': 'anthropic',
                'model_id': 'claude-3-5-haiku-20241022'
            },
            {
                'key': 'claude_3_opus',
                'label': 'Anthropic: Claude 3 Opus',
                'provider': 'anthropic',
                'model_id': 'claude-3-opus-20240229'
            }
        ]
        
        logger.info(f"Found {len(anthropic_models)} Anthropic models")
        return anthropic_models
        
    except Exception as e:
        # STEP 6A: Enhanced error detection for user-friendly messages
        error_str = str(e).lower()
        
        # Check for authentication errors (invalid API key)
        if "401" in error_str or "unauthorized" in error_str or "authentication" in error_str or "api key" in error_str:
            logger.warning("Anthropic API key is invalid")
            raise ValueError("Anthropic API key is invalid. Please check your key in Settings.")
        
        # Check for forbidden errors
        if "403" in error_str or "forbidden" in error_str:
            logger.warning("Anthropic API key lacks permissions")
            raise ValueError("Anthropic API key lacks required permissions. Please check your key in Settings.")
        
        # Generic Anthropic error
        logger.warning(f"Anthropic error: {e}")
        raise ValueError(f"Anthropic error: {str(e)}")

def get_google_models():
    """
    Query Google Gemini API for available models based on user's API key.
    Returns a list of model dictionaries with 'key' and 'label' fields.
    Returns empty list if Google API key is not configured or unavailable.
    
    STEP 6A: Enhanced error detection with user-friendly messages.
    """
    try:
        keys = _get_fresh_api_keys()
        if not keys["google"]:
            logger.info("Google Gemini API key not configured, skipping")
            return []
        
        logger.info("Querying Google Gemini for available models...")
        _setup_gemini_client(keys["google"])
        
        # Query Google for available models
        available_models = list(genai.list_models())
        
        # Filter for models that support content generation
        gemini_models = []
        for model in available_models:
            # Only include models that support generateContent
            if "generateContent" in model.supported_generation_methods:
                model_name = model.name.replace("models/", "")
                
                # Create model key (e.g., "gemini_gemini_1_5_pro")
                model_key = f"gemini_{model_name.replace('-', '_').replace('.', '_')}"
                # Create display label (e.g., "Google: Gemini 1.5 Pro")
                model_label = f"Google: {model_name.title()}"
                
                gemini_models.append({
                    'key': model_key,
                    'label': model_label,
                    'provider': 'google',
                    'model_id': model_name
                })
        
        logger.info(f"Found {len(gemini_models)} Google Gemini models")
        return gemini_models
        
    except Exception as e:
        # STEP 6A: Enhanced error detection for user-friendly messages
        error_str = str(e).lower()
        
        # Check for authentication errors (invalid API key)
        if "401" in error_str or "unauthorized" in error_str or "authentication" in error_str or "api key" in error_str or "invalid" in error_str:
            logger.warning("Google Gemini API key is invalid")
            raise ValueError("Google Gemini API key is invalid. Please check your key in Settings.")
        
        # Check for forbidden errors
        if "403" in error_str or "forbidden" in error_str:
            logger.warning("Google Gemini API key lacks permissions")
            raise ValueError("Google Gemini API key lacks required permissions. Please check your key in Settings.")
        
        # Check for network errors
        if "connection" in error_str or "timeout" in error_str or "network" in error_str:
            logger.warning("Network error connecting to Google Gemini")
            raise ValueError("Unable to connect to Google Gemini. Please check your internet connection.")
        
        # Generic Google error
        logger.warning(f"Google Gemini error: {e}")
        raise ValueError(f"Google Gemini error: {str(e)}")

def get_all_available_models():
    """
    Aggregate all available models from all providers.
    Returns a dictionary containing models and provider errors.
    Always returns a valid response (empty models list if no providers are available).
    
    Models are returned in provider order: Ollama, OpenAI, Anthropic, Google
    
    STEP 6A: Now collects errors from all providers for better user feedback.
    STEP 6C-1: Now returns provider_errors along with models for frontend display.
    
    Returns:
        dict: {
            "models": [{"key": str, "label": str, "provider": str}, ...],
            "provider_errors": {"provider": "error message", ...} or None
        }
    """
    all_models = []
    provider_errors = {}
    
    # Aggregate models from all providers
    # Order matters: Ollama (local) first, then cloud providers
    
    # 1. Ollama (local)
    try:
        ollama_models = get_ollama_models()
        all_models.extend(ollama_models)
    except ValueError as e:
        # Store user-friendly error message
        provider_errors['ollama'] = str(e)
        logger.info(f"Ollama unavailable: {e}")
    except Exception as e:
        provider_errors['ollama'] = "Ollama service error. Please check Ollama installation."
        logger.warning(f"Unexpected Ollama error: {e}")
    
    # 2. OpenAI
    try:
        openai_models = get_openai_models()
        all_models.extend(openai_models)
    except ValueError as e:
        provider_errors['openai'] = str(e)
        logger.info(f"OpenAI unavailable: {e}")
    except Exception as e:
        provider_errors['openai'] = "OpenAI service error. Please check your API key."
        logger.warning(f"Unexpected OpenAI error: {e}")
    
    # 3. Anthropic
    try:
        anthropic_models = get_anthropic_models()
        all_models.extend(anthropic_models)
    except ValueError as e:
        provider_errors['anthropic'] = str(e)
        logger.info(f"Anthropic unavailable: {e}")
    except Exception as e:
        provider_errors['anthropic'] = "Anthropic service error. Please check your API key."
        logger.warning(f"Unexpected Anthropic error: {e}")
    
    # 4. Google
    try:
        google_models = get_google_models()
        all_models.extend(google_models)
    except ValueError as e:
        provider_errors['google'] = str(e)
        logger.info(f"Google Gemini unavailable: {e}")
    except Exception as e:
        provider_errors['google'] = "Google Gemini service error. Please check your API key."
        logger.warning(f"Unexpected Google error: {e}")
    
    # Log summary
    logger.info(f"Total available models across all providers: {len(all_models)}")
    if provider_errors:
        logger.info(f"Provider errors: {provider_errors}")
    
    # STEP 6C-1: Return both models and provider errors for frontend display
    return {
        "models": all_models,
        "provider_errors": provider_errors if provider_errors else None
    }

# --- Model Calling Functions ---

def _call_ollama(model: str, prompt: str) -> str:
    """Call Ollama with fresh API key loading (none needed for local)."""
    try:
        logger.info(f"Sending prompt to Ollama model: {model}")
        response = ollama.chat(model=model, messages=[{'role': 'user', 'content': prompt}])
        return response['message']['content']
    except Exception as e:
        if "not found" in str(e).lower():
            raise ValueError(f"Ollama model '{model}' is not installed. Please run: ollama pull {model}")
        raise

def _call_openai(model: str, prompt: str) -> str:
    """Call OpenAI with fresh API key loading."""
    keys = _get_fresh_api_keys()
    _setup_openai_client(keys["openai"])
    
    logger.info(f"Sending prompt to OpenAI model: {model}")
    response = openai.chat.completions.create(
        model=model, 
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def _call_anthropic(model: str, prompt: str) -> str:
    """Call Anthropic with fresh API key loading."""
    keys = _get_fresh_api_keys()
    client = _setup_anthropic_client(keys["anthropic"])
    
    logger.info(f"Sending prompt to Anthropic model: {model}")
    message = client.messages.create(
        model=model, 
        max_tokens=4096, 
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text

def _call_gemini(model: str, prompt: str) -> str:
    """
    DYNAMIC GEMINI FIX: Call Google Gemini with dynamic model discovery.
    Uses the same model discovery that makes test connection work.
    """
    keys = _get_fresh_api_keys()
    _setup_gemini_client(keys["google"])
    
    # Use dynamic model discovery instead of the provided model name
    working_model = _get_working_gemini_model()
    
    logger.info(f"Sending prompt to Gemini model: {working_model} (originally requested: {model})")
    
    try:
        model_instance = genai.GenerativeModel(working_model)
        response = model_instance.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Failed to generate content with {working_model}: {e}")
        raise

# --- API Testing Functions (REQUIREMENT 5.4) ---

def test_ollama_connection(model: str = "mistral") -> dict:
    """Test Ollama connection and model availability."""
    try:
        # Test with a simple prompt
        response = ollama.chat(model=model, messages=[{'role': 'user', 'content': 'Hi'}])
        return {
            "success": True,
            "message": f"Ollama model '{model}' is working correctly",
            "provider": "ollama"
        }
    except Exception as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            return {
                "success": False,
                "message": f"Model '{model}' not found. Install with: ollama pull {model}",
                "provider": "ollama",
                "error": error_msg
            }
        return {
            "success": False,
            "message": f"Ollama connection failed: {error_msg}",
            "provider": "ollama",
            "error": error_msg
        }

def test_openai_connection() -> dict:
    """Test OpenAI API connection with fresh key loading."""
    try:
        keys = _get_fresh_api_keys()
        _setup_openai_client(keys["openai"])
        
        # Test with a simple completion
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # Use current reliable model for testing
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=5
        )
        
        return {
            "success": True,
            "message": "OpenAI API connection successful",
            "provider": "openai"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"OpenAI API connection failed: {str(e)}",
            "provider": "openai",
            "error": str(e)
        }

def test_anthropic_connection() -> dict:
    """Test Anthropic API connection with fresh key loading."""
    try:
        keys = _get_fresh_api_keys()
        client = _setup_anthropic_client(keys["anthropic"])
        
        # Test with a simple message
        message = client.messages.create(
            model="claude-3-5-haiku-20241022",  # Use latest Haiku for testing
            max_tokens=5,
            messages=[{"role": "user", "content": "Hi"}]
        )
        
        return {
            "success": True,
            "message": "Anthropic API connection successful",
            "provider": "anthropic"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Anthropic API connection failed: {str(e)}",
            "provider": "anthropic",
            "error": str(e)
        }

def test_gemini_connection() -> dict:
    """Test Google Gemini API connection with dynamic model discovery."""
    try:
        keys = _get_fresh_api_keys()
        _setup_gemini_client(keys["google"])
        
        # First, try to list available models to find a working one
        try:
            # List available models
            available_models = list(genai.list_models())
            
            # Find a suitable model for text generation
            suitable_model = None
            model_preferences = [
                "gemini-1.5-pro-latest",
                "gemini-1.5-pro", 
                "gemini-pro",
                "gemini-1.0-pro"
            ]
            
            # Check if any of our preferred models are available
            for model in available_models:
                model_name = model.name.replace("models/", "")
                if model_name in model_preferences:
                    suitable_model = model_name
                    break
            
            # If no preferred model found, use the first available text generation model
            if not suitable_model:
                for model in available_models:
                    if "generateContent" in model.supported_generation_methods:
                        suitable_model = model.name.replace("models/", "")
                        break
            
            if not suitable_model:
                return {
                    "success": False,
                    "message": "No suitable Gemini models found for text generation",
                    "provider": "google",
                    "error": "No compatible models available"
                }
            
            # Test with the suitable model
            model_instance = genai.GenerativeModel(suitable_model)
            response = model_instance.generate_content("Hi")
            
            return {
                "success": True,
                "message": f"Google Gemini API connection successful (using {suitable_model})",
                "provider": "google"
            }
            
        except Exception as model_error:
            # Fallback: try with the most basic model name
            try:
                model_instance = genai.GenerativeModel("gemini-pro")
                response = model_instance.generate_content("Hi")
                
                return {
                    "success": True,
                    "message": "Google Gemini API connection successful (using gemini-pro)",
                    "provider": "google"
                }
            except Exception as fallback_error:
                return {
                    "success": False,
                    "message": f"Google Gemini API connection failed: {str(fallback_error)}",
                    "provider": "google",
                    "error": str(fallback_error)
                }
                
    except Exception as e:
        return {
            "success": False,
            "message": f"Google Gemini API connection failed: {str(e)}",
            "provider": "google",
            "error": str(e)
        }

def test_api_connection(provider: str) -> dict:
    """
    REQUIREMENT 5.4: Test connection for a specific provider.
    Used by the new API testing endpoints.
    """
    if provider == "ollama":
        return test_ollama_connection()
    elif provider == "openai":
        return test_openai_connection()
    elif provider == "anthropic":
        return test_anthropic_connection()
    elif provider == "google":
        return test_gemini_connection()
    else:
        return {
            "success": False,
            "message": f"Unknown provider: {provider}",
            "provider": provider,
            "error": "Invalid provider"
        }

# --- Main Public Function ---

def generate_response(prompt: str, model_key: str = "ollama_mistral") -> str:
    """
    Routes a prompt to the specified AI provider and returns the response.
    REQUIREMENT 5.1: Now uses fresh API key loading on each request.
    DYNAMIC GEMINI FIX: Uses dynamic model discovery for Google Gemini.
    """
    if model_key not in SUPPORTED_MODELS:
        raise ValueError(f"Model '{model_key}' is not supported.")

    model_name = SUPPORTED_MODELS[model_key]
    
    try:
        if model_key.startswith("ollama"):
            return _call_ollama(model_name, prompt)
        elif model_key.startswith("openai"):
            return _call_openai(model_name, prompt)
        elif model_key.startswith("claude"):
            return _call_anthropic(model_name, prompt)
        elif model_key.startswith("gemini"):
            return _call_gemini(model_name, prompt)
        else:
            raise ValueError("Unknown model provider.")
    except Exception as e:
        logger.error(f"Error with {model_key}: {e}")
        return f"Error: Could not get a response from {model_key}. {str(e)}"