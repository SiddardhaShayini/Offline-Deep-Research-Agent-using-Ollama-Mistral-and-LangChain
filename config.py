"""Configuration and Settings Module.

Centralized configuration for the research system.
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
import json


@dataclass
class OllamaConfig:
    """Configuration for Ollama connection."""
    base_url: str = "http://localhost:11434"
    model: str = "mistral"
    temperature: float = 0.3
    num_ctx: int = 4096  # Context window size
    num_predict: int = 512  # Max tokens to generate
    top_k: int = 40
    top_p: float = 0.9
    repeat_penalty: float = 1.1


@dataclass
class ResearchConfig:
    """Configuration for research parameters."""
    max_searches: int = 5
    max_iterations: int = 6
    search_timeout: int = 30
    include_metadata: bool = True
    export_format: str = "markdown"  # markdown, json, html


@dataclass
class KnowledgeBaseConfig:
    """Configuration for knowledge base."""
    use_vectors: bool = True
    embedding_model: str = "nomic-embed-text"
    search_type: str = "hybrid"  # keyword, vector, hybrid
    max_results: int = 3
    chunk_size: int = 1000
    chunk_overlap: int = 200


@dataclass
class SystemConfig:
    """System-wide configuration."""
    debug: bool = False
    log_level: str = "INFO"
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 1 hour
    concurrent_workers: int = 3
    enable_streaming: bool = True


class Config:
    """Main configuration manager."""
    
    def __init__(self):
        self.ollama = OllamaConfig()
        self.research = ResearchConfig()
        self.knowledge_base = KnowledgeBaseConfig()
        self.system = SystemConfig()
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Load configuration from environment variables."""
        config = cls()
        
        # Ollama settings
        config.ollama.base_url = os.getenv('OLLAMA_BASE_URL', config.ollama.base_url)
        config.ollama.model = os.getenv('OLLAMA_MODEL', config.ollama.model)
        config.ollama.temperature = float(os.getenv('OLLAMA_TEMPERATURE', config.ollama.temperature))
        
        # Research settings
        config.research.max_searches = int(os.getenv('MAX_SEARCHES', config.research.max_searches))
        config.research.max_iterations = int(os.getenv('MAX_ITERATIONS', config.research.max_iterations))
        config.research.export_format = os.getenv('EXPORT_FORMAT', config.research.export_format)
        
        # Knowledge base settings
        config.knowledge_base.use_vectors = os.getenv('USE_VECTORS', 'true').lower() == 'true'
        config.knowledge_base.search_type = os.getenv('SEARCH_TYPE', config.knowledge_base.search_type)
        
        # System settings
        config.system.debug = os.getenv('DEBUG', 'false').lower() == 'true'
        config.system.log_level = os.getenv('LOG_LEVEL', config.system.log_level)
        
        return config
    
    @classmethod
    def from_file(cls, filepath: str) -> 'Config':
        """Load configuration from JSON file."""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            config = cls()
            
            # Update from loaded data
            if 'ollama' in data:
                for key, value in data['ollama'].items():
                    setattr(config.ollama, key, value)
            
            if 'research' in data:
                for key, value in data['research'].items():
                    setattr(config.research, key, value)
            
            if 'knowledge_base' in data:
                for key, value in data['knowledge_base'].items():
                    setattr(config.knowledge_base, key, value)
            
            if 'system' in data:
                for key, value in data['system'].items():
                    setattr(config.system, key, value)
            
            return config
        except Exception as e:
            print(f"Error loading config from {filepath}: {e}")
            return cls()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'ollama': asdict(self.ollama),
            'research': asdict(self.research),
            'knowledge_base': asdict(self.knowledge_base),
            'system': asdict(self.system),
        }
    
    def save_to_file(self, filepath: str) -> bool:
        """Save configuration to JSON file."""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config to {filepath}: {e}")
            return False
    
    def __str__(self) -> str:
        """String representation of configuration."""
        return json.dumps(self.to_dict(), indent=2)


# Global configuration instance
config = Config.from_env()


# ===== PRESET CONFIGURATIONS =====

def get_fast_config() -> Config:
    """Configuration optimized for speed."""
    config = Config()
    config.ollama.temperature = 0.1
    config.ollama.num_ctx = 2048
    config.ollama.num_predict = 256
    config.research.max_searches = 2
    config.knowledge_base.search_type = "keyword"  # Faster than vector
    return config


def get_quality_config() -> Config:
    """Configuration optimized for quality."""
    config = Config()
    config.ollama.temperature = 0.5
    config.ollama.num_ctx = 4096
    config.ollama.num_predict = 1024
    config.research.max_searches = 5
    config.knowledge_base.search_type = "hybrid"  # Best quality
    return config


def get_balanced_config() -> Config:
    """Balanced configuration (default)."""
    return Config()


def get_minimal_config() -> Config:
    """Minimal configuration for low-resource environments."""
    config = Config()
    config.ollama.model = "mistral"  # Smallest capable model
    config.ollama.temperature = 0.1
    config.ollama.num_ctx = 2048
    config.ollama.num_predict = 128
    config.research.max_searches = 1
    config.knowledge_base.use_vectors = False
    config.knowledge_base.search_type = "keyword"
    config.system.cache_enabled = True
    return config


if __name__ == "__main__":
    print("Configuration Examples:\n")
    
    print("1. Default configuration:")
    print(get_balanced_config())
    print("\n" + "="*50 + "\n")
    
    print("2. Fast configuration:")
    print(get_fast_config())
    print("\n" + "="*50 + "\n")
    
    print("3. Quality configuration:")
    print(get_quality_config())
    print("\n" + "="*50 + "\n")
    
    print("4. Minimal configuration:")
    print(get_minimal_config())