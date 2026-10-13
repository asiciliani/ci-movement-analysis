import argparse
import os
import time
import json
from google import genai
from google.genai import types

def analyze_video_with_llm(video_path, output_path):
    print(f"Initializing Gemini client...")
    # Initialize the client. Assumes GOOGLE_API_KEY is in the environment.
    try:
        client = genai.Client()
    except Exception as e:
        print(f"Error initializing client (is GOOGLE_API_KEY set?): {e}")
        return

    print(f"Uploading video {video_path} to Gemini...")
    video_file = client.files.upload(file=video_path)
    
    print(f"Waiting for video processing to complete...")
    # Poll until the file is ready
    while True:
        file_info = client.files.get(name=video_file.name)
        if file_info.state.name == "ACTIVE":
            break
        elif file_info.state.name == "FAILED":
            print(f"Video processing failed.")
            return
        time.sleep(5)
    
    print(f"Video ready. Requesting interpretation...")
    
    prompt = """
    You are an expert in Contact Improvisation, biomechanics, and kinesthetic empathy.
    Watch this video carefully and provide a semantic interpretation of the physical interaction.
    
    Focus on:
    1. **Weight Sharing:** Who is bearing the weight? Is the 'Yield' mutual or one-sided?
    2. **State Classification:** Is the duet currently in a state of 'Survival Biomechanics' (focusing purely on physical safety, support, and reflexes) or 'Artistic Expression' (intentional gestures, breaking physical necessity for aesthetics)?
    3. **Leadership and Lag:** Is there a clear leader dictating the momentum? How does the follower adapt (immediate response vs delayed resolution)?
    4. **Safety & Empathy:** How is the physical safety managed? Are there sudden spikes in movement (Jerk), or is the kinetic energy absorbed smoothly? Note if there are extreme asymmetries (e.g. an adult and a baby, or drastically different sizes).
    
    Format the output as a clean, structured JSON object with keys: 
    "weight_sharing", "state_classification", "leadership_dynamics", "safety_and_empathy", and "overall_summary".
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-pro',
        contents=[
            video_file,
            prompt
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2,
        )
    )
    
    print("Interpretation received. Saving to output...")
    try:
        data = json.loads(response.text)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Successfully saved interpretation to {output_path}")
    except Exception as e:
        print("Failed to parse JSON response. Saving raw text instead.")
        with open(output_path.replace('.json', '.txt'), "w", encoding="utf-8") as f:
            f.write(response.text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LLM Video Interpreter for Contact Improvisation")
    parser.add_argument("--video", type=str, required=True, help="Path to the video file")
    parser.add_argument("--output", type=str, required=True, help="Path to save the JSON output")
    args = parser.parse_args()
    
    analyze_video_with_llm(args.video, args.output)
