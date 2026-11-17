"""
MP4 Video Generator using ffmpeg-python
This script creates an MP4 video from an MP3 audio file, images, and a timeline script.
Supports motion effects: push_in, pull_out, pan_left, pan_right, static
"""

import os  # Import os module for file system operations
import sys  # Import sys module for command line argument handling
import json  # Import json module for parsing timeline configuration files
import ffmpeg  # Import ffmpeg-python wrapper for video processing


OUTPUT_WIDTH = 1080
OUTPUT_HEIGHT = 1920
OUTPUT_FPS = 30


def fit_to_portrait_canvas(video_stream):
    """Scale without stretching, then pad to a 9:16 portrait frame."""
    return (
        video_stream
        .filter(
            'scale',
            OUTPUT_WIDTH,
            OUTPUT_HEIGHT,
            force_original_aspect_ratio='decrease'
        )
        .filter(
            'pad',
            OUTPUT_WIDTH,
            OUTPUT_HEIGHT,
            '(ow-iw)/2',
            '(oh-ih)/2',
            color='black'
        )
        .filter('setsar', 1)
    )


def create_video_from_timeline(audio_file, images_dir, timeline_file, output_file):  # Main function to create MP4 video from audio, images, and timeline
    """
    Create an MP4 video from audio, images, and a timeline script.
    
    Args:
        audio_file (str): Path to the MP3 audio file
        images_dir (str): Directory containing the images
        timeline_file (str): Path to JSON timeline file with scene information
        output_file (str): Path for the output MP4 file
    
    Returns:
        bool: True if video creation successful, False otherwise
    
    Raises:
        FileNotFoundError: If input files don't exist
        Exception: For other conversion errors
    """
    try:  # Start try block for error handling
        # Validate input files  # Comment indicating file validation section
        if not os.path.exists(audio_file):  # Check if audio file exists
            raise FileNotFoundError(f"Audio file '{audio_file}' not found")  # Raise error if audio file missing
        
        if not os.path.exists(images_dir):  # Check if images directory exists
            raise FileNotFoundError(f"Images directory '{images_dir}' not found")  # Raise error if images directory missing
        
        if not os.path.exists(timeline_file):  # Check if timeline file exists
            raise FileNotFoundError(f"Timeline file '{timeline_file}' not found")  # Raise error if timeline file missing
        
        # Load the timeline  # Comment indicating timeline loading section
        with open(timeline_file, 'r', encoding='utf-8') as f:  # Open timeline file with UTF-8 encoding
            timeline = json.load(f)  # Parse JSON content from timeline file
        
        print(f"Loaded timeline from: {timeline_file}")  # Print confirmation of timeline file loaded
        print(f"Audio file: {audio_file}")  # Print audio file path for user confirmation
        print(f"Images directory: {images_dir}")  # Print images directory path for user confirmation
        
        # Validate timeline structure  # Comment indicating timeline validation section
        if 'scenes' not in timeline:  # Check if timeline contains required 'scenes' key
            raise ValueError("Timeline must contain 'scenes' array")  # Raise error if scenes array missing
        
        scenes = timeline['scenes']  # Extract scenes array from timeline dictionary
        if len(scenes) == 0:  # Check if scenes array is empty
            raise ValueError("Timeline must contain at least one scene")  # Raise error if no scenes defined
        
        print(f"Processing {len(scenes)} scenes...")  # Print number of scenes to process
        
        # Create temporary directory for processed segments  # Comment indicating temp directory creation
        temp_dir = 'temp_segments'  # Define temporary directory name
        os.makedirs(temp_dir, exist_ok=True)  # Create temp directory if it doesn't exist
        
        # Process each scene  # Comment indicating scene processing loop
        segment_files = []  # Initialize list to store segment file paths
        for i, scene in enumerate(scenes):  # Iterate through scenes with index
            image_file = scene.get('image')  # Extract image filename from scene data
            start_time = scene.get('start', 0)  # Extract start time, default to 0
            end_time = scene.get('end', 5)  # Extract end time, default to 5
            motion = scene.get('motion', 'static')  # Extract motion type, default to static
            intensity = scene.get('intensity', 0.05)  # Extract motion intensity, default to 0.05
            
            if not image_file:  # Check if image filename is missing
                raise ValueError(f"Scene {i} missing 'image' field")  # Raise error if image field missing
            
            # Calculate duration from start/end times in seconds.
            duration = end_time - start_time
            
            image_path = os.path.join(images_dir, image_file)  # Build full path to image file
            if not os.path.exists(image_path):  # Check if image file exists at specified path
                raise FileNotFoundError(f"Image file '{image_path}' not found")  # Raise error if image file missing
            
            # Create video segment from image  # Comment indicating segment creation
            segment_output = os.path.join(temp_dir, f'segment_{i:03d}.mp4')  # Build output path for segment file
            
            print(f"Creating scene {i+1}/{len(scenes)}: {scene.get('name', image_file)} ({duration:.2f}s, motion: {motion})")  # Print scene creation progress
            
            # Apply motion effects using ffmpeg filters  # Comment indicating motion effect application
            video_input = ffmpeg.input(image_path, loop=1, framerate=OUTPUT_FPS)  # Create ffmpeg input from image with looping and 30fps
            video_input = fit_to_portrait_canvas(video_input)
            
            # Build filter chain based on motion type  # Comment indicating filter chain logic
            if motion == 'push_in':  # Check if motion type is zoom in
                # Zoom in effect  # Comment describing push_in effect
                video_input = video_input.filter('zoompan', 
                    zoom=f"min(zoom+{intensity},1.5)",  # Set zoom parameter to gradually increase
                    d=1,
                    x='iw/2-(iw/zoom/2)',
                    y='ih/2-(ih/zoom/2)',
                    s=f'{OUTPUT_WIDTH}x{OUTPUT_HEIGHT}',
                    fps=OUTPUT_FPS)
            elif motion == 'pull_out':  # Check if motion type is zoom out
                # Zoom out effect  # Comment describing pull_out effect
                video_input = video_input.filter('zoompan',
                    zoom=f"max(zoom-{intensity},1.0)",  # Set zoom parameter to gradually decrease
                    d=1,
                    x='iw/2-(iw/zoom/2)',
                    y='ih/2-(ih/zoom/2)',
                    s=f'{OUTPUT_WIDTH}x{OUTPUT_HEIGHT}',
                    fps=OUTPUT_FPS)
            elif motion == 'pan_left':  # Check if motion type is pan left
                # Pan left effect  # Comment describing pan_left effect
                video_input = video_input.filter('zoompan',
                    zoom=1.0,
                    d=1,
                    x='iw-iw/zoom',  # Set x position to pan from right to left
                    y='ih/2-(ih/zoom/2)',
                    s=f'{OUTPUT_WIDTH}x{OUTPUT_HEIGHT}',
                    fps=OUTPUT_FPS)
            elif motion == 'pan_right':  # Check if motion type is pan right
                # Pan right effect  # Comment describing pan_right effect
                video_input = video_input.filter('zoompan',
                    zoom=1.0,
                    d=1,
                    x='0',  # Set x position to pan from left to right
                    y='ih/2-(ih/zoom/2)',
                    s=f'{OUTPUT_WIDTH}x{OUTPUT_HEIGHT}',
                    fps=OUTPUT_FPS)
            else:
                video_input = video_input.filter('fps', fps=OUTPUT_FPS)
            
            # Output the segment  # Comment indicating segment output generation
            (  # Start ffmpeg output chain
                video_input
                .output(segment_output,  # Set output file path
                       vcodec='libx264',  # Use H.264 video codec
                       pix_fmt='yuv420p',  # Use YUV420P pixel format for compatibility
                       t=duration,  # Set video duration
                       crf=23,  # Set constant rate factor for quality (lower = better)
                       preset='medium')  # Use medium encoding preset for balance of speed/quality
                .overwrite_output()  # Overwrite output file if it exists
                .run(quiet=True)  # Execute ffmpeg command quietly
            )  # End ffmpeg output chain
            
            segment_files.append(segment_output)  # Add segment file path to list
        
        print("Concatenating segments...")  # Print concatenation progress message
        
        # Create concat file for ffmpeg  # Comment indicating concat file creation
        concat_file = os.path.join(temp_dir, 'concat.txt')  # Build path for concat configuration file
        with open(concat_file, 'w') as f:  # Open concat file for writing
            for segment_file in segment_files:  # Iterate through segment files
                f.write(f"file '{os.path.abspath(segment_file)}'\n")  # Write each segment file path to concat file
        
        # Concatenate all video segments  # Comment indicating concatenation process
        video_output = os.path.join(temp_dir, 'video_only.mp4')  # Build path for concatenated video file
        (
            ffmpeg
            .input(concat_file, format='concat', safe=0)  # Input concat file with concat format
            .output(video_output,  # Set output file path
                   vcodec='libx264',
                   pix_fmt='yuv420p',
                   crf=23,
                   preset='medium')
            .overwrite_output()
            .run(quiet=True)
        )
        
        print("Adding audio...")  # Print audio addition progress message
        
        # Combine video with audio  # Comment indicating audio combination process
        video_input = ffmpeg.input(video_output)  # Input concatenated video file
        audio_input = ffmpeg.input(audio_file)  # Input audio file
        
        # Get audio duration  # Comment indicating audio duration retrieval
        audio_probe = ffmpeg.probe(audio_file)  # Probe audio file for metadata
        audio_duration = float(audio_probe['format']['duration'])  # Extract audio duration in seconds
        
        # Loop video if shorter than audio, or trim if longer  # Comment indicating duration matching logic
        video_duration = float(ffmpeg.probe(video_output)['format']['duration'])  # Extract video duration in seconds
        
        if video_duration < audio_duration:  # Check if video is shorter than audio
            # Loop video to match audio duration  # Comment indicating video looping
            loop_count = int(audio_duration / video_duration) + 1  # Calculate how many times to loop video
            video_input = ffmpeg.concat(*[video_input] * loop_count, v=1, a=0)  # Concatenate video with itself to loop
        
        # Combine video and audio  # Comment indicating final combination
        (
            ffmpeg
            .output(video_input, audio_input, output_file,  # Combine video and audio to output file
                   vcodec='libx264',
                   acodec='aac',  # Use AAC audio codec
                   audio_bitrate='192k',  # Set audio bitrate to 192kbps
                   pix_fmt='yuv420p',
                   shortest=None,  # Don't trim to shortest input
                   preset='medium')
            .overwrite_output()
            .run(quiet=True)
        )
        
        # Clean up temporary files  # Comment indicating cleanup section
        print("Cleaning up temporary files...")  # Print cleanup progress message
        for segment_file in segment_files:
            os.remove(segment_file)  # Delete each segment file
        os.remove(concat_file)  # Delete concat configuration file
        os.remove(video_output)  # Delete concatenated video file
        os.rmdir(temp_dir)  # Remove temporary directory
        
        print(f"Successfully created video: {output_file}")  # Print success message with output file path
        return True  # Return True to indicate success
        
    except FileNotFoundError as e:  # Catch file not found errors
        print(f"Error: {e}")
        return False
    except ValueError as e:  # Catch value errors
        print(f"Error: {e}")
        return False
    except Exception as e:  # Catch any other exceptions
        print(f"An error occurred during video creation: {e}")  # Print error message
        return False


