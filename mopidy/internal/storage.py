import gzip
import json
import logging
import tempfile

from mopidy import models
from mopidy.compat import pathlib
from mopidy.internal import encoding

logger = logging.getLogger(__name__)


def load(path):
    """
    Deserialize data from file.

    :param path: full path to import file
    :type path: pathlib.Path
    :return: deserialized data
    :rtype: dict
    """

    # TODO: raise an exception in case of error?
    if not path.is_file():
        logger.info("File does not exist: %s", path)
        return {}
    try:
        with gzip.open(str(path), "rb") as fp:
            return json.load(fp, object_hook=models.model_json_decoder)
    except (IOError, ValueError) as error:
        logger.warning("Loading JSON failed: %s", encoding.locale_decode(error))
        return {}


def dump(path, data):
    """
    Serialize data to file.

    :param path: full path to export file
    :type path: pathlib.Path
    :param data: dictionary containing data to save
    :type data: dict
    """

    # TODO: cleanup directory/basename.* files.
    tmp = tempfile.NamedTemporaryFile(
        prefix=path.name + ".", dir=str(path.parent), delete=False
    )
    tmp_path = pathlib.Path(tmp.name)

    try:
        data_string = json.dumps(
            data, cls=models.ModelJSONEncoder, indent=2, separators=(",", ": ")
        )
        with gzip.GzipFile(fileobj=tmp, mode="wb") as fp:
            fp.write(data_string.encode("utf-8"))
        tmp_path.rename(path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()
