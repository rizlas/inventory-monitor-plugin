def invmon_file_upload(instance, filename):
    """
    Return a path for uploading invom file attchments.
    """
    path = 'invmon-attachments/'

    # Rename the file to the provided name, if any. Attempt to preserve the file extension.
    extension = filename.rsplit('.')[-1].lower()
    if instance.name:
        filename = '.'.join([instance.name, extension])
    elif instance.name:
        filename = instance.name

    return '{}{}_{}_{}'.format(path, instance.content_type.name, instance.object_id, filename)
