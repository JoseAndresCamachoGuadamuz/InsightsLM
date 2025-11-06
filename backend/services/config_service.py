# backend/services/config_service.py
# VERSION: Step 2 - Fix Missing Encryption Key File
# CHANGES: Add safety check to create .encryption_key file if missing
# REASON: Flag was set but file was never created, breaking encryption

import json
import os
import base64
import uuid
import platform
import traceback
from appdirs import user_data_dir
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes

# --- Constants ---
# Define application details for appdirs
APP_NAME = "InsightsLM"
APP_AUTHOR = "InsightsLM_Dev"

# Get the standard user data directory for this application
APP_DATA_DIR = user_data_dir(APP_NAME, APP_AUTHOR)

# Define the full path for our configuration file
CONFIG_FILE_PATH = os.path.join(APP_DATA_DIR, "config.json")

# STEP 1 CHANGE: Define path for persistent encryption key file
ENCRYPTION_KEY_FILE = os.path.join(APP_DATA_DIR, ".encryption_key")

# OLD SECRET KEY - Only used for one-time migration of existing keys
OLD_SECRET_KEY = b'a_very_secret_key_for_insightslm'
SALT = b'a_fixed_salt_for_derivation'

# Debug flag - set to False to disable debug logging in production
DEBUG_ENABLED = True

def debug_log(message: str):
    """Safe debug logging that can be easily disabled."""
    if DEBUG_ENABLED:
        print(f"[DEBUG config_service] {message}")

def error_log(message: str, exception: Exception = None):
    """Error logging with optional exception details."""
    print(f"[ERROR config_service] {message}")
    if exception and DEBUG_ENABLED:
        traceback.print_exc()

def mask_sensitive(data: str, show_chars: int = 4) -> str:
    """Safely mask sensitive data for logging."""
    if not data:
        return "<empty>"
    if len(data) <= show_chars:
        return "*" * len(data)
    return f"{data[:show_chars]}...{data[-2:]} (length: {len(data)})"

# --- File-Based Key Management (STEP 1 NEW) ---

def get_or_create_master_key() -> bytes:
    """
    STEP 1 NEW FUNCTION: Get or create persistent master encryption key.
    
    This key is stored in a file and persists across system changes,
    solving the MAC address instability problem in WSL.
    
    The key file is created once and reused forever, ensuring encrypted
    data can always be decrypted regardless of network adapter changes.
    
    Security:
    - 256-bit random key (32 bytes)
    - Stored with restrictive permissions (owner read/write only)
    - Located in user data directory (outside git repository)
    
    Returns:
        bytes: 32-byte master encryption key
    """
    debug_log("Getting or creating master encryption key...")
    
    try:
        if os.path.exists(ENCRYPTION_KEY_FILE):
            # Key file exists, read it
            debug_log(f"Reading existing key file: {ENCRYPTION_KEY_FILE}")
            with open(ENCRYPTION_KEY_FILE, 'rb') as f:
                master_key = f.read()
            
            # Verify key length
            if len(master_key) != 32:
                error_log(f"Invalid key file length: {len(master_key)} bytes (expected 32)")
                raise ValueError("Corrupted encryption key file")
            
            debug_log("Master key loaded successfully from file")
            return master_key
        
        else:
            # First run - generate new key
            debug_log("No encryption key file found, generating new one...")
            print("=" * 60)
            print("[INIT] First-time setup: Generating master encryption key")
            print("=" * 60)
            
            # Generate cryptographically secure random key
            master_key = get_random_bytes(32)  # 32 bytes = 256 bits
            debug_log(f"Generated {len(master_key)}-byte random key")
            
            # Ensure directory exists
            os.makedirs(APP_DATA_DIR, exist_ok=True)
            
            # Save key to file
            debug_log(f"Saving key to: {ENCRYPTION_KEY_FILE}")
            with open(ENCRYPTION_KEY_FILE, 'wb') as f:
                f.write(master_key)
            
            # Set restrictive permissions (owner read/write only: 0o600)
            debug_log("Setting restrictive file permissions (0o600)...")
            os.chmod(ENCRYPTION_KEY_FILE, 0o600)
            
            print(f"[INIT] ✓ Master encryption key created: {ENCRYPTION_KEY_FILE}")
            print(f"[INIT] ✓ File permissions set to owner-only access")
            print("=" * 60)
            debug_log("Master key created and saved successfully")
            
            return master_key
            
    except Exception as e:
        error_log(f"Failed to get/create master key: {e}", e)
        raise

