import asyncio
from litellm import acompletion
from openai import OpenAIError

# Frontier models mapping
FRONTIER_MODELS = {
    "gpt-4o": "gpt-4o",
    "o3": "o3",
    "o3-mini": "o3-mini",
    "claude-opus-4": "anthropic/claude-opus-4-20250514",
    "gemini-2.5-flash-preview": "gemini/gemini-2.5-flash-preview-05-20",
    "gemini-2.5-pro-preview": "gemini/gemini-2.5-pro-preview-06-05",
}

# Set up your API keys
# os.environ["OPENAI_API_KEY"] = "your-openai-api-key"
# os.environ["ANTHROPIC_API_KEY"] = "your-anthropic-api-key"
# os.environ["GOOGLE_API_KEY"] = "your-google-api-key"


def handle_response(response, max_tokens, model_id):
    # Handle truncation - return partial content with truncation notice
    print(f"Tokens: {response.usage.total_tokens}")
    finish_reason = response.choices[0].finish_reason
    content = response.choices[0].message.content
    if finish_reason == "length" and content:
        # Return the partial content with a note that it was truncated
        truncation_note = f"\n\n[Note: Response was truncated at {max_tokens} tokens due to length limit]"
        print(content + truncation_note)
        return
    elif finish_reason == "length" and not content:
        # If somehow we have no content but finish_reason is length
        print(
            f"Hit max tokens limit. Response was truncated at {max_tokens} tokens for {model_id}."
        )
        return
    print(content)


async def basic_async_call_example():
    """Basic async completion call example"""
    try:
        model_id = "gpt-4o"
        response = await acompletion(
            model=FRONTIER_MODELS[model_id],
            messages=[{"role": "user", "content": "Hello, how are you?"}],
            drop_params=True,
        )
        print(f"\nModel used: {response.model}")
        print("-" * 50)
        handle_response(response, 100, model_id)
        return response
    except OpenAIError as e:
        print(f"Error in basic call: {e}")
        return None


async def multiple_models_example():
    """Example calling multiple frontier models concurrently"""
    # Create tasks for different models
    models_to_test = ["gpt-4o", "o3-mini", "gemini-2.5-flash-preview"]

    # Create coroutines for each model
    async def call_model(model_key):
        try:
            response = await acompletion(
                model=FRONTIER_MODELS[model_key],
                messages=[
                    {
                        "role": "user",
                        "content": f"Explain quantum computing in one sentence using the perspective of {model_key}",
                    }
                ],
                drop_params=True,
            )
            print(f"Model used: {response.model}")
            print("-" * 50)
            handle_response(response, None, model_key)
        except Exception as e:
            print(f"Error with {model_key}: {e}")

    print("Calling multiple models concurrently...")

    # Run all tasks in parallel
    tasks = [call_model(model_key) for model_key in models_to_test]
    await asyncio.gather(*tasks)


async def advanced_parameters_example():
    """Example with advanced parameters"""
    try:
        response = await acompletion(
            model=FRONTIER_MODELS["gemini-2.5-pro-preview"],
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant specializing in technology.",
                },
                {
                    "role": "user",
                    "content": "Explain the benefits of async programming",
                },
            ],
            temperature=0.7,
            max_tokens=200,
            top_p=0.9,
            presence_penalty=0.1,
            frequency_penalty=0.1,
            drop_params=True,
        )

        handle_response(response, 200, "gemini-2.5-pro-preview")

    except OpenAIError as e:
        print(f"Error in advanced call: {e}")


async def compare_models_example():
    """Compare responses from different frontier models"""
    prompt = "Explain the concept of artificial intelligence in 50 words"
    max_tokens = 75

    print("Comparing responses from different models:")
    print("=" * 50)

    # Create coroutines for each model
    async def call_model_for_comparison(model_name, model_id):
        try:
            response = await acompletion(
                model=model_id,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                drop_params=True,
            )
            return model_name, response, None
        except Exception as e:
            return model_name, None, e

    # Run all models in parallel
    tasks = [
        call_model_for_comparison(model_name, model_id)
        for model_name, model_id in FRONTIER_MODELS.items()
    ]
    results = await asyncio.gather(*tasks)

    # Process and display results
    for model_name, response, error in results:
        if error:
            print(f"\n{model_name.upper()}: Error - {error}")
        else:
            print(f"\n{model_name.upper()}:")
            print("-" * 20)
            handle_response(response, max_tokens, model_name)


async def main():
    """Main function to run all examples"""
    print("LiteLLM Async Examples with Frontier Models")
    print("=" * 50)

    # Run examples
    await basic_async_call_example()
    print("\n" + "=" * 50)

    await multiple_models_example()
    print("\n" + "=" * 50)

    await advanced_parameters_example()
    print("\n" + "=" * 50)

    await compare_models_example()
    print("\n" + "=" * 50)


if __name__ == "__main__":
    # Run the async examples
    asyncio.run(main())
