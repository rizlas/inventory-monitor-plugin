from django import forms
from django.utils.translation import gettext as _
from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm, NetBoxModelBulkEditForm
from utilities.forms.fields import ColorField, SlugField, TagFilterField, CommentField
from utilities.forms.rendering import FieldSet

from inventory_monitor.models import AssetType


class AssetTypeForm(NetBoxModelForm):
    slug = SlugField()

    fieldsets = (FieldSet("name", "slug", "color", "description", "tags"),)

    class Meta:
        model = AssetType
        fields = [
            "name",
            "slug",
            "color",
            "description",
            "tags",
        ]


class AssetTypeBulkEditForm(NetBoxModelBulkEditForm):
    name = forms.CharField(
        max_length=AssetType._meta.get_field("name").max_length,
        required=False
    )
    color = ColorField(required=False)
    description = forms.CharField(
        widget=forms.Textarea,
        required=False
    )
    comments = CommentField(required=False)

    model = AssetType
    nullable_fields = ('name', 'color', 'description', 'comments')


class AssetTypeFilterForm(NetBoxModelFilterSetForm):
    model = AssetType
    fieldsets = (
        FieldSet("q", "filter_id", "tag"),
        FieldSet("color", name=_("Attributes")),
    )
    tag = TagFilterField(model)

    color = ColorField(label=_("Color"), required=False)
