from PIL import Image, ImageChops, ImageStat


def compare_images(before: Image.Image, after: Image.Image):
    if not before or not after:
        raise ValueError("Both 'before' and 'after' images are required for comparison.")

    before_rgb = before.convert("RGB").resize((256, 256))
    after_rgb = after.convert("RGB").resize((256, 256))

    diff = ImageChops.difference(before_rgb, after_rgb)
    stat = ImageStat.Stat(diff)

    # Mean pixel difference, normalized to 0..1.
    mean_diff = sum(stat.mean) / (3 * 255)
    change_score = max(0.0, min(1.0, mean_diff * 2.0))

    return {
        "change_score": round(change_score, 4),
        "verified": change_score >= 0.20,
    }

