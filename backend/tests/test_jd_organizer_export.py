import zipfile

import numpy as np
from PIL import Image

from backend.services import vip_organizer_service as service


def test_jd_export_uses_separate_800_and_750_folders(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "_session_result_dir", lambda _session_id: tmp_path)
    monkeypatch.setattr(service, "_validate_slot_map", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        service,
        "_render_slot_image",
        lambda *_args, **_kwargs: Image.new("RGB", (32, 32), "white"),
    )

    slots = [
        {"file_name": file_name, "image_ids": [1], "adjustments": []}
        for file_name, *_ in service.JD_SLOT_DEFINITIONS
    ]
    session_id = "a" * 32
    result = service.export_package(session_id, slots, {}, "jd")
    export_id = result["download_url"].split("/")[-2]
    zip_path = service.export_zip(session_id, export_id)

    with zipfile.ZipFile(zip_path) as archive:
        names = set(archive.namelist())

    expected_800 = {
        "800/0-无logo.jpg",
        "800/1.jpg",
        "800/2.jpg",
        "800/3.jpg",
        "800/4.jpg",
        "800/5.jpg",
        "800/透明.png",
    }
    expected_750 = {f"750/{index}.jpg" for index in range(1, 6)}

    assert names == expected_800 | expected_750
    assert all(name.startswith(("800/", "750/")) for name in names)


def _dark_pixel_bbox(image: Image.Image) -> tuple[int, int, int, int]:
    pixels = np.asarray(image.convert("RGB"))
    mask = pixels.mean(axis=2) < 245
    ys, xs = np.where(mask)
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def _bright_pixel_bbox(image: Image.Image) -> tuple[int, int, int, int]:
    pixels = np.asarray(image.convert("RGB"))
    mask = pixels.mean(axis=2) > 50
    ys, xs = np.where(mask)
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def test_jd_logo_matches_example_geometry():
    canvas_800 = Image.new("RGB", (800, 800), "white")
    service._draw_jd_elle_logo(canvas_800, canvas_800.size)
    assert _dark_pixel_bbox(canvas_800) == (32, 38, 219, 98)

    canvas_750 = Image.new("RGB", (750, 1000), "white")
    service._draw_jd_elle_logo(canvas_750, canvas_750.size)
    assert _dark_pixel_bbox(canvas_750) == (56, 45, 243, 105)


def test_jd_white_logo_uses_the_same_geometry():
    canvas_800 = Image.new("RGB", (800, 800), "#222222")
    service._draw_jd_elle_logo(canvas_800, canvas_800.size, "white")
    assert _bright_pixel_bbox(canvas_800) == (32, 38, 219, 98)

    canvas_750 = Image.new("RGB", (750, 1000), "#222222")
    service._draw_jd_elle_logo(canvas_750, canvas_750.size, "white")
    assert _bright_pixel_bbox(canvas_750) == (56, 45, 243, 105)


def test_jd_logo_color_is_stored_per_output_slot():
    slot_map = service._slot_map(
        [
            {"file_name": "0-无logo.jpg", "image_ids": [1], "adjustments": []},
            {"file_name": "1.jpg", "image_ids": [1], "adjustments": [], "logo_color": "white"},
            {"file_name": "2.jpg", "image_ids": [2], "adjustments": []},
        ],
        "jd",
    )

    assert slot_map["1.jpg"]["logo_color"] == "white"
    assert slot_map["2.jpg"]["logo_color"] == "black"


def test_jd_single_model_preview_does_not_create_vip_model_slot():
    slot_map = service._slot_map(
        [{"file_name": "1.jpg", "image_ids": [7], "adjustments": [], "logo_color": "white"}],
        "jd",
    )

    assert slot_map["1.jpg"]["image_ids"] == [7]
    assert "50.jpg" not in slot_map


def test_manual_crop_switches_cover_templates_to_contain():
    assert service._crop_aware_mode(None, "cover") == "cover"
    assert service._crop_aware_mode({"crop_y": 0.1, "crop_height": 0.8}, "cover") == "contain"


def test_401_manual_product_layer_can_move_outside_original_box():
    source = Image.new("RGBA", (20, 20), (210, 20, 20, 255))
    clipped = Image.new("RGB", (100, 100), "white")
    floating = Image.new("RGB", (100, 100), "white")
    adjustment = {"offset_y": 1.0}

    service._paste_product(clipped, source, (40, 40, 60, 60), adjustment)
    service._paste_product_floating(floating, source, (40, 40, 60, 60), adjustment)

    assert clipped.getpixel((50, 70)) == (255, 255, 255)
    assert floating.getpixel((50, 70))[0] > floating.getpixel((50, 70))[1]
