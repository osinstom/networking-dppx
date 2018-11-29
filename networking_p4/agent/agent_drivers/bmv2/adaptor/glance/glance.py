from keystoneauth1 import loading as ks_loading
from oslo_config import cfg
from glanceclient import Client
from networking_p4.services.common.exceptions import P4ImageNotFound


class GlanceClientWrapper(object):

    def __init__(self):
        # FIXME: Replace group name
        session = ks_loading.load_session_from_conf_options(
            cfg.CONF, group='nova')
        auth = ks_loading.load_auth_from_conf_options(
            cfg.CONF, group='nova')

        self.glance = Client('2', session=session, auth=auth)

    def download_image(self, name):
        image_id = self.get_image_id_by_name(name)
        if image_id:
            data = self.glance.images.data(image_id)
            adapter = ImageReadHandler(data)
            image = adapter.read()
            return image
        else:
            raise P4ImageNotFound()

    def get_image_id_by_name(self, name):
        for image in self.glance.images.list():
            if image['name'] == name:
                return image.id


class ImageReadHandler(object):
    """Read handle for glance images."""

    def __init__(self, glance_read_iter):
        """Initializes the read handle with given parameters.

        :param glance_read_iter: iterator to read data from glance image
        """
        self._glance_read_iter = glance_read_iter.__iter__()

    def read(self):
        """Read an item from the image data iterator.

        The input chunk size is ignored since the client ImageBodyIterator
        uses its own chunk size.
        """
        data = []
        for chunk in self._glance_read_iter:
            data.append(chunk)

        return ''.join(data)
