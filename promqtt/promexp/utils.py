'''Utility functions for the prometheus exporter'''

def _get_label_string(labels):
    '''Convert a dictionary of labels to a unique label string'''

    labelstr = ','.join(
        [f'{k}="{labels[k]}"' for k in sorted(labels.keys())]
    )

    return labelstr
