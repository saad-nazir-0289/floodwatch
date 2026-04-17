from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

import cv2
import numpy as np
from PIL import Image


@dataclass
class AnalysisResult:
    original: np.ndarray
    enhanced: np.ndarray
    water_mask: np.ndarray
    urban_mask: np.ndarray
    water_overlay: np.ndarray
    urban_overlay: np.ndarray
    combined_overlay: np.ndarray
    confidence_note: str
    metrics: dict[str, float | int | str]


@dataclass
class ChangeResult:
    before: np.ndarray
    after: np.ndarray
    change_map: np.ndarray
    flood_gain_mask: np.ndarray
    urban_change_mask: np.ndarray
    change_overlay: np.ndarray
    metrics: dict[str, float | int | str]


def read_image(uploaded_file) -> np.ndarray:
    image = Image.open(uploaded_file).convert("RGB")
    return np.array(image)


def resize_for_demo(image: np.ndarray, max_side: int = 1400) -> np.ndarray:
    h, w = image.shape[:2]
    scale = min(max_side / max(h, w), 1.0)
    if scale == 1.0:
        return image
    new_size = (max(1, int(w * scale)), max(1, int(h * scale)))
    return cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)


def enhance_image(image: np.ndarray, contrast: float = 1.2) -> np.ndarray:
    gamma = 0.95
    lookup = np.array([((value / 255.0) ** gamma) * 255 for value in range(256)], dtype=np.uint8)
    gamma_corrected = cv2.LUT(image, lookup)
    image_f = gamma_corrected.astype(np.float32) / 255.0
    image_f = np.clip((image_f - 0.5) * contrast + 0.5, 0.0, 1.0)
    return (image_f * 255).astype(np.uint8)


def _normalize_gray(gray: np.ndarray) -> np.ndarray:
    return cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)


def estimate_water_mask(image: np.ndarray, sensitivity: float = 0.5) -> np.ndarray:
    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray, (7, 7), 0)
    texture = cv2.Laplacian(blur, cv2.CV_32F)
    texture = cv2.convertScaleAbs(texture)

    h, s, v = cv2.split(hsv)
    l, a, b = cv2.split(lab)

    sat_gate = int(45 + 90 * sensitivity)
    val_gate = int(150 - 45 * sensitivity)
    texture_gate = int(26 + 20 * (1 - sensitivity))

    blueish = (h > 80) & (h < 145) & (s > sat_gate)
    dark_smooth = (v < val_gate) & (texture < texture_gate)
    lab_water = (b < np.percentile(b, 45 + 18 * sensitivity)) & (a < np.percentile(a, 55))

    candidate = (blueish | dark_smooth | lab_water).astype(np.uint8) * 255
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    candidate = cv2.morphologyEx(candidate, cv2.MORPH_OPEN, kernel, iterations=1)
    candidate = cv2.morphologyEx(candidate, cv2.MORPH_CLOSE, kernel, iterations=2)

    area_threshold = max(48, int(image.shape[0] * image.shape[1] * 0.00008))
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(candidate, connectivity=8)
    cleaned = np.zeros_like(candidate)
    for idx in range(1, num_labels):
        if stats[idx, cv2.CC_STAT_AREA] >= area_threshold:
            cleaned[labels == idx] = 255
    return cleaned


def estimate_urban_mask(image: np.ndarray, sensitivity: float = 0.5) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    gray = _normalize_gray(gray)
    edges = cv2.Canny(gray, 60, 160)
    sobel_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    gradient = cv2.magnitude(sobel_x, sobel_y)
    gradient = _normalize_gray(gradient)

    local_mean = cv2.blur(gray, (15, 15))
    local_var = cv2.blur((gray.astype(np.float32) - local_mean.astype(np.float32)) ** 2, (15, 15))
    local_var = _normalize_gray(local_var)

    bright = gray > int(120 - 30 * sensitivity)
    structured = gradient > int(75 - 18 * sensitivity)
    textured = local_var > int(68 - 18 * sensitivity)
    edgier = cv2.dilate(edges, np.ones((3, 3), np.uint8), iterations=1) > 0

    candidate = (bright & structured) | (structured & textured) | (bright & edgier)
    mask = candidate.astype(np.uint8) * 255

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    return mask