# --- Encryption & Decryption Helpers ---

def get_encryption_key():
    """
    STEP 1 MODIFIED: Derives encryption key from persistent file-based master key.
    
    CHANGE: Replaced get_machine_uuid() with get_or_create_master_key()
    REASON: MAC address changes in WSL break encryption. File-based key persists.
    
    Security layers:
    1. 256-bit random master key (from file)
    2. App-specific derivation (master_key + APP_NAME)
    3. PBKDF2 key derivation (additional security layer)
    
    Returns:
        bytes: 32-byte derived encryption key for AES-256
    """
    debug_log("Deriving encryption key...")
    try:
        # STEP 1 CHANGE: Use persistent file-based key instead of MAC address
        master_key = get_or_create_master_key()
        
        # Combine master key with app name for app-specific uniqueness
        app_specific_key = master_key + APP_NAME.encode('utf-8')
        
        debug_log("Running PBKDF2 key derivation...")
        derived_key = PBKDF2(app_specific_key, SALT, dkLen=32)  # 32 bytes for AES-256
        
        debug_log(f"Encryption key derived successfully (length: {len(derived_key)} bytes)")
        return derived_key
    except Exception as e:
        error_log(f"Failed to derive encryption key: {e}", e)
        raise

def encrypt_key(api_key: str) -> str:
    """Encrypts an API key and returns it as a base64 encoded string."""
    debug_log(f"encrypt_key() called with key: {mask_sensitive(api_key)}")
    
    if not api_key:
        debug_log("Empty API key provided, returning empty string")
        return ""
    
    try:
        debug_log("Step 1: Getting encryption key...")
        key = get_encryption_key()
        
        debug_log("Step 2: Creating AES cipher in CBC mode...")
        cipher = AES.new(key, AES.MODE_CBC)
        debug_log(f"AES cipher created (IV length: {len(cipher.iv)} bytes)")
        
        debug_log("Step 3: Encoding and padding plaintext...")
        plaintext_bytes = api_key.encode('utf-8')
        debug_log(f"Plaintext encoded to {len(plaintext_bytes)} bytes")
        
        padded_data = pad(plaintext_bytes, AES.block_size)
        debug_log(f"Data padded to {len(padded_data)} bytes (block size: {AES.block_size})")
        
        debug_log("Step 4: Encrypting data...")
        ct_bytes = cipher.encrypt(padded_data)
        debug_log(f"Encryption successful, ciphertext length: {len(ct_bytes)} bytes")
        
        debug_log("Step 5: Combining IV + ciphertext and encoding to base64...")
        combined = cipher.iv + ct_bytes
        debug_log(f"Combined IV+ciphertext length: {len(combined)} bytes")
        
        encrypted_result = base64.b64encode(combined).decode('utf-8')
        debug_log(f"Base64 encoding successful, final result length: {len(encrypted_result)} chars")
        debug_log(f"Encrypted result preview: {encrypted_result[:20]}...{encrypted_result[-20:]}")
        
        return encrypted_result
        
    except Exception as e:
        error_log(f"Exception during encryption: {type(e).__name__}: {e}", e)
        return ""

