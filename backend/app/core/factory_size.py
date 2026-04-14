FACTORY_SIZE_LIMITS = {
    1: {"workforce": 160, "commercial_staff": 40, "overhead": 1_600_000},
    2: {"workforce": 200, "commercial_staff": 50, "overhead": 3_200_000},
    3: {"workforce": 240, "commercial_staff": 60, "overhead": 4_800_000},
    4: {"workforce": 320, "commercial_staff": 80, "overhead": 6_400_000},
    5: {"workforce": 400, "commercial_staff": 100, "overhead": 8_000_000},
}

OVERHEAD_TO_FACTORY_SIZE = {
    values["overhead"]: stars
    for stars, values in FACTORY_SIZE_LIMITS.items()
}


def normalize_factory_size(factory_size: int | None) -> int:
    value = int(factory_size or 1)
    return min(max(value, 1), 5)


def get_factory_limits(factory_size: int | None) -> dict[str, int]:
    size = normalize_factory_size(factory_size)
    return {
        "factory_size": size,
        "workforce": FACTORY_SIZE_LIMITS[size]["workforce"],
        "commercial_staff": FACTORY_SIZE_LIMITS[size]["commercial_staff"],
        "overhead": FACTORY_SIZE_LIMITS[size]["overhead"],
    }


def infer_factory_size_from_overhead(factory_overhead_yearly: int | None) -> int:
    overhead = int(factory_overhead_yearly or 0)
    if overhead in OVERHEAD_TO_FACTORY_SIZE:
        return OVERHEAD_TO_FACTORY_SIZE[overhead]
    for stars in sorted(FACTORY_SIZE_LIMITS):
        if overhead <= FACTORY_SIZE_LIMITS[stars]["overhead"]:
            return stars
    return 5
