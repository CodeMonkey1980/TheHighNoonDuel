def between(value, reference_1, reference_2):
    reference_low = min(reference_1, reference_2)
    reference_high = max(reference_1, reference_2)
    return reference_low < value and reference_high > value


def is_collision(a_x, a_y, a_width, a_height, b_x, b_y, b_width, b_height):
    # a = self
    # b = target
    contact_points = []
    if a_x + a_width < b_x:
        return False
    if b_x + b_width < a_x:
        return False
    if b_y + b_height < a_y:
        return False
    if b_y > a_y + a_height:
        return False
    return True