def decrypt_key(encrypted_key: str) -> str:
    """Decrypts a base64 encoded API key string."""
    debug_log(f"decrypt_key() called with encrypted key: {mask_sensitive(encrypted_key, 8)}")
    
    if not encrypted_key:
        debug_log("Empty encrypted key provided, returning empty string")
        return ""
    
    try:
        debug_log("Step 1: Getting encryption key...")
        key = get_encryption_key()
        
        debug_log("Step 2: Decoding base64...")
        decoded_data = base64.b64decode(encrypted_key)
        debug_log(f"Base64 decoded to {len(decoded_data)} bytes")
        
        debug_log("Step 3: Extracting IV and ciphertext...")
        # The first 16 bytes are the IV, the rest is the ciphertext
        iv = decoded_data[:16]
        ct = decoded_data[16:]
        debug_log(f"IV extracted: {len(iv)} bytes, Ciphertext: {len(ct)} bytes")
        
        debug_log("Step 4: Creating AES cipher with extracted IV...")
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        debug_log("Step 5: Decrypting ciphertext...")
        decrypted_padded = cipher.decrypt(ct)
        debug_log(f"Decryption successful, padded plaintext length: {len(decrypted_padded)} bytes")
        
        debug_log("Step 6: Removing padding...")
        pt = unpad(decrypted_padded, AES.block_size)
        debug_log(f"Padding removed, final plaintext length: {len(pt)} bytes")
        
        result = pt.decode('utf-8')
        debug_log(f"Decryption successful, result: {mask_sensitive(result)}")
        
        return result
        
    except (ValueError, KeyError) as e:
        error_log(f"Decryption failed (likely malformed/corrupted key): {type(e).__name__}: {e}", e)
        return ""
    except Exception as e:
        error_log(f"Unexpected error during decryption: {type(e).__name__}: {e}", e)
        return ""


# --- Migration Helpers ---

def is_old_encryption(config: dict) -> bool:
    """
    Check if config uses old hardcoded key encryption.
    Returns True if any encrypted keys are detected using the old system.
    """
    debug_log("Checking if config uses old encryption system...")
    api_keys = config.get("api_keys", {})
    
    for key_name, encrypted_value in api_keys.items():
        if not encrypted_value:
            continue
            
        try:
            debug_log(f"Testing {key_name} with old encryption method...")
            # Try decrypting with OLD hardcoded key
            old_key = PBKDF2(OLD_SECRET_KEY, SALT, dkLen=32)
            decoded = base64.b64decode(encrypted_value)
            iv = decoded[:16]
            ct = decoded[16:]
            cipher = AES.new(old_key, AES.MODE_CBC, iv)
            unpad(cipher.decrypt(ct), AES.block_size)
            
            # If we got here, decryption succeeded = old encryption detected
            debug_log(f"Old encryption detected for {key_name}!")
            return True
        except Exception:
            debug_log(f"Old encryption not detected for {key_name}")
            pass
    
    debug_log("No old encrypted keys found")
    return False

def migrate_old_keys(config: dict) -> dict:
    """
    Migrate API keys from old hardcoded encryption to new machine-specific encryption.
    This is a one-time migration performed automatically on first load.
    """
    print("=" * 60)
    print("[MIGRATION] Starting API key migration to machine-specific encryption...")
    print("=" * 60)
    
    old_key = PBKDF2(OLD_SECRET_KEY, SALT, dkLen=32)
    api_keys = config.get("api_keys", {})
    migration_success = True
    
    for key_name, encrypted_value in api_keys.items():
        if not encrypted_value:
            debug_log(f"Skipping empty key: {key_name}")
            continue
            
        try:
            debug_log(f"Migrating {key_name}...")
            
            # Step 1: Decrypt with OLD hardcoded key
            debug_log(f"  Step 1: Decrypting with old key...")
            decoded = base64.b64decode(encrypted_value)
            iv = decoded[:16]
            ct = decoded[16:]
            cipher = AES.new(old_key, AES.MODE_CBC, iv)
            plaintext = unpad(cipher.decrypt(ct), AES.block_size).decode('utf-8')
            debug_log(f"  Old decryption successful")
            
            # Step 2: Re-encrypt with NEW machine-specific key
            debug_log(f"  Step 2: Re-encrypting with new machine-specific key...")
            new_encrypted = encrypt_key(plaintext)
            config["api_keys"][key_name] = new_encrypted
            
            print(f"[MIGRATION] ✓ Successfully migrated {key_name} API key")
            
        except Exception as e:
            error_log(f"Failed to migrate {key_name}: {e}", e)
            print(f"[MIGRATION] ✗ Failed to migrate {key_name}")
            print(f"[MIGRATION]   User will need to re-enter {key_name} key in Settings")
            # Clear the corrupted key
            config["api_keys"][key_name] = ""
            migration_success = False
    
    # Mark as migrated (even if some keys failed - prevents retry loops)
    config["_migrated_to_machine_key"] = True
    
    if migration_success:
        print("[MIGRATION] ✓ Migration completed successfully!")
    else:
        print("[MIGRATION] ⚠ Migration completed with some warnings. Check logs above.")
    
    print("=" * 60)
    return config


