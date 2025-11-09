from django.contrib import admin
from .models import Area, Subarea, Plano
from django import forms


class SubareaInline(admin.TabularInline):
    model = Subarea
    extra = 1


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "abrev")
    search_fields = ("nombre", "abrev")
    inlines = [SubareaInline]


# @admin.register(Subarea)
# class SubareaAdmin(admin.ModelAdmin):
#     list_display = ("nombre", "abrev", "area")
#     list_filter = ("area",)
#     search_fields = ("nombre", "abrev")


class PlanoForm(forms.ModelForm):
    area = forms.ModelChoiceField(
        queryset=Area.objects.all(), required=False, label="Área"
    )

    class Meta:
        model = Plano
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Si estás editando, precarga el área y acota subáreas
        if self.instance.pk:
            self.fields["area"].initial = self.instance.subarea.area
            self.fields["subarea"].queryset = Subarea.objects.filter(
                area=self.instance.subarea.area)
        else:
            self.fields["subarea"].queryset = Subarea.objects.none()

        # Si el usuario ya seleccionó un área en el POST, filtra subáreas
        area_id = (self.data.get("area") or self.initial.get("area"))
        try:
            if area_id:
                self.fields["subarea"].queryset = Subarea.objects.filter(
                    area_id=int(area_id))
        except (TypeError, ValueError):
            pass


@admin.register(Plano)
class PlanoAdmin(admin.ModelAdmin):
    form = PlanoForm
    list_display = ("codigo", "titulo", "subarea",
                    "version", "subido_por", "fecha_subida")
    list_filter = ("subarea__area", "subarea", "version")
    search_fields = ("codigo", "titulo", "descripcion")
    readonly_fields = ("codigo", "fecha_subida")
    autocomplete_fields = ("subido_por",)
    fields = ("titulo", "descripcion", "subido_por", "area",
              "subarea", "version", "codigo", "fecha_subida")


try:
    admin.site.unregister(Subarea)
except admin.sites.NotRegistered:
    pass
