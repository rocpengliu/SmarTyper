import os
import platform


def get_interface_scale(width: int, height: int, design_width: int, design_height: int) -> float:
    if min(width, height, design_width, design_height) <= 0:
        raise ValueError("Window and design dimensions must be positive")
    return min(1.0, width / design_width, height / design_height) * 0.98


def get_bottom_margin() -> int:
    configured = os.environ.get("SMARTYPER_BOTTOM_MARGIN")
    if configured is not None:
        try:
            margin = int(configured)
        except ValueError as error:
            raise ValueError("SMARTYPER_BOTTOM_MARGIN must be a non-negative integer") from error
        if margin < 0:
            raise ValueError("SMARTYPER_BOTTOM_MARGIN must be a non-negative integer")
        return margin

    is_wsl = bool(os.environ.get("WSL_DISTRO_NAME")) or "microsoft" in platform.release().lower()
    return 64 if is_wsl else 0
