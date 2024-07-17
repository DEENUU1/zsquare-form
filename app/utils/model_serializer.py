from datetime import datetime


def serialize_model(instance):
    """
    Helper function to serialize SQLAlchemy model instance, excluding
    internal state and any non-serializable attributes.
    """
    instance_dict = instance.__dict__.copy()
    if '_sa_instance_state' in instance_dict:
        del instance_dict['_sa_instance_state']

    for key, value in instance_dict.items():
        if isinstance(value, datetime):
            instance_dict[key] = str(value)[:10]

    return instance_dict