def blend_mask(image: np.ndarray, mask: np.ndarray, color: tuple[int, int, int], alpha: float = 0.42) -> np.ndarray:
    overlay = image.copy().astype(np.float32)
    color_arr = np.array(color, dtype=np.float32)
    active = mask > 0
    overlay[active] = overlay[active] * (1 - alpha) + color_arr * alpha
    return np.clip(overlay, 0, 255).astype(np.uint8)


def blend_dual_masks(image: np.ndarray, water_mask: np.ndarray, urban_mask: np.ndarray, alpha: float = 0.40) -> np.ndarray:
    combined = image.copy().astype(np.float32)
    water = water_mask > 0
    urban = urban_mask > 0
    combined[water] = combined[water] * (1 - alpha) + np.array([35, 195, 230], dtype=np.float32) * alpha
    combined[urban] = combined[urban] * (1 - alpha) + np.array([255, 156, 70], dtype=np.float32) * alpha
    both = water & urban
    combined[both] = np.array([201, 104, 255], dtype=np.float32)
    return np.clip(combined, 0, 255).astype(np.uint8)


def _connected_regions(mask: np.ndarray) -> int:
    num_labels, _, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    count = 0
    for idx in range(1, num_labels):
        if stats[idx, cv2.CC_STAT_AREA] > 40:
            count += 1
    return count


def estimate_confidence(image: np.ndarray, water_mask: np.ndarray) -> str:
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    contrast = gray.std()
    water_share = water_mask.mean() / 255.0
    if contrast > 42 and 0.01 < water_share < 0.55:
        return "High demo confidence: good tonal separation and coherent water regions."
    if contrast > 28:
        return "Moderate demo confidence: usable overhead imagery, but inspect overlays before presenting."
    return "Low demo confidence: low contrast or ambiguous terrain may reduce segmentation quality."


def analyze_single_image(image: np.ndarray, sensitivity: float = 0.5, alpha: float = 0.42) -> AnalysisResult:
    original = resize_for_demo(image)
    enhanced = enhance_image(original)
    water_mask = estimate_water_mask(enhanced, sensitivity=sensitivity)
    urban_mask = estimate_urban_mask(enhanced, sensitivity=sensitivity)

    water_overlay = blend_mask(original, water_mask, (35, 195, 230), alpha=alpha)
    urban_overlay = blend_mask(original, urban_mask, (255, 156, 70), alpha=alpha)
    combined_overlay = blend_dual_masks(original, water_mask, urban_mask, alpha=alpha)

    total_pixels = original.shape[0] * original.shape[1]
    water_pixels = int(np.count_nonzero(water_mask))
    urban_pixels = int(np.count_nonzero(urban_mask))

    metrics = {
        "Water coverage (%)": round(100 * water_pixels / total_pixels, 2),
        "Built-up proxy (%)": round(100 * urban_pixels / total_pixels, 2),
        "Connected flood regions": _connected_regions(water_mask),
        "Image size": f"{original.shape[1]} x {original.shape[0]}",
    }

    return AnalysisResult(
        original=original,
        enhanced=enhanced,
        water_mask=water_mask,
        urban_mask=urban_mask,
        water_overlay=water_overlay,
        urban_overlay=urban_overlay,
        combined_overlay=combined_overlay,
        confidence_note=estimate_confidence(enhanced, water_mask),
        metrics=metrics,
    )


