import requests
import json
import time
import sys
from config_local import OLLAMA_API_URL, MODEL_NAME

class LLMHandler:
    def __init__(self):
        self.api_url = OLLAMA_API_URL
        self.model = MODEL_NAME
        self._verify_ollama_connection()

    def _verify_ollama_connection(self):
        """Verify that Ollama is running and accessible"""
        try:
            response = requests.get("http://127.0.0.1:11434")
            if response.status_code == 200:
                print("✅ Successfully connected to Ollama")
            else:
                print(f"⚠️  Warning: Ollama returned status code {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to Ollama. Please ensure it's running with:")
            print("   ollama serve")
            raise ConnectionError("Ollama service not accessible")

    def _is_incomplete_response(self, text):
        """Check if response seems incomplete"""
        incomplete_markers = ['<think>', '<thinking>', '...', 'Let me think']
        return any(marker in text for marker in incomplete_markers) or len(text) < 20

    def generate_response(self, prompt):
        """Generate response from Ollama API using streaming to ensure completion"""
        try:
            # Append instruction for concise answer
            enhanced_prompt = f"{prompt}\n[Instruction: Please provide a clear and concise answer, focusing on the key points.]"
            
            data = {
                "model": self.model,
                "prompt": enhanced_prompt,
                "stream": True,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 2000,
                    "top_k": 40,
                    "top_p": 0.9,
                }
            }
            
            print("\n🤔 Starting LLM processing...")
            start_time = time.time()
            
            response = requests.post(self.api_url, json=data, stream=True)
            
            if response.status_code == 404:
                print(f"❌ Model '{self.model}' not found. Try running:")
                print(f"   ollama pull {self.model}")
                return "I'm sorry, but I'm not properly configured yet. Please make sure the model is installed."
            
            response.raise_for_status()
            
            # Process streaming response
            response_parts = []
            current_response_length = 0
            spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
            spinner_idx = 0
            last_update = time.time()
            last_newline = True
            buffer = ""  # Buffer for accumulating partial words/sentences
            
            print("\nReceiving response:")
            
            for line in response.iter_lines():
                if line:
                    try:
                        json_response = json.loads(line)
                        
                        if 'response' in json_response:
                            chunk = json_response['response']
                            current_response_length += len(chunk.split())
                            
                            # Check if we've exceeded 2000 words
                            if current_response_length > 2000:
                                print("\n⚠️  Response exceeded 2000 words, truncating...")
                                break
                            
                            # Accumulate in buffer
                            buffer += chunk
                            
                            # If we have a complete sentence or significant punctuation, flush the buffer
                            if any(p in buffer for p in ['.', '!', '?', '\n', ';']) or len(buffer) > 50:
                                response_parts.append(buffer)
                                
                                # Print the accumulated buffer
                                current_time = time.time()
                                if current_time - last_update >= 0.1:
                                    spinner = spinner_chars[spinner_idx]
                                    spinner_idx = (spinner_idx + 1) % len(spinner_chars)
                                    last_update = current_time
                                    
                                    if last_newline:
                                        print(f"{spinner} {buffer}", end='')
                                        last_newline = False
                                    else:
                                        print(buffer, end='')
                                    
                                    if buffer.endswith('\n'):
                                        last_newline = True
                                    
                                    sys.stdout.flush()
                                buffer = ""
                        
                        # Check if response is complete
                        if json_response.get('done', False):
                            # Flush any remaining buffer
                            if buffer:
                                response_parts.append(buffer)
                                print(buffer, end='')
                            break
                            
                    except json.JSONDecodeError:
                        continue
            
            # Ensure we end with a newline
            if not last_newline:
                print()
                
            elapsed_time = time.time() - start_time
            print(f"\n✨ Response completed in {elapsed_time:.1f} seconds")
            
            # Join all parts with proper spacing
            final_response = ' '.join(''.join(response_parts).split())
            
            return final_response
            
        except requests.exceptions.ConnectionError:
            error_msg = "❌ Connection error. Please ensure Ollama is running with 'ollama serve'"
            print(error_msg)
            return error_msg
        except requests.exceptions.Timeout:
            error_msg = "⏰ Request timed out. The model is taking too long to respond."
            print(error_msg)
            return error_msg
        except requests.exceptions.RequestException as e:
            error_msg = f"❌ Error communicating with Ollama: {str(e)}"
            print(error_msg)
            return error_msg 