def main():  # Main entry point for command line execution
    """
    Main function to handle command line arguments and execute video creation.
    """
    if len(sys.argv) < 4:  # Check if minimum arguments provided
        print("Usage: python create_mp4.py <audio_file> <images_dir> <timeline_file> [output_file]")  # Print usage instructions
        print("Example: python create_mp4.py audio.mp3 images/ video-timeline.json output.mp4")  # Print example usage
        print("The timeline file should contain a 'scenes' array with image, start, end, motion, and intensity fields.")  # Print timeline format description
        sys.exit(1)  # Exit with error code
    
    # Parse arguments  # Comment indicating argument parsing section
    audio_file = sys.argv[1]  # Get audio file path from first argument
    images_dir = sys.argv[2]  # Get images directory path from second argument
    timeline_file = sys.argv[3]  # Get timeline file path from third argument
    output_file = sys.argv[4] if len(sys.argv) > 4 else 'output.mp4'  # Get output file path or use default
    
    # Execute video creation  # Comment indicating function call
    success = create_video_from_timeline(audio_file, images_dir, timeline_file, output_file)  # Call video creation function
    
    # Exit with appropriate code  # Comment indicating exit logic
    sys.exit(0 if success else 1)  # Exit with success (0) or failure (1) code


if __name__ == "__main__":  # Check if script is run directly
    main()  # Call main function
