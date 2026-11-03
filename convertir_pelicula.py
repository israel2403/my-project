"""Ejecutar: uv run --with imageio-ffmpeg convertir_pelicula.py"""

import argparse
import shutil
import subprocess
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Convierte MKV a MP4 sin recodificar el video.")
    parser.add_argument("--input", type=Path, default=Path(
        r"C:\Users\jacob\Videos\Mision.Imposible.La.sentencia.final.2025.1080p-Dual-Lat\Mision.Imposible.La.Sentencia.Final.2025.1080P-Dual-Lat.mkv"
    ))
    parser.add_argument("--project", type=Path, default=Path(r"C:\projects\movies"))
    args = parser.parse_args()
    if not args.input.is_file():
        parser.error(f"No existe el video: {args.input}")
    import imageio_ffmpeg

    args.project.mkdir(parents=True, exist_ok=True)
    script = Path(__file__).resolve()
    destination = args.project / script.name
    if script != destination.resolve():
        shutil.copy2(script, destination)
    output = args.project / (args.input.stem + ".mp4")
    partial = args.project / (args.input.stem + ".partial.mp4")
    if output.exists() or partial.exists():
        parser.error(f"Ya existe la salida o una conversion parcial en {args.project}; no se sobrescribira.")
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    base = [ffmpeg, "-hide_banner", "-nostdin", "-n", "-i", str(args.input),
            "-map", "0:v:0", "-map", "0:a?", "-map", "0:s?",
            "-map_metadata", "0", "-c:v", "copy", "-c:s", "mov_text"]
    try:
        # Primero conservar tambien el audio; AAC es el respaldo si no cabe en MP4.
        result = subprocess.run(base + ["-c:a", "copy", "-movflags", "+faststart", str(partial)])
        if result.returncode:
            if partial.exists():
                partial.unlink()
            subprocess.run(base + ["-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", str(partial)], check=True)
        # Leer la estructura del archivo antes de darle el nombre definitivo.
        subprocess.run([ffmpeg, "-v", "error", "-i", str(partial), "-map", "0:v:0",
                        "-t", "1", "-f", "null", "-"], check=True)
        partial.rename(output)
    except (subprocess.CalledProcessError, KeyboardInterrupt):
        print(f"Conversion interrumpida. Archivo parcial: {partial}")
        raise SystemExit(1)
    print(f"MP4 creado: {output}")
    print("El MKV original se conserva.")


if __name__ == "__main__":
    main()
