import moviepy.editor as mp
import speech_recognition as sr
from pydub import AudioSegment
import os

def video_to_text(video_path):
    """
    Extract audio from video and convert speech to text.
    
    Args:
        video_path (str): Path to the video file
        
    Returns:
        str: Transcribed text from the video
    """
    try:
        # Extract audio from video
        video = mp.VideoFileClip(video_path)
        audio = video.audio
        
        # Save audio as WAV file temporarily
        temp_audio_path = "temp_audio.wav"
        audio.write_audiofile(temp_audio_path)
        video.close()
        
        # Initialize recognizer
        recognizer = sr.Recognizer()
        
        # Load audio file
        with sr.AudioFile(temp_audio_path) as audio_file:
            # Read the audio data
            audio_data = recognizer.record(audio_file)
            
            # Convert speech to text using Google's free speech recognition
            text = recognizer.recognize_google(audio_data)
            
        # Clean up temporary file
        os.remove(temp_audio_path)
        
        return text
        
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Example usage
if __name__ == "__main__":
    video_file = "video.mp4"  # Replace with your video path
    transcribed_text = video_to_text(video_file)
    print("Transcribed Text:")
    print(transcribed_text)