"""Registry tên cho các khe thuật toán (ADR-004).

Mỗi khe (``quality_gate``, ``detector``...) có nhiều phương pháp, đăng ký bằng tên
và chọn trong config. Mục config của một khe có dạng::

    detector:
      method: yolo11n        # tên phương pháp đã đăng ký
      min_score: 0.15        # tham số chung của khe (giá trị không phải dict)
      yolo11n: {...}         # tham số riêng của phương pháp đang chọn (tuỳ chọn)

Riêng khe ``runtime`` dùng khoá ``backend`` thay cho ``method``.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

SLOTS: tuple[str, ...] = (
    "quality_gate",
    "stabilization",
    "detector",
    "plume_tracker",
    "motion_features",
    "clip_classifier",
    "calibrator",
    "landcover",
    "runtime",
)

_METHOD_KEY: dict[str, str] = {"runtime": "backend"}

_REGISTRY: dict[str, dict[str, Callable[..., Any]]] = {slot: {} for slot in SLOTS}


class RegistryError(LookupError):
    pass


def method_key(slot: str) -> str:
    return _METHOD_KEY.get(slot, "method")


def _check_slot(slot: str) -> None:
    if slot not in _REGISTRY:
        raise RegistryError(f"khe không tồn tại: '{slot}'. Các khe hợp lệ: {', '.join(SLOTS)}")


def register(slot: str, name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator đăng ký một factory (class hoặc hàm) cho ``slot`` dưới tên ``name``."""
    _check_slot(slot)

    def decorator(factory: Callable[..., Any]) -> Callable[..., Any]:
        existing = _REGISTRY[slot].get(name)
        if existing is not None and existing is not factory:
            raise RegistryError(f"'{slot}/{name}' đã được đăng ký bởi {existing!r}")
        _REGISTRY[slot][name] = factory
        return factory

    return decorator


def available(slot: str) -> list[str]:
    _check_slot(slot)
    return sorted(_REGISTRY[slot])


def get(slot: str, name: str) -> Callable[..., Any]:
    _check_slot(slot)
    try:
        return _REGISTRY[slot][name]
    except KeyError:
        raise RegistryError(
            f"chưa đăng ký phương pháp '{name}' cho khe '{slot}'. "
            f"Đã đăng ký: {available(slot) or '(chưa có)'}"
        ) from None


def selected_method(config: Mapping[str, Any], slot: str) -> str | None:
    """Tên phương pháp config chọn cho ``slot``; ``None`` nếu khe bị tắt hoặc vắng."""
    _check_slot(slot)
    section = config.get(slot)
    if not isinstance(section, Mapping):
        return None
    name = section.get(method_key(slot))
    return None if name is None else str(name)


def selected_methods(config: Mapping[str, Any]) -> dict[str, str]:
    """Bảng khe -> tên phương pháp, dùng cho ``provenance.methods``."""
    methods = {}
    for slot in SLOTS:
        name = selected_method(config, slot)
        if name is not None:
            methods[slot] = name
    return methods


def params_for(config: Mapping[str, Any], slot: str) -> dict[str, Any]:
    """Tham số chung của khe gộp với tham số riêng của phương pháp đang chọn."""
    section = config.get(slot) or {}
    key = method_key(slot)
    params = {k: v for k, v in section.items() if k != key and not isinstance(v, Mapping)}
    name = selected_method(config, slot)
    specific = section.get(name) if name is not None else None
    if isinstance(specific, Mapping):
        params.update(specific)
    return params


def build(config: Mapping[str, Any], slot: str) -> Any:
    """Khởi tạo phương pháp mà config chọn cho ``slot``; ``None`` nếu khe bị tắt."""
    name = selected_method(config, slot)
    if name is None:
        return None
    return get(slot, name)(**params_for(config, slot))