def align_images(before: np.ndarray, after: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    before = resize_for_demo(before)
    after = resize_for_demo(after)
    target_h = min(before.shape[0], after.shape[0])
    target_w = min(before.shape[1], after.shape[1])
    before_resized = cv2.resize(before, (target_w, target_h), interpolation=cv2.INTER_AREA)
    after_resized = cv2.resize(after, (target_w, target_h), interpolation=cv2.INTER_AREA)
    return before_resized, after_resized


def analyze_change(before: np.ndarray, after: np.ndarray, sensitivity: float = 0.5, alpha: float = 0.45) -> ChangeResult:
    before_aligned, after_aligned = align_images(before, after)
    before_enhanced = enhance_image(before_aligned)
    after_enhanced = enhance_image(after_aligned)

    before_gray = cv2.cvtColor(before_enhanced, cv2.COLOR_RGB2GRAY)
    after_gray = cv2.cvtColor(after_enhanced, cv2.COLOR_RGB2GRAY)
    diff = cv2.absdiff(before_gray, after_gray)
    diff_norm = _normalize_gray(diff)

    _, diff_mask = cv2.threshold(diff_norm, int(28 + 22 * (1 - sensitivity)), 255, cv2.THRESH_BINARY)
    score, similarity_map = estimate_similarity(before_gray, after_gray)
    _, similarity_mask = cv2.threshold(
        similarity_map,
        int(42 + 22 * (1 - sensitivity)),
        255,
        cv2.THRESH_BINARY,
    )

    change_mask = cv2.bitwise_or(diff_mask, similarity_mask)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    change_mask = cv2.morphologyEx(change_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    change_mask = cv2.morphologyEx(change_mask, cv2.MORPH_OPEN, kernel, iterations=1)

    before_water = estimate_water_mask(before_enhanced, sensitivity=sensitivity)
    after_water = estimate_water_mask(after_enhanced, sensitivity=sensitivity)
    flood_gain = cv2.bitwise_and(after_water, cv2.bitwise_not(before_water))

    before_urban = estimate_urban_mask(before_enhanced, sensitivity=sensitivity)
    after_urban = estimate_urban_mask(after_enhanced, sensitivity=sensitivity)
    urban_change = cv2.bitwise_xor(before_urban, after_urban)

    overlay = after_aligned.copy().astype(np.float32)
    overlay[change_mask > 0] = overlay[change_mask > 0] * (1 - alpha) + np.array([253, 223, 77]) * alpha
    overlay[flood_gain > 0] = np.array([35, 195, 230])
    overlay[urban_change > 0] = overlay[urban_change > 0] * 0.55 + np.array([255, 156, 70]) * 0.45
    overlay = np.clip(overlay, 0, 255).astype(np.uint8)

    total_pixels = after_aligned.shape[0] * after_aligned.shape[1]
    metrics = {
        "Changed area (%)": float(round(100 * np.count_nonzero(change_mask) / total_pixels, 2)),
        "New water / flood gain (%)": float(round(100 * np.count_nonzero(flood_gain) / total_pixels, 2)),
        "Urban proxy change (%)": float(round(100 * np.count_nonzero(urban_change) / total_pixels, 2)),
        "Similarity score": round(float(score), 3),
    }

    return ChangeResult(
        before=before_aligned,
        after=after_aligned,
        change_map=change_mask,
        flood_gain_mask=flood_gain,
        urban_change_mask=urban_change,
        change_overlay=overlay,
        metrics=metrics,
    )


def mask_to_rgb(mask: np.ndarray, color: tuple[int, int, int]) -> np.ndarray:
    rgb = np.zeros((mask.shape[0], mask.shape[1], 3), dtype=np.uint8)
    rgb[mask > 0] = color
    return rgb


def to_png_bytes(image: np.ndarray) -> bytes:
    pil_image = Image.fromarray(image)
    buffer = BytesIO()
    pil_image.save(buffer, format="PNG")
    return buffer.getvalue()


def estimate_similarity(before_gray: np.ndarray, after_gray: np.ndarray) -> tuple[float, np.ndarray]:
    before_f = before_gray.astype(np.float32) / 255.0
    after_f = after_gray.astype(np.float32) / 255.0

    tonal_diff = np.abs(before_f - after_f)
    before_blur = cv2.GaussianBlur(before_f, (11, 11), 1.5)
    after_blur = cv2.GaussianBlur(after_f, (11, 11), 1.5)
    before_grad = cv2.Laplacian(before_blur, cv2.CV_32F)
    after_grad = cv2.Laplacian(after_blur, cv2.CV_32F)
    structure_diff = np.clip(np.abs(before_grad - after_grad), 0.0, 1.0)

    combined = np.clip(0.65 * tonal_diff + 0.35 * structure_diff, 0.0, 1.0)
    similarity_score = float(np.clip(1.0 - combined.mean(), 0.0, 1.0))
    return similarity_score, (combined * 255).astype(np.uint8)
