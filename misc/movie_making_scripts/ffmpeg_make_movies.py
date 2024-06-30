# https://stackoverflow.com/questions/42438380/ffmpeg-in-python-script
import os

### rather than running a couple hundred thousand bash lines, OR trying to
### figure out ffmpy, we can just use os to run commands in a python script

path_in = '/mnt/research/turbulence/hayeskea_vsf/ffmpeg_test/'
path_out = '/mnt/research/turbulence/hayeskea_vsf/movies_new/'

header = ['NGC4472_density_slice_x_']
footer = ['400_kpc']

in_format = '.png'
out_format = '.mp4'

for i in header:
    for j in footer:

        frames = path_in + i + 'output_*_' + j + in_format

        movie = path_out + i + j + '_test_' + out_format

        os.system("ffmpeg -framerate 10 -pattern_type glob -i '{}' -f mp4 -vcodec h264 -b:v 8M -r 10 {}".format(frames, movie))
