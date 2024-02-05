"""Helpers to create widgets from a model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from magicgui.widgets import Container, create_widget

if TYPE_CHECKING:
    from magicgui.widgets._bases import ValueWidget
    from psygnal import EventedModel


# TODO: needs magicgui to support pydantic constraints
def make_controller(model: EventedModel) -> Container:
    """Create a controller widget for an EventedModel."""
    widgets = []
    for field in model.__fields__.values():
        if field.field_info.extra.get("hide_control", False):
            continue
        current_value = getattr(model, field.name)
        wdg: ValueWidget = create_widget(
            value=current_value,
            annotation=field.outer_type_,
            name=f"{field.name}_",
            raise_on_unknown=False,
        )

        wdg.changed.connect_setattr(model, field.name)
        model.events.signals[field.name].connect_setattr(wdg, "value")
        widgets.append(wdg)
    return Container(widgets=widgets)
