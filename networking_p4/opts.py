import itertools

from networking_p4.extensions import p4


def list_quota_opts():
    return [
        ('quotas',
         itertools.chain(
             p4.p4_quota_opts)
         ),
    ]

