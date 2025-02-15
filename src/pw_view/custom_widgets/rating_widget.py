from typing import Optional
import flet as ft

class RatingWidget(ft.Row):  # type: ignore
    def __init__(self, text: str, min_value: int = 0, max_value: int = 100, text_width: Optional[int] = None):
        """
        A rating widget that displays an attribute as a 5-star rating.

        Args:
            text (str): The label text for the attribute.
            min_value (int): The minimum possible value for the rating scale.
            max_value (int): The maximum possible value for the rating scale.
            text_width (Optional[int]): The width of the text label.
        """
        self.min_value = min_value
        self.max_value = max_value
        self.text_widget = ft.Text(text, width=text_width)
        self.update_row(min_value)  # Initialize with min value

        super(RatingWidget, self).__init__(controls=self.controls)

    def attribute_to_stars(self, attribute: int) -> int:
        """
        Converts an attribute value (within a defined min-max range) into a 1-5 star rating.

        Args:
            attribute (int): The attribute value to convert.

        Returns:
            int: The corresponding star rating (1-5).
        """
        # Clamp the attribute within the range
        attribute = max(self.min_value, min(self.max_value, attribute))

        # Normalize the attribute to a 0-1 scale
        normalized_value = (attribute - self.min_value) / (self.max_value - self.min_value)

        # Scale to 1-5 star rating
        return max(1, min(5, int(normalized_value * 4) + 1))

    def create_star_row(self, star_rating: int) -> None:
        """
        Creates a row of star icons based on the star rating.

        Args:
            star_rating (int): The number of filled stars (1-5).
        """
        stars = [
            ft.Icon(ft.Icons.SQUARE if i < star_rating else ft.Icons.SQUARE_OUTLINED, color=ft.Colors.PRIMARY)
            for i in range(5)
        ]

        self.icon_row = ft.Row(controls=stars, spacing=1)
        self.controls = [self.text_widget, self.icon_row]

    def update_row(self, rating: int) -> None:
        """
        Updates the widget with a new rating.

        Args:
            rating (int): The new attribute value.
        """
        star_rating = self.attribute_to_stars(rating)
        self.create_star_row(star_rating)

    def update_text(self, text: str) -> None:
        """
        Updates the label text of the widget.

        Args:
            text (str): The new label text.
        """
        self.text_widget.value = text
