import pytest
from skimage.data import binary_blobs
from skimage.filters import gaussian
from skimage.util import random_noise

from dexp.processing.backends.backend import Backend
from dexp.processing.backends.cupy_backend import CupyBackend
from dexp.processing.backends.numpy_backend import NumpyBackend
from dexp.processing.equalise.equalise_intensity import equalise_intensity
from dexp.utils.timeit import timeit


def demo_equalise_intensity_numpy():
    backend = NumpyBackend()
    _equalise_intensity(backend)


def demo_equalise_intensity_cupy():
    try:
        backend = CupyBackend()
        _equalise_intensity(backend)
    except ModuleNotFoundError:
        print("Cupy module not found! Test passes nevertheless!")


def _equalise_intensity(backend: Backend, length=512):
    with timeit("generate demo dataset"):
        ratio_gt = 1.77

        image_1 = 300 * binary_blobs(length=length, n_dim=3, blob_size_fraction=0.04, volume_fraction=0.01).astype('f4')
        image_1 = gaussian(image_1, sigma=1)
        image_2 = image_1.copy() * ratio_gt

        image_1 = 95 + random_noise(image_1, mode='gaussian', var=0.2, clip=False)
        image_2 = 95 + random_noise(image_2, mode='gaussian', var=0.2, clip=False)

    org_image_1, org_image_2 = image_1.copy(), image_2.copy()
    with timeit("equalise intensity"):
        equ_image_1, equ_image_2, corr_ratio = equalise_intensity(backend, image_1, image_2)

    corr_ratio = backend.to_numpy(corr_ratio)

    print(f" Ratio:{1 / corr_ratio}")

    assert ratio_gt == pytest.approx(1 / corr_ratio, 1e-2)

    from napari import Viewer
    import napari
    with napari.gui_qt():
        def _c(array):
            return backend.to_numpy(array)

        viewer = Viewer()
        viewer.add_image(_c(image_1), name='image_1')
        viewer.add_image(_c(image_2), name='image_2')
        viewer.add_image(_c(org_image_1), name='org_image_1', contrast_limits=(0, 700))
        viewer.add_image(_c(org_image_2), name='org_image_2', contrast_limits=(0, 700))
        viewer.add_image(_c(equ_image_1), name='equ_image_1', contrast_limits=(0, 700))
        viewer.add_image(_c(equ_image_2), name='equ_image_2', contrast_limits=(0, 700))


demo_equalise_intensity_numpy()
demo_equalise_intensity_cupy()