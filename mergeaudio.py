import ffmpeg

def merge_mp3_files(file_list, output_file):
    input_files = [ffmpeg.input(f) for f in file_list]
    ffmpeg.concat(*input_files, v=0, a=1).output(output_file).run()

# Example usage
file_list = [f"years_{i}.mp3" for i in range(0, 124)]  # Adjust range as needed
output_file = "years_all.mp3"
merge_mp3_files(file_list, output_file)
