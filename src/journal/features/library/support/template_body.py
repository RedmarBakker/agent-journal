from journal.features.library.support.portable_body import PortableBody
from journal.models.template import Template

TEMPLATE_FIELDS = ("title", "targets", "purpose", "brief", "parts", "commands")


class TemplateBody:
    """A template as the library carries it: the fields named here alone, never its number or stamps; and back into a template of its own."""

    @staticmethod
    def text(template: Template) -> str:
        return PortableBody.text({name: list(value) if isinstance(value := getattr(template, name), tuple) else value for name in TEMPLATE_FIELDS})

    @staticmethod
    def template(text: str) -> Template:
        fields = PortableBody.fields(text)
        return Template(**{name: tuple(fields[name]) if isinstance(fields[name], list) else fields[name] for name in TEMPLATE_FIELDS})
