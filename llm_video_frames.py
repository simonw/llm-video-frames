import os
import tempfile
import subprocess
import glob
from urllib.parse import urlparse, parse_qs
import llm


@llm.hookimpl
def register_fragment_loaders(register):
    register("video-frames", video_frames_loader)


def video_frames_loader(argument: str):
    """
    Fragment loader "video-frames:<path>?fps=N&timestamps=1"
    - extracts frames at `fps` per second (default 1)
    - if `timestamps=1`, overlays "filename hh:mm:ss" at bottom-right
    """
    # parse out path and query params
    parts = urlparse(argument)
    video_path = parts.path
    params = parse_qs(parts.query)
    fps = float(params.get("fps", ["1"])[0])
    timestamps = params.get("timestamps", ["0"])[0] in ("1", "true", "True")
    if not os.path.exists(video_path):
        raise ValueError(f"Video file not found: {video_path}")

    # prepare temp dir
    out_dir = tempfile.mkdtemp(prefix="llm_video_frames_")
    # base filename for overlay
    base_name = os.path.basename(video_path)

    # build ffmpeg filter
    vf_parts = [f"fps={fps}"]
    if timestamps:
        # overlay filename and timestamp (hh:mm:ss) at bottom-right
        timestamp_expr = r"%{pts\:hms}"  # → %{pts\:hms}
        text = f"{base_name} {timestamp_expr}"  # → "items.mov %{pts\:hms}"
        draw = (
            "drawtext=fontcolor=white:fontsize=24:box=1:boxcolor=black@0.5"
            f":text='{text}':x=w-tw-10:y=h-th-10"
        )
        vf_parts.append(draw)
    vf = ",".join(vf_parts)

    # output pattern
    pattern = os.path.join(out_dir, "frame_%05d.jpg")

    # run ffmpeg
    cmd = ["ffmpeg", "-v", "error", "-i", video_path, "-vf", vf, "-q:v", "2", pattern]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ffmpeg failed: {e}")

    # collect frames
    files = sorted(glob.glob(os.path.join(out_dir, "frame_*.jpg")))
    attachments = [llm.Attachment(path=f) for f in files]
    return attachments
