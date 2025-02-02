import requests
import m3u8
import subprocess
import os
import shutil

def download_music_interval(m3u8_url, start_time, end_time, output_filename="output.mp3"):
    """
    Downloads a specific time interval from an m3u8 stream and converts it to MP3.

    Args:
        m3u8_url: The URL of the m3u8 playlist.
        start_time: The start time in seconds.
        end_time: The end time in seconds.
        output_filename: The name of the output MP3 file.
    """
    temp_dir = "."  # Create a temporary directory

    try:
        response = requests.get(m3u8_url)
        response.raise_for_status()
        playlist = m3u8.loads(response.text)

        total_duration = 0
        segments_to_download = []
        print(playlist.target_duration)

        for segment in playlist.segments:
            segment_duration = segment.duration
            segment_url = segment.uri
            if not segment_url.startswith("http"):
                segment_url = m3u8_url.rsplit("/", 1)[0] + "/" + segment_url

            if total_duration + segment_duration >= start_time:
                segments_to_download.append((segment_url, max(0, start_time - total_duration), min(segment_duration, end_time - total_duration)))  # Store segment URL and overlapping time

            total_duration += segment_duration
            if total_duration >= end_time:
                break

        if not segments_to_download:
            print("No segments found within the specified time interval.")
            return

        os.makedirs(temp_dir, exist_ok=True)
        segment_files = []

        for i, (segment_url, segment_start, segment_duration) in enumerate(segments_to_download):
            segment_filename = os.path.join(temp_dir, f"segment_{i}.ts")
            segment_files.append(segment_filename)

            segment_response = requests.get(segment_url, stream=True)
            segment_response.raise_for_status()
            with open(segment_filename, "wb") as f:
                for chunk in segment_response.iter_content(chunk_size=8192):
                    f.write(chunk)

            # Trim the segment using ffmpeg if necessary
            if segment_start > 0 or segment_duration < segment.duration:
                trimmed_filename = os.path.join(temp_dir, f"trimmed_{i}.ts")
                command = ["ffmpeg", "-ss 00:01:00.000" "-t 00:02:00.000", "-i", segment_filename, "-c", "copy", trimmed_filename]
                subprocess.run(command, check=True)
                segment_files[i] = trimmed_filename # Update the segment file list

        # Concatenate and convert to MP3 using ffmpeg
        concat_list_path = os.path.join(temp_dir, "concat.txt")
        with open(concat_list_path, "w") as f:
            for file in segment_files:
                f.write(f"file '{file}'\n")

        command = ["ffmpeg", "-f", "concat", "-safe", "0", "-i", concat_list_path, "-c:a", "libmp3lame", output_filename]
        subprocess.run(command, check=True)

        print(f"Music interval saved to {output_filename}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching .m3u8 or segment: {e}")
    # except m3u8.exceptions.M3U8Error as e:
    #     print(f"Error parsing .m3u8: {e}")
    except FileNotFoundError:
        print("Error: ffmpeg not found. Please install ffmpeg.")
    except subprocess.CalledProcessError as e:
        print(f"Error running ffmpeg: {e}")
    finally:
        if os.path.exists(temp_dir):
            return
            shutil.rmtree(temp_dir)  # Clean up temporary files and directory


if __name__ == "__main__":
    # m3u8_url = input("Enter the .m3u8 URL: ")
    m3u8_url = 'https://stream44.asset.filimo.com/filimo-video/173856265779447214/1738620969/089dccd7f0e55c9521df01aae3aa9de4ccd33622/163476x264new1-360p.mp4/chunk.m3u8?wmsAuthSign=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbiI6IjZjMjY2Njk5M2ExMTQ1YjM2MDNmOWRkNjUyMDc2NWRlIiwiZXhwIjoxNzM4NjIwOTY5LCJpc3MiOiJTYWJhIElkZWEgR1NJRyJ9.QpPGIeh7QwkF7nSL6uc65sdJS6_AcLai7clC1wiwLhY'
    start_time = 1
    end_time = 10
    download_music_interval(m3u8_url, start_time, end_time)