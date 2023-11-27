
import pygame

from component import Component


class BorderContainer(Component):
    top: Component | None
    bottom: Component | None
    left: Component | None
    right: Component | None
    center: Component | None

    def __init__(self):
        self.children = []

    def get_preferred_size(self) -> tuple[int, int]:
        top: tuple[int, int]
        bottom: tuple[int, int]
        left: tuple[int, int]
        right: tuple[int, int]
        center: tuple[int, int]

        top = self.top.get_preferred_size() if self.top else (0, 0)
        bottom = self.bottom.get_preferred_size() if self.bottom else (0, 0)
        left = self.left.get_preferred_size() if self.left else (0, 0)
        right = self.right.get_preferred_size() if self.right else (0, 0)
        center = self.center.get_preferred_size() if self.center else (0, 0)

        center_height = max(left[1], center[1], right[1])
        center_width = 0
        if self.left:
            center_width += self.left.get_preferred_width(center_height)
        if self.center:
            center_width += self.center.get_preferred_width(center_height)
        if self.right:
            center_width += self.right.get_preferred_width(center_height)
        width = max(top[0], center_width, bottom[0])

        height = top[1] + center_height + bottom[1]

        width = max(width, 8)
        height = max(height, 8)

        edge = self.edge_spacing()

        return (width + edge.h, height + edge.v)

    def get_preferred_width(self, height: int) -> int:
        edge = self.edge_spacing()
        height -= edge.v

        top: tuple[int, int]
        bottom: tuple[int, int]

        top = self.top.get_preferred_size() if self.top else (0, 0)
        bottom = self.bottom.get_preferred_size() if self.bottom else (0, 0)

        top_height = top[1]
        bottom_height = bottom[1]
        center_height = height - (top_height + bottom_height)
        if center_height < 0:
            total = top_height + bottom_height
            top_height = (height * top_height) // total
            bottom_height = (height * bottom_height) // total
            center_height = 0

        center_width = 0
        if self.left:
            center_width += self.left.get_preferred_width(center_height)
        if self.center:
            center_width += self.center.get_preferred_width(center_height)
        if self.right:
            center_width += self.right.get_preferred_width(center_height)

        top_width = 0
        if self.top:
            top_width = self.top.get_preferred_width(top_height)
        bottom_width = 0
        if self.bottom:
            bottom_width = self.bottom.get_preferred_width(bottom_height)

        return max(top_width, center_width, bottom_width) + edge.h

    def get_preferred_height(self, width: int) -> int:
        edge = self.edge_spacing()
        width -= edge.h

        left: tuple[int, int]
        right: tuple[int, int]

        left = self.left.get_preferred_size() if self.left else (0, 0)
        right = self.right.get_preferred_size() if self.right else (0, 0)
        left_width = left[0]
        right_width = right[0]
        center_width = width - (left_width + right_width)
        if center_width < 0:
            total = left_width + right_width
            left_width = (width * left_width) // total
            right_width = (width * right_width) // total
            center_width = 0
        left_height = 0
        if self.left:
            left_height = self.left.get_preferred_height(left_width)
        right_height = 0
        if self.right:
            right_height = self.right.get_preferred_height(right_width)
        center_height = 0
        if self.center:
            center_height = self.center.get_preferred_height(center_width)

        center_height = max(left_height, center_height, right_height)

        top_height = 0
        if self.top:
            top_height = self.top.get_preferred_height(width)
        bottom_height = 0
        if self.bottom:
            bottom_height = self.bottom.get_preferred_height(width)

        return top_height + center_height + bottom_height + edge.v

    def set_area(self, area: pygame.Rect):
        super().set_area(area)

        edge = self.edge_spacing()
        area.x += edge.left
        area.w -= edge.h
        area.y += edge.top
        area.h -= edge.v

        top_height = 0
        if self.top:
            top_height = self.top.get_preferred_height(area.w)
        bottom_height = 0
        if self.bottom:
            bottom_height = self.bottom.get_preferred_height(area.w)
        center_height = area.h - (top_height + bottom_height)
        if center_height < 0:
            total = top_height + bottom_height
            top_height = (area.h * top_height) // total
            bottom_height = (area.h * bottom_height) // total
            center_height = 0

        left_width = 0
        if self.left:
            left_width = self.left.get_preferred_width(center_height)
        right_width = 0
        if self.right:
            right_width = self.right.get_preferred_width(center_height)

        center_width = area.w - (left_width + right_width)
        if center_width < 0:
            total = left_width + right_width
            left_width = (area.w * left_width) // total
            right_width = (area.w * right_width) // total
            center_width = 0

        x = area.x
        y = area.y
        if self.top:
            self.top.set_area(pygame.Rect(x, y, area.w, top_height))
        if self.bottom:
            self.bottom.set_area(pygame.Rect(
                x, y-bottom_height, area.w, bottom_height))
        if self.left:
            self.left.set_area(pygame.Rect(
                x, y+top_height, left_width, center_height))
        if self.right:
            self.right.set_area(pygame.Rect(
                x+area.w-right_width, y+top_height, right_width, center_height))
        if self.center:
            self.center.set_area(pygame.Rect(
                x+left_width, y+top_height, center_width, center_height))

    def draw(self, surface: pygame.Surface):
        super().draw(surface)
        if self.center:
            self.center.draw(surface)
        if self.right:
            self.right.draw(surface)
        if self.left:
            self.left.draw(surface)
        if self.bottom:
            self.bottom.draw(surface)
        if self.top:
            self.top.draw(surface)
