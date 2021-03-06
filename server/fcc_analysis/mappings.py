FIELDS = {
    'addressentity': {
        'properties': {
            'zip_code': {'type': 'keyword'},
            'internationaladdressentity': {
                'properties': {
                    'addresstext': {
                        'type': 'text',
                        'fields': {
                            'keyword': {
                                'ignore_above': 256,
                                'type': 'keyword'
                            }
                        }
                    }
                }
            },
            'address_line_1': {'type': 'text'},
            'city': {'type': 'text'},
            'address_line_2': {
                'type': 'text',
                'fields': {
                    'keyword': {'ignore_above': 256, 'type': 'keyword'}
                }
            },
            'zip4': {'type': 'keyword'},
            'state': {'type': 'keyword'}
        }
    },
    'browser' : {
        'type' : 'text',
        'fields' : {
          'keyword' : {
            'type' : 'keyword',
            'ignore_above' : 256
          }
        }
    },
    'date_disseminated': {'type': 'date', 'format': 'strict_date_optional_time'},
    'date_received': {'type': 'date', 'format': 'strict_date_optional_time'},
    'confirmation_number': {'type': 'keyword'},
    'contact_email': {
        'type': 'text',
        'fields': {
            'raw': {'type': 'keyword'}
        }
    },
    'emailConfirmation': {
        'type': 'text',
        'fields': {'keyword': {'ignore_above': 256, 'type': 'keyword'}}
    },
    'express_comment': {'type': 'integer'},
    'filers': {
        'properties': {
            'name': {'type': 'text'}
        }
    },
    'id_submission': {'type': 'keyword'},
    'internationaladdressentity': {
        'properties': {
            'addresstext': {
                'type': 'text',
                'fields': {
                    'keyword': {
                        'ignore_above': 256,
                        'type': 'keyword'
                    }
                }
            }
        }
    },
    'proceedings': {
        'properties': {
            '_index': {'type': 'keyword'}
        }
    },
    'text_data': {
        'analyzer': 'standard',
        'type': 'text',
        'fields': {
            'english': {'analyzer': 'english', 'type': 'text'}
        },
        'fielddata': True
    },
    # added by analyze
    'analysis': {
        'properties': {
            'source': {'type': 'keyword'},
            'capsemail': {'type': 'boolean'},
            'proceedings_keys': {'type': 'keyword'},
            'ingestion_method': {'type': 'keyword'},
            'titleii': {'type': 'boolean'},
            'fingerprint': {'type': 'keyword'},
            'onsite': {'type': 'boolean'},
            'fulladdress': {'type': 'boolean'},
            'breached': {'type': 'boolean'},
            'more_like_this': {
                'properties': {
                    # add 'fielddata': True to enable significant terms
                    # but it takes a lot of memory and is not recommended for large indexes
                    'src_doc_id': {'type': 'keyword'},
                    'is_source': {'type': 'boolean'},
                    'matches': {'type': 'integer'},
                    'too_short': {'type': 'boolean'}
                }
            }
        }
    },
}

MAPPINGS = {
    'mappings': {
        'filing': {
            'properties': FIELDS
        }
    }
}
