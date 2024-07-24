from schemas.client_schema import ClientOutputSchema
from schemas.form_schema import FormOutputSchema


def generate_filename(form_data: FormOutputSchema, client: ClientOutputSchema):
    return f"{form_data.id}_{client.full_name}.pdf"