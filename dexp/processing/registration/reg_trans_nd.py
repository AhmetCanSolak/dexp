import math

import numpy

from dexp.processing.backends.backend import Backend
from dexp.processing.registration.model.translation_registration_model import TranslationRegistrationModel


def register_translation_nd(backend: Backend,
                            image_a,
                            image_b,
                            max_range_ratio: float = 0.5,
                            fine_window_radius: int = 4,
                            decimate: int = 16,
                            quantile: float = 0.999,
                            internal_dtype=numpy.float32,
                            log: bool = False) -> TranslationRegistrationModel:
    """
    Registers two nD images using just a translation-only model.
    This uses a full nD robust phase correlation based approach.


    Parameters
    ----------
    backend : backend for computation
    image_a : First image to register
    image_b : Second image to register
    max_range_ratio : backend for computation
    fine_window_radius : Window of which to refine translation estimate
    decimate : How much to decimate when computing floor level
    quantile : Quantile to use for robust min and max
    internal_dtype : internal dtype for computation
    log : output logging information, or not.

    Returns
    -------
    Translation-only registration model

    """
    image_a = backend.to_backend(image_a)
    image_b = backend.to_backend(image_b)

    xp = backend.get_xp_module()
    sp = backend.get_sp_module()

    # We compute the phase correlation:
    raw_correlation = _phase_correlation(backend, image_a, image_b, internal_dtype)
    correlation = raw_correlation

    # max range is computed from max_range_ratio:
    max_range = 8 + int(max_range_ratio * numpy.min(correlation.shape))

    # We estimate the noise floor of the correlation:
    max_ranges = tuple(max(0, min(max_range, s - 2 * max_range)) for s in correlation.shape)
    if log:
        print(f"max_ranges={max_ranges}")
    empty_region = correlation[tuple(slice(r, s - r) for r, s in zip(max_ranges, correlation.shape))].copy()
    noise_floor_level = xp.percentile(empty_region.ravel()[::decimate].astype(numpy.float32), q=100 * quantile)
    if log:
        print(f"noise_floor_level={noise_floor_level}")

    # we use that floor to clip anything below:
    correlation = correlation.clip(noise_floor_level, math.inf) - noise_floor_level

    # We roll the array and crop it to restrict ourself to the search region:
    correlation = xp.roll(correlation, shift=max_range, axis=tuple(range(image_a.ndim)))
    correlation = correlation[(slice(0, 2 * max_range),) * image_a.ndim]

    # denoise cropped correlation image:
    # correlation = gaussian_filter(correlation, sigma=sigma, mode='wrap')

    # We use the max as quickly computed proxy for the real center:
    rough_shift = xp.unravel_index(
        xp.argmax(correlation, axis=None), correlation.shape
    )

    if log:
        print(f"rough_shift= {rough_shift}")

    # We crop further to facilitate center-of-mass estimation:
    cropped_correlation = correlation[
        tuple(
            slice(max(0, int(s) - fine_window_radius), min(d, int(s) + fine_window_radius))
            for s, d in zip(rough_shift, correlation.shape)
        )
    ]
    if log:
        print(f"cropped_correlation.shape = {cropped_correlation.shape}")


    # We compute the signed rough shift
    signed_rough_shift = xp.array(rough_shift) - max_range
    signed_rough_shift = backend.to_numpy(signed_rough_shift)
    if log:
        print(f"signed_rough_shift= {signed_rough_shift}")
    cropped_correlation = backend.to_numpy(cropped_correlation)

    # We compute the center of mass:
    # We take the square to squash small values far from the maximum that are likely noisy...
    signed_com_shift = (
            xp.array(_center_of_mass(backend, cropped_correlation ** 2))
            - fine_window_radius
    )
    signed_com_shift = backend.to_numpy(signed_com_shift)
    if log:
        print(f"signed_com_shift= {signed_com_shift}")

    # The final shift is the sum of the rough sight plus the fine center of mass shift:
    shift = list(signed_rough_shift + signed_com_shift)

    # print(f"shift = {shift}")
    # from napari import gui_qt, Viewer
    # with gui_qt():
    #     def _c(array):
    #         return backend.to_numpy(array)
    #     viewer = Viewer()
    #     viewer.add_image(_c(image_a), name='image_a')
    #     viewer.add_image(_c(image_b), name='image_b')
    #     viewer.add_image(_c(raw_correlation), name='raw_correlation')
    #     viewer.add_image(_c(correlation), name='correlation')
    #     viewer.add_image(_c(cropped_correlation), name='cropped_correlation')
    #     viewer.grid_view(3,3,1)

    #if log:


    return TranslationRegistrationModel(shift_vector=shift, error=0)


def _center_of_mass(backend: Backend, image):
    image = backend.to_backend(image)

    xp = backend.get_xp_module()
    sp = backend.get_sp_module()

    try:
        return sp.ndimage.center_of_mass(image)
    except AttributeError:
        # Workaround for the lack of implementation of center_of_mass in cupy
        # TODO: remove this code path once center_of_mass is implemented in cupy!

        normalizer = xp.sum(image)

        if abs(normalizer) > 0:
            grids = numpy.ogrid[[slice(0, i) for i in image.shape]]
            grids = list([backend.to_backend(grid) for grid in grids])

            results = list([xp.sum(image * grids[dir].astype(float)) / normalizer
                            for dir in range(image.ndim)])

            return tuple(float(f) for f in results)
        else:
            return tuple(s/2 for s in image.shape)




def _normalised_projection(backend: Backend, image, axis, gamma=3):
    xp = backend.get_xp_module(image)
    projection = xp.max(image, axis=axis)
    min_value = xp.min(projection)
    max_value = xp.max(projection)
    range_value = (max_value - min_value)
    if abs(range_value)>0:
        normalised_image = ((projection - min_value) / range_value) ** gamma
    else:
        normalised_image = 0
    return normalised_image


def _phase_correlation(backend: Backend, image_a, image_b, internal_dtype=numpy.float32):
    xp = backend.get_xp_module(image_a)
    G_a = xp.fft.fftn(image_a).astype(numpy.complex64, copy=False)
    G_b = xp.fft.fftn(image_b).astype(numpy.complex64, copy=False)
    conj_b = xp.conj(G_b)
    R = G_a * conj_b
    R /= xp.absolute(R)
    r = xp.fft.ifftn(R).real.astype(internal_dtype, copy=False)
    return r
