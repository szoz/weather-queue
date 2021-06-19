def validate_cities(raw_cities: str) -> bool:
    """Returns True if given cities match 'city,city,...' pattern."""
    for city in raw_cities.split(','):
        if not city.isalpha():
            return False

    return True