# --- Configuration Management ---

def get_default_config():
    """Returns the default configuration dictionary."""
    debug_log("Creating default configuration...")
    return {
        "data_storage_path": APP_DATA_DIR,
        "default_model": "ollama_mistral",
        "api_keys": {
            "openai": "",  # Encrypted (empty by default)
            "anthropic": "",  # Encrypted (empty by default)
            "google": ""  # Encrypted (empty by default)
        }
    }

def load_config() -> dict:
    """
    Loads the configuration from the JSON file, creating it if it doesn't exist.
    Automatically performs one-time migration from old encryption to machine-specific encryption.
    
    STEP 1 MODIFIED: Added detection and handling for MAC-based to file-based migration.
    STEP 2 MODIFIED: Added safety check to create .encryption_key file if missing.
    """
    debug_log("=" * 60)
    debug_log("load_config() called")
    debug_log(f"Config file path: {CONFIG_FILE_PATH}")
    debug_log(f"App data directory: {APP_DATA_DIR}")
    
    # Ensure the data directory exists
    debug_log("Ensuring data directory exists...")
    os.makedirs(APP_DATA_DIR, exist_ok=True)
    
    if not os.path.exists(CONFIG_FILE_PATH):
        debug_log("No config file found, creating new one with default settings...")
        default_config = get_default_config()
        save_config(default_config)
        debug_log("Default config created and saved")
        return default_config
    
    try:
        debug_log("Reading config file...")
        with open(CONFIG_FILE_PATH, 'r') as f:
            config = json.load(f)
        debug_log(f"Config file loaded successfully")
        debug_log(f"Config keys: {list(config.keys())}")
        
        # Check if migration from old encryption is needed
        debug_log("Checking migration status...")
        if not config.get("_migrated_to_machine_key", False):
            debug_log("Migration flag not set, checking for old encryption...")
            if is_old_encryption(config):
                debug_log("Old encryption detected, performing migration...")
                # Perform one-time migration
                config = migrate_old_keys(config)
                debug_log("Saving migrated config...")
                save_config(config)
                debug_log("Migration complete and saved")
            else:
                debug_log("No old encryption detected, marking as migrated")
                config["_migrated_to_machine_key"] = True
                save_config(config)
        else:
            debug_log("Migration already completed (flag set)")
        
        # STEP 1 NEW: Check if migration from MAC-based to file-based key is needed
        if config.get("_migrated_to_machine_key", False) and not config.get("_migrated_to_file_key", False):
            debug_log("Detected MAC-based encrypted keys, need migration to file-based encryption")
            print("=" * 60)
            print("[MIGRATION] MAC-based encryption detected")
            print("[MIGRATION] API keys need to be re-encrypted with stable file-based key")
            print("[MIGRATION] This is a one-time operation to fix MAC address instability")
            print("=" * 60)
            print("[ACTION REQUIRED] Please re-enter your API keys in Settings")
            print("  1. Open Settings tab")
            print("  2. Enter your OpenAI, Anthropic, and Google API keys")
            print("  3. Click 'Save API Keys'")
            print("=" * 60)
            
            # Clear old MAC-based encrypted keys
            debug_log("Clearing old MAC-based encrypted keys...")
            config["api_keys"] = {
                "openai": "",
                "anthropic": "",
                "google": ""
            }
            
            # Mark as migrated to file-based key
            config["_migrated_to_file_key"] = True
            debug_log("Setting migration flag: _migrated_to_file_key = True")
            
            # Save updated config
            save_config(config)
            debug_log("Migration flag saved, user needs to re-enter keys")
        elif config.get("_migrated_to_file_key", False):
            debug_log("Already migrated to file-based encryption")
            
            # STEP 2 NEW: Safety check - ensure .encryption_key file exists
            debug_log("Checking if encryption key file exists...")
            if not os.path.exists(ENCRYPTION_KEY_FILE):
                debug_log("WARNING: Migration flag set but encryption key file missing!")
                print("=" * 60)
                print("[REPAIR] Encryption key file missing - creating now...")
                print("=" * 60)
                
                # Proactively create the encryption key file
                try:
                    # Call get_or_create_master_key to trigger file creation
                    master_key = get_or_create_master_key()
                    debug_log(f"Encryption key file created successfully: {ENCRYPTION_KEY_FILE}")
                    print("[REPAIR] ✓ Encryption key file created successfully")
                    print("=" * 60)
                except Exception as e:
                    error_log(f"Failed to create encryption key file: {e}", e)
                    print(f"[REPAIR] ✗ Failed to create encryption key file: {e}")
                    print("=" * 60)
            else:
                debug_log(f"Encryption key file exists: {ENCRYPTION_KEY_FILE}")
        else:
            debug_log("No migration flags set, treating as fresh install")
            config["_migrated_to_file_key"] = True
            save_config(config)
            
            # STEP 2 NEW: Ensure encryption key file is created for fresh installs
            debug_log("Fresh install - ensuring encryption key file exists...")
            try:
                master_key = get_or_create_master_key()
                debug_log("Encryption key file ready for fresh install")
            except Exception as e:
                error_log(f"Failed to create encryption key file on fresh install: {e}", e)
        
        # Ensure all default keys exist in the loaded config
        debug_log("Merging with default config to ensure all keys exist...")
        default_config = get_default_config()
        for key, value in default_config.items():
            if key not in config:
                debug_log(f"Adding missing key: {key}")
                config[key] = value
        for sub_key, sub_value in default_config["api_keys"].items():
            if sub_key not in config["api_keys"]:
                debug_log(f"Adding missing API key: {sub_key}")
                config["api_keys"][sub_key] = sub_value
        
        debug_log("Config loaded successfully")
        debug_log("=" * 60)
        return config
        
    except json.JSONDecodeError as e:
        error_log(f"JSON decode error in config file: {e}", e)
        debug_log("Reverting to default settings due to JSON error")
        return get_default_config()
    except Exception as e:
        error_log(f"Unexpected error loading config file: {e}", e)
        debug_log("Reverting to default settings due to error")
        return get_default_config()

