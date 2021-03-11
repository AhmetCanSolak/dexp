import click
from arbol.arbol import aprint

from dexp.video.blend import blend_color_image_sequences


@click.command()
@click.argument('input_paths', nargs=-1)
@click.option('--output_path', '-o', type=str, default=None, help='Output folder for blended frames.')
@click.option('--modes', '-m', type=str, default='max',
              help='Either one for all images, or one per image in the form of a sequence. Blending modes are: mean, add, satadd, max, alpha. In the add mode the values are clipped. For alpha-blending, we assume that RGB values are not ‘alpha-premultiplied’.',
              show_default=True)
@click.option('--alphas', '-a', type=str, default=None,
              help='List of alpha values for each input image',
              show_default=True)
@click.option('--scales', '-s', type=str, default=None,
              help='List of scales ‘s’ for each input image, starting with the second one (first image has always a scale of 1). Scaled images must be of same dimension or smaller than the first images. ',
              show_default=True)
@click.option('--translations', '-t', type=str, default=None, help='List of translations ‘x0,y0*x1,y1;...’ for each input image, starting with the second one (first image is always at 0,0). ',
              show_default=True)
@click.option('--borderwidth', '-bw', type=int, default=0, help='Border width added to insets. ', show_default=True)
@click.option('--bordercolor', '-bc', type=str, default='1,1,1,1', help='Border color in RGBA format. For example: 1,1,1,1 is white.', show_default=True)
@click.option('--borderover', '-bo', is_flag=True, help='Border is overlayed on top of inset images, without increasing their size. ', show_default=True)
@click.option('--overwrite', '-w', is_flag=True, help='Force overwrite of output images.', show_default=True)
@click.option('--workers', '-k', type=int, default=-1, help='Number of worker threads to spawn, set to -1 for maximum number of workers', show_default=True)  #
@click.option('--workersbackend', '-wkb', type=str, default='threading', help='What backend to spawn workers with, can be ‘loky’ (multi-process) or ‘threading’ (multi-thread) ', show_default=True)  #
def blend(input_paths,
          output_path,
          modes,
          alphas,
          scales,
          translations,
          borderwidth,
          bordercolor,
          borderover,
          overwrite,
          workers,
          workersbackend):
    number_of_inputs = len(input_paths)

    if output_path is None:
        output_path = input_paths[0] + '_blend'
    elif output_path.startswith('_'):
        output_path = input_paths[0] + output_path

    if ',' in modes:
        modes = tuple(mode.strip() for mode in modes.split(','))
    else:
        modes = (modes,) * number_of_inputs

    if alphas is None:
        alphas = (1.0,) * number_of_inputs
    else:
        alphas = tuple(float(alpha) for alpha in alphas.split(','))

    if scales is None:
        scales = (1,) * number_of_inputs
    else:
        scales = tuple(float(scale) for scale in scales.split(','))

    if translations is None:
        translations = ((0, 0),) * number_of_inputs
    else:
        translations = tuple(tuple(float(v) for v in xy.split(',')) for xy in translations.split('*'))

    bordercolor = tuple(float(v) for v in bordercolor.split(','))

    if len(input_paths) <= 1:
        aprint("Blending requires at least two paths!")
        return

    blend_color_image_sequences(input_paths=input_paths,
                                output_path=output_path,
                                modes=modes,
                                alphas=alphas,
                                scales=scales,
                                translations=translations,
                                border_width=borderwidth,
                                border_color=bordercolor,
                                border_over_image=borderover,
                                overwrite=overwrite,
                                workers=workers,
                                workersbackend=workersbackend)
