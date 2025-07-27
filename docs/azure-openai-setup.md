# Azure OpenAI Setup Guide for MindTube

This guide explains how to configure MindTube to use Azure OpenAI instead of the standard OpenAI API.

## Prerequisites

1. **Azure Subscription**: You need an active Azure subscription
2. **Azure OpenAI Resource**: Create an Azure OpenAI resource in the Azure portal
3. **Model Deployments**: Deploy the required models in your Azure OpenAI resource

## Step 1: Create Azure OpenAI Resource

1. Go to the [Azure Portal](https://portal.azure.com)
2. Click "Create a resource" and search for "OpenAI"
3. Select "Azure OpenAI" and click "Create"
4. Fill in the required information:
   - **Subscription**: Your Azure subscription
   - **Resource Group**: Create new or use existing
   - **Region**: Choose a region that supports Azure OpenAI (e.g., East US, West Europe)
   - **Name**: Choose a unique name for your resource
   - **Pricing Tier**: Select appropriate tier (Standard S0 recommended)

## Step 2: Deploy Models

After creating the resource, you need to deploy the models:

1. Go to your Azure OpenAI resource in the portal
2. Click on "Model deployments" or go to Azure OpenAI Studio
3. Deploy the following models:
   - **gpt-4o-mini**: For map/reduce operations (cost-effective)
   - **gpt-4o**: For final reduction (higher quality)

### Recommended Deployment Names

Use these deployment names to match the default configuration:

- **Deployment Name**: `gpt-4o-mini`
  - **Model**: `gpt-4o-mini`
  - **Version**: Latest available
  - **Tokens per Minute Rate Limit**: 30K (adjust based on needs)

- **Deployment Name**: `gpt-4o` (optional, for higher quality)
  - **Model**: `gpt-4o`
  - **Version**: Latest available
  - **Tokens per Minute Rate Limit**: 10K (adjust based on needs)

## Step 3: Get Configuration Values

From your Azure OpenAI resource, collect these values:

1. **Endpoint**: Found in "Keys and Endpoint" section
   - Format: `https://your-resource-name.openai.azure.com`

2. **API Key**: Found in "Keys and Endpoint" section
   - Use either Key 1 or Key 2

3. **API Version**: Use `2024-02-01` (recommended)

## Step 4: Configure MindTube

### Environment Variables

Set these environment variables in your `.env` file:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_API_VERSION=2024-02-01

# Model Configuration (use your deployment names)
DEFAULT_MAP_MODEL=gpt-4o-mini
DEFAULT_REDUCE_MODEL=gpt-4o-mini
```

### Example .env Configuration

```bash
# Azure OpenAI API (primary LLM provider)
AZURE_OPENAI_ENDPOINT=https://mindtube-openai.openai.azure.com
AZURE_OPENAI_API_KEY=abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
AZURE_OPENAI_API_VERSION=2024-02-01

# LLM Configuration (Azure deployment names)
DEFAULT_MAP_MODEL=gpt-4o-mini
DEFAULT_REDUCE_MODEL=gpt-4o-mini
MAX_TOKENS_PER_REQUEST=4000
TEMPERATURE=0.1
```

## Step 5: Test the Configuration

Run the test script to verify your Azure OpenAI setup:

```bash
cd backend
python3 tmp_rovodev_test_azure_openai.py
```

Expected output:
```
🧪 Testing Azure OpenAI Integration
==================================================

📋 Checking Configuration:
  Endpoint: https://your-resource-name.openai.azure.com
  API Key: ✅ Set
  API Version: 2024-02-01

🔧 Initializing Azure OpenAI Client...
✅ Client initialized successfully

🔢 Testing token counting...
✅ Token count for test text: 12

📝 Testing summary generation...
✅ Generated summary: This sample covers machine learning fundamentals including supervised...

🎯 Testing summarization service...
✅ Short summary generated: 3 points
    1. This tutorial covers machine learning fundamentals
    2. Supervised learning uses labeled data for predictions
    3. Practice with real datasets to build skills

🎉 All tests passed! Azure OpenAI integration is working correctly.
```

## Step 6: Update Dependencies

Make sure you have the required dependencies installed:

```bash
cd backend
pip install openai tiktoken python-dotenv
```

## Troubleshooting

### Common Issues

1. **Authentication Error**
   - Verify your API key is correct
   - Check that your Azure OpenAI resource is active
   - Ensure you're using the correct endpoint URL

2. **Model Not Found Error**
   - Verify your deployment names match the configuration
   - Check that models are successfully deployed in Azure OpenAI Studio
   - Ensure the models have sufficient quota allocated

3. **Rate Limit Errors**
   - Increase the tokens per minute limit for your deployments
   - Implement retry logic with exponential backoff
   - Consider using multiple deployments for load balancing

4. **Region/Quota Issues**
   - Some regions have limited model availability
   - Check Azure OpenAI service availability in your region
   - Request quota increases if needed

### Debugging Tips

1. **Enable Detailed Logging**
   ```bash
   export OPENAI_LOG=debug
   ```

2. **Check Azure OpenAI Studio**
   - Use the playground to test your deployments
   - Monitor usage and quotas
   - Review deployment logs

3. **Test with Minimal Example**
   ```python
   from openai import AzureOpenAI
   
   client = AzureOpenAI(
       azure_endpoint="https://your-resource.openai.azure.com",
       api_key="your-api-key",
       api_version="2024-02-01"
   )
   
   response = client.chat.completions.create(
       model="gpt-4o-mini",  # your deployment name
       messages=[{"role": "user", "content": "Hello!"}]
   )
   print(response.choices[0].message.content)
   ```

## Cost Optimization

### Model Selection
- Use `gpt-4o-mini` for most operations (cost-effective)
- Reserve `gpt-4o` for final summary generation only
- Consider `gpt-35-turbo` for even lower costs

### Token Management
- Implement chunking to stay within token limits
- Monitor token usage in Azure portal
- Set up billing alerts

### Rate Limiting
- Implement proper rate limiting in your application
- Use exponential backoff for retries
- Consider request queuing for high-volume scenarios

## Security Best Practices

1. **API Key Management**
   - Store API keys in environment variables, not code
   - Rotate keys regularly
   - Use Azure Key Vault for production deployments

2. **Network Security**
   - Configure network access restrictions if needed
   - Use private endpoints for enhanced security
   - Monitor access logs

3. **Content Filtering**
   - Azure OpenAI includes built-in content filtering
   - Configure appropriate filter levels for your use case
   - Monitor filtered requests

## Production Considerations

1. **High Availability**
   - Deploy across multiple regions
   - Implement failover mechanisms
   - Monitor service health

2. **Monitoring**
   - Set up Azure Monitor alerts
   - Track usage metrics and costs
   - Monitor error rates and latency

3. **Scaling**
   - Plan for quota increases
   - Consider multiple deployments for load distribution
   - Implement proper caching strategies

## Support Resources

- [Azure OpenAI Documentation](https://docs.microsoft.com/azure/cognitive-services/openai/)
- [Azure OpenAI Studio](https://oai.azure.com/)
- [OpenAI Python Library Documentation](https://github.com/openai/openai-python)
- [Azure Support](https://azure.microsoft.com/support/)