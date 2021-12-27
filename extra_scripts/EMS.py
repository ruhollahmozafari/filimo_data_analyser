from rest_framework.response import Response


def validation_error(serialized):
    print(serialized.errors)
    return Response(
        {
            'succeeded': False,
            'details': serialized.errors,
            'error_type': 'validation_error'
        },
        status=400
    )


def existence_error(object_name):
    return Response(
        {
            'succeeded': False,
            'details': '{} object does not exist!'.format(object_name),
            'error_type': 'existence_error'
        },
        status=404
    )
