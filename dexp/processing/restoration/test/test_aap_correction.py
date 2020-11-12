import numpy
from scipy.ndimage import gaussian_filter
from skimage.data import binary_blobs
from skimage.util import random_noise

from dexp.processing.backends.cupy_backend import CupyBackend
from dexp.processing.backends.numpy_backend import NumpyBackend
from dexp.processing.restoration.aap_correction import axis_aligned_pattern_correction
from dexp.utils.timeit import timeit


def add_patterned_noise(image, n):
    image = image.copy()
    image *= 1 + 0.1 * (numpy.random.rand(n, n) - 0.5)
    image += 0.1 * numpy.random.rand(n, n)
    # image += 0.1*numpy.random.rand(n)[]
    image = random_noise(image, mode="gaussian", var=0.00001, seed=0)
    image = random_noise(image, mode="s&p", amount=0.000001, seed=0)
    return image


def test_aap_correction_numpy():
    backend = NumpyBackend()
    _test_aap_correction(backend)


def test_aap_correction_cupy():
    try:
        backend = CupyBackend()
        _test_aap_correction(backend)
    except (ModuleNotFoundError, NotImplementedError):
        print("Cupy module not found! ignored!")


def _test_aap_correction(backend, length_xy=128):
    xp = backend.get_xp_module()

    image = binary_blobs(length=length_xy, seed=1, n_dim=3, volume_fraction=0.01)
    image = image.astype(numpy.float32)
    image = gaussian_filter(image, sigma=4)
    noisy = add_patterned_noise(image, length_xy)

    with timeit("generate data"):
        corrected = axis_aligned_pattern_correction(backend, noisy, sigma=0)
        corrected = backend.to_numpy(corrected)

    assert corrected is not noisy
    assert corrected.shape == noisy.shape
    assert corrected.dtype == noisy.dtype

    average_error = numpy.mean(numpy.absolute(image - corrected))
    print(f"average_error = {average_error}")
    assert average_error < 0.007

    # import napari
    # with napari.gui_qt():
    #     viewer = napari.Viewer()
    #     viewer.add_image(image, name='image')
    #     viewer.add_image(noisy, name='noisy')
    #     viewer.add_image(corrected, name='corrected')