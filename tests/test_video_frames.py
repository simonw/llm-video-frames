import os
import shutil
import pytest

# adjust this import path to wherever your loader code actually lives
from llm_video_frames import video_frames_loader

# skip entire module if ffmpeg is not installed
ffmpeg_path = shutil.which("ffmpeg")
if not ffmpeg_path:
    pytest.skip(
        "ffmpeg not found on PATH, skipping video frame extraction tests",
        allow_module_level=True,
    )


@pytest.fixture
def video_file_path(tmp_path):
    """
    Ensure there's a test.mp4 available.  We expect a small 2-second mp4
    sitting next to this test file at tests/test.mp4; if not found, we skip.
    """
    here = os.path.dirname(__file__)
    candidate = os.path.join(here, "test.mp4")
    if not os.path.exists(candidate):
        pytest.skip("test.mp4 not found in tests directory, skipping")
    return candidate


def cleanup_attachments(attachments):
    """
    Remove generated files and their parent temp directory.
    """
    if not attachments:
        return
    # attachments are llm.Attachment objects with .path
    out_dir = os.path.dirname(attachments[0].path)
    shutil.rmtree(out_dir)


def test_missing_file_raises_value_error():
    fake = "/path/does/not/exist.mp4"
    with pytest.raises(ValueError) as exc:
        video_frames_loader(fake)
    assert "Video file not found" in str(exc.value)


def test_default_fps_produces_two_frames(video_file_path):
    """
    Default is fps=1 on a 2-second video -> 2 frames
    """
    arg = f"video-frames:{video_file_path}"
    attachments = video_frames_loader(arg)
    try:
        paths = [a.path for a in attachments]
        assert len(paths) == 2, f"expected 2 frames, got {len(paths)}"
        for p in paths:
            assert os.path.exists(p), f"frame file missing: {p}"
            assert p.lower().endswith(".jpg")
    finally:
        cleanup_attachments(attachments)


@pytest.mark.parametrize(
    "fps, expected_count",
    [
        (1, 2),
        (2, 5),
        (0.5, 1),
    ],
)
def test_fps_parameter_changes_frame_count(video_file_path, fps, expected_count):
    arg = f"video-frames:{video_file_path}?fps={fps}"
    attachments = video_frames_loader(arg)
    try:
        paths = [a.path for a in attachments]
        assert (
            len(paths) == expected_count
        ), f"fps={fps} expected {expected_count} frames, got {len(paths)}"
    finally:
        cleanup_attachments(attachments)


def test_timestamps_overlay_does_not_change_count(video_file_path):
    """
    Turning on timestamps should not change the number of frames, just overlay text.
    """
    arg = f"video-frames:{video_file_path}?timestamps=1"
    attachments = video_frames_loader(arg)
    try:
        paths = [a.path for a in attachments]
        # still 2 frames at default fps=1
        assert len(paths) == 2
        # basic sanity: files exist and are non‐empty
        for p in paths:
            assert os.path.getsize(p) > 0
    finally:
        cleanup_attachments(attachments)