def save_config(config: dict):
    """Saves the configuration dictionary to the JSON file."""
    debug_log("=" * 60)
    debug_log("save_config() called")
    debug_log(f"Config keys to save: {list(config.keys())}")
    
    # Log API key status (safely)
    debug_log("API keys status:")
    for key_name, encrypted_value in config.get("api_keys", {}).items():
        if encrypted_value:
            debug_log(f"  {key_name}: {mask_sensitive(encrypted_value, 8)}")
        else:
            debug_log(f"  {key_name}: <empty>")
    
    try:
        debug_log("Ensuring data directory exists...")
        os.makedirs(APP_DATA_DIR, exist_ok=True)
        
        debug_log(f"Writing config to: {CONFIG_FILE_PATH}")
        with open(CONFIG_FILE_PATH, 'w') as f:
            json.dump(config, f, indent=4)
        
        debug_log("Config file written successfully")
        
        # Verify the write
        debug_log("Verifying write by reading back...")
        with open(CONFIG_FILE_PATH, 'r') as f:
            verification = json.load(f)
        
        # Check API keys were actually saved
        for key_name in ["openai", "anthropic", "google"]:
            saved_value = verification.get("api_keys", {}).get(key_name, "")
            original_value = config.get("api_keys", {}).get(key_name, "")
            if saved_value == original_value:
                debug_log(f"Verification: {key_name} saved correctly")
            else:
                error_log(f"Verification FAILED: {key_name} mismatch!")
                error_log(f"  Expected: {mask_sensitive(original_value, 8)}")
                error_log(f"  Got: {mask_sensitive(saved_value, 8)}")
        
        debug_log("Save operation completed successfully")
        debug_log("=" * 60)
        
    except Exception as e:
        error_log(f"Error saving config file: {e}", e)
        debug_log("=" * 60)
        raise