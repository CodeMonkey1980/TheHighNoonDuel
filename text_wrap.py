# automatically wraps words
# returns any texts that didn't get blitted
from pygame.rect import Rect


def draw_text(surface, text, color, rect, font, aa=False, bkg=None):
    rect = Rect(rect)
    y = rect.top
    line_spacing = -2

    # get the height of the font
    font_height = font.size("Tg")[1]

    # remove carriage_returns
    text = text.replace('\r', '')

    page_end_marker_found = False
    while text:
        i = 1

        # determine if the row of texts will be outside our area
        if y + font_height > rect.bottom or page_end_marker_found:
            break

        # determine maximum width of line
        while font.size(text[:i])[0] < rect.width and i < len(text):
            if text[i] == '~':
                text = f'{text[:i]} {text[i + 1:]}'
                page_end_marker_found = True
            elif i == 1 and (text[0] == '\n'):
                text = f'{text[i:]}'
                break
            elif text[i] == '\n':
                text = f'{text[:i]} {text[i + 1:]}'
                i += 1
                break
            i += 1

        # if we've wrapped the texts, then adjust the wrap to the last word
        if i < len(text): 
            i = text.rfind(" ", 0, i) + 1

        # render the line and blit it to the surface
        if bkg:
            image = font.render(text[:i], 1, color, bkg)
            image.set_colorkey(bkg)
        else:
            image = font.render(text[:i], aa, color)

        surface.blit(image, (rect.left, y))
        y += font_height + line_spacing

        # remove the texts we just blitted
        text = text[i:]

    return text