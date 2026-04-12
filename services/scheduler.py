def get_smart_frequency(predicted_passengers: int, base_freq: int) -> int:
    """
    Reduce interval = more buses = handles more passengers.
    base_freq is in minutes.
    """
    if predicted_passengers > 200:
        return max(5, base_freq // 4)      # very high demand → bus every 5 min
    elif predicted_passengers > 150:
        return max(8, base_freq // 3)
    elif predicted_passengers > 100:
        return max(10, base_freq // 2)
    elif predicted_passengers < 30:
        return base_freq * 2               # low demand → reduce frequency
    else:
        return base_freq                   # normal

def generate_departure_times(frequency_minutes: int) -> list:
    """Generate all departure times from 05:00 to 23:00."""
    times = []
    hour = 5
    minute = 0
    while hour < 23:
        times.append(f"{hour:02d}:{minute:02d}")
        minute += frequency_minutes
        if minute >= 60:
            hour += minute // 60
            minute = minute % 60
    return times