from src.ai_companion.modules.image import TextToImage, ImageToText
from src.ai_companion.core.exceptions import TextToImageError, ImageToTextError

async def main():
    # Set your Google API Key (ensure it's configured in your environment or settings)
    # os.environ["GOOGLE_API_KEY"] = "YOUR_ACTUAL_GOOGLE_API_KEY" # Uncomment and set if not using a settings file

    tti = TextToImage() 
    itt = ImageToText()

    # Test Image Generation
    try:
        image_prompt = "A majestic lion standing on a rock overlooking a vast savannah at sunset, photorealistic, cinematic lighting."
        # Generate and resize to 800x600
        image_data_bytes = await tti.generate_image(
            prompt=image_prompt,
            output_path="generated_lion.png",
            width=800,
            height=600
        )
        print(f"\nGenerated and resized image (800x600). Size: {len(image_data_bytes)} bytes")
        # Display the image
        from IPython.display import Image, display
        display(Image(data=image_data_bytes, width=800))

        # Test another size
        # image_data_bytes_small = await tti.generate_image(
        #     prompt="A whimsical treehouse with glowing windows in a magical forest.",
        #     output_path="treehouse_small.png",
        #     width=400,
        #     height=300
        # )
        # print(f"\nGenerated and resized image (400x300). Size: {len(image_data_bytes_small)} bytes")
        # display(Image(data=image_data_bytes_small, width=400))

        # Test Image Analysis
        image_analysis = await itt.analyze_image(image_data_bytes)
        print(f"\nImage Analysis: {image_analysis}")

    except ImageToTextError as e:
        print(f"Error generating image: {e}")
    except TextToImageError as e:
        print(f"Error generating image: {e}")
    except ValueError as e:
        print(f"Configuration error: {e}")

# This will run the async main function
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
