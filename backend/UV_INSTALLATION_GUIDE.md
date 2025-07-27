# Using UV to Install Azure OpenAI Dependencies

This guide shows how to use `uv` (the fast Python package installer) to install the new Azure OpenAI dependencies for MindTube.

## What is UV?

`uv` is a fast Python package installer and resolver written in Rust. It's significantly faster than pip and provides better dependency resolution.

## Installing UV

If you don't have `uv` installed yet:

```bash
# Install uv using pip
pip install uv

# Or install using curl (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using homebrew (macOS)
brew install uv
```

## Installing Azure OpenAI Dependencies

### Option 1: Install Specific Packages

Install just the new Azure OpenAI packages:

```bash
cd backend

# Install the updated OpenAI library with Azure support
uv add openai==1.54.3

# Install tiktoken for token counting
uv add tiktoken==0.8.0
```

### Option 2: Install from Requirements Files

Install all dependencies from the updated requirements files:

```bash
cd backend

# Install from full requirements.txt
uv pip install -r requirements.txt

# Or install from simplified requirements (for development)
uv pip install -r requirements-simple.txt
```

### Option 3: Install from pyproject.toml

If you prefer using the pyproject.toml configuration:

```bash
cd backend

# Install all dependencies including optional dev dependencies
uv pip install -e ".[dev]"

# Or install just the main dependencies
uv pip install -e .
```

## Creating a Virtual Environment with UV

UV can also manage virtual environments:

```bash
cd backend

# Create a new virtual environment
uv venv

# Activate the virtual environment
source .venv/bin/activate  # On Linux/macOS
# or
.venv\Scripts\activate     # On Windows

# Install dependencies in the virtual environment
uv pip install -r requirements.txt
```

## Upgrading Existing Installation

If you already have the old OpenAI package installed:

```bash
cd backend

# Upgrade to the new version with Azure support
uv pip install --upgrade openai==1.54.3 tiktoken==0.8.0

# Or upgrade all packages
uv pip install --upgrade -r requirements.txt
```

## Verifying Installation

After installation, verify that the packages are correctly installed:

```bash
# Check installed versions
uv pip list | grep -E "(openai|tiktoken)"

# Or use Python to check
python3 -c "
import openai
import tiktoken
print(f'OpenAI version: {openai.__version__}')
print(f'Tiktoken version: {tiktoken.__version__}')
print('✅ Azure OpenAI dependencies installed successfully!')
"
```

Expected output:
```
OpenAI version: 1.54.3
Tiktoken version: 0.8.0
✅ Azure OpenAI dependencies installed successfully!
```

## Testing Azure OpenAI Integration

After installing the dependencies, test the Azure OpenAI integration:

```bash
cd backend

# Test import and basic functionality
python3 -c "
try:
    from openai import AzureOpenAI
    print('✅ AzureOpenAI client imported successfully')
    
    from app.services.llm_client import AzureOpenAIClient
    from app.services.summarization import SummarizationService
    print('✅ MindTube Azure OpenAI services imported successfully')
    print('🎉 Ready to use Azure OpenAI!')
except ImportError as e:
    print(f'❌ Import error: {e}')
except Exception as e:
    print(f'⚠️  Configuration needed: {e}')
"
```

## UV Performance Benefits

UV is significantly faster than pip:

```bash
# Benchmark: Install all dependencies
time uv pip install -r requirements.txt
# vs
time pip install -r requirements.txt

# UV is typically 10-100x faster than pip
```

## UV Commands Cheat Sheet

```bash
# Install a package
uv add package-name

# Install from requirements file
uv pip install -r requirements.txt

# Install in development mode
uv pip install -e .

# Upgrade a package
uv pip install --upgrade package-name

# List installed packages
uv pip list

# Show package information
uv pip show package-name

# Create virtual environment
uv venv

# Install with specific Python version
uv venv --python 3.11

# Sync dependencies (install exact versions from lock file)
uv pip sync requirements.txt
```

## Troubleshooting

### Common Issues

1. **UV not found**
   ```bash
   # Make sure uv is in your PATH
   which uv
   # If not found, reinstall uv
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Permission errors**
   ```bash
   # Use virtual environment instead of system Python
   uv venv
   source .venv/bin/activate
   uv pip install -r requirements.txt
   ```

3. **Package conflicts**
   ```bash
   # UV has better dependency resolution, but if issues persist:
   uv pip install --force-reinstall -r requirements.txt
   ```

4. **Old OpenAI version cached**
   ```bash
   # Clear UV cache
   uv cache clean
   # Reinstall
   uv pip install --no-cache-dir openai==1.54.3
   ```

## Next Steps

After installing the dependencies:

1. **Configure Azure OpenAI**: Set up your Azure OpenAI resource and get credentials
2. **Update Environment**: Add Azure OpenAI configuration to your `.env` file
3. **Test Integration**: Run the test scripts to verify everything works
4. **Deploy**: Your application is now ready to use Azure OpenAI!

## Additional Resources

- [UV Documentation](https://docs.astral.sh/uv/)
- [Azure OpenAI Setup Guide](./docs/azure-openai-setup.md)
- [OpenAI Python Library](https://github.com/openai/openai-python)
- [Tiktoken Documentation](https://github.com/openai/tiktoken)