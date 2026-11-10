import os
import glob
import cv2  # OpenCV library for video processing
from PIL import Image  # Pillow library for image processing
from pyktok import specify_browser, save_tiktok
from tqdm import tqdm  # For displaying progress bars

# Solicitar la URL del video de TikTok
video_url = input("Please enter the TikTok video URL: ").strip()

if not video_url:
    print("No URL provided. Exiting the program.")
    exit()

# Definir la ruta base y el archivo final único
script_folder = os.path.dirname(os.path.abspath(__file__))
output_bin_path = os.path.join(script_folder, "frames.bin")

# Eliminar el archivo 'frames.bin' previo si existe para regenerarlo limpio
if os.path.exists(output_bin_path):
    print("Removing previous frames.bin...")
    os.remove(output_bin_path)

# Descargar video de TikTok
try:
    print("Downloading TikTok video...")
    specify_browser("chrome")
    save_tiktok(video_url, save_video=True)
    print("TikTok video downloaded successfully.")
except Exception as e:
    print(f"Error downloading TikTok video: {e}")
    exit()

# Buscar los videos MP4 descargados en la carpeta del script
mp4_files = glob.glob(os.path.join(script_folder, "*.mp4"))
if not mp4_files:
    print("No MP4 videos found to process.")
    exit()

for video_path in mp4_files:
    print(f"Processing video: {os.path.basename(video_path)}")

    try:
        video = cv2.VideoCapture(video_path)
        fps = video.get(cv2.CAP_PROP_FPS)
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

        # Iniciar desde el cuadro 0 (inicio completo del video)
        start_frame = 0
        video.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        frame_count = 0
        oled_resolution = (128, 64)

        # Se abre el archivo 'frames.bin' en modo binario continuo ("wb")
        with open(output_bin_path, "wb") as bin_file:
            with tqdm(total=total_frames, desc="Extracting frames", unit="frame") as pbar:
                while True:
                    ret, frame = video.read()
                    if not ret:
                        break

                    # Redimensionar e interpretar la imagen en monocromo (1-bit)
                    resized_frame = cv2.resize(frame, oled_resolution)
                    grayscale_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
                    bw_image = Image.fromarray(grayscale_frame).convert("1")

                    # Concatenar directamente los bytes de este frame al archivo
                    bin_file.write(bw_image.tobytes())

                    frame_count += 1
                    pbar.update(1)

        video.release()
        print(f"Successfully extracted {frame_count} frames into '{os.path.basename(output_bin_path)}'.")

    except Exception as e:
        print(f"Error processing video {os.path.basename(video_path)}: {e}